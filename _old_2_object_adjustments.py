import functools
import inspect

from ultralytics.models.fastsam import FastSAM, FastSAMPrompt
import pyqtgraph as pg
import numpy as np
from skimage import io
from skimage.measure import label, regionprops, find_contours
from skimage.transform import resize
from ultralytics.engine.results import Results
from qtpy import QtWidgets, QtCore
from pyqtgraph.parametertree import Parameter, interact, RunOptions

params = Parameter.create(name="Options", type="group")
interact.setOpts(parent=params)


def opts(type: str, **kwargs):
    return dict(type=type, **kwargs)


def register(**kwargs):
    def wrapper(func):
        func.__opts__ = kwargs
        return func

    return wrapper


def get_label_contours(mask):
    """
    ``find_contours` treats pixels in the mask borders as separate contours, so
    add a 1-pixel border to the mask to avoid this issue. Then, subtract 1 from
    the coordinates of the contours to align with the original mask
    """
    mask = np.pad(mask, 1, mode="constant", constant_values=0)
    contours = find_contours(mask, 0)
    for contour in contours:
        contour -= 1
    return contours


class ObjectsScatter(pg.ScatterPlotItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mask_xywh = None

    def set_label_mask(self, mask):
        symbols = []
        locs = []
        brushes = []
        for region in regionprops(mask):
            nan_contours = []
            for contour in get_label_contours(region.image):
                nan_contours.append(contour)
                nan_contours.append([np.nan, np.nan])
            rc_coords = np.vstack(nan_contours[:-1]) + region.bbox[:2]
            xy_coords = rc_coords[:, ::-1]
            # Join all regions and separate by NaN
            symbol, pos = self.symbol_from_vertices(xy_coords)
            locs.append(pos)
            symbols.append(symbol)
            color = pg.mkColor(region.label)
            color.setAlphaF(0.5)
            brushes.append(color)
        self.setData(
            pos=np.vstack(locs),
            symbol=symbols,
            size=1,
            pxMode=False,
            brush=brushes,
            pen="#fff",
        )
        coords_xy = np.c_[mask.nonzero()][:, ::-1]
        self.mask_xywh = np.array([coords_xy.min(0), coords_xy.ptp(0) + 1]).flatten()

    @staticmethod
    def symbol_from_vertices(vertices: np.ndarray):
        if not len(vertices):
            symbol_pos = np.array([[0, 0]])
        else:
            symbol_pos = np.nanmin(vertices, 0, keepdims=True)
        vertices = vertices - symbol_pos + 0.5
        if not len(vertices):
            isfinite = "all"
        else:
            isfinite = np.isfinite(vertices).all(1)
        return pg.arrayToQPath(*vertices.T, connect=isfinite), symbol_pos

    def boundingRect(self):
        if self.mask_xywh is None:
            return super().boundingRect()
        return pg.QtCore.QRectF(*self.mask_xywh)


class SAMCanvas(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_item = pg.ImageItem(axisOrder="row-major")
        self.mask_item = pg.ImageItem(axisOrder="row-major")
        self.scatter_item = ObjectsScatter()
        for item in [self.image_item, self.mask_item, self.scatter_item]:
            self.addItem(item)
        self.setAspectLocked(True)
        self.invertY()

        for name, func in inspect.getmembers(
            self, predicate=lambda obj: hasattr(obj, "__opts__")
        ):
            interact(func, **func.__opts__)
        self.set_styles()

    @register(
        path=opts("file", nameFilter="Images (*.png *.jpg *.jpeg *.bmp " "*.tiff)"),
        runOptions=[RunOptions.ON_CHANGED, RunOptions.ON_ACTION],
    )
    def load_local_image(self, path="flamingos.jpg"):
        self.image_item.setImage(io.imread(path))

    @register()
    def load_random_image(self):
        self.image_item.setImage(io.imread("https://source.unsplash.com/random"))

    @register()
    def run_predictor(self):
        image = self.image_item.image
        if image is None:
            return
        results: Results = model.predict(image, verbose=False)
        assert len(results) == 1, "FastSAM only supports single-image predictions"
        if results[0].masks is None:
            return
        combined = results[0].masks.data.argmax(axis=0)
        foreground = combined.detach().cpu().numpy().astype(int)
        label_mask = resize(foreground, image.shape[:2], order=0, anti_aliasing=False)
        self.scatter_item.set_label_mask(label_mask)

    @register(
        colormap=opts("list", values=["viridis", "plasma", "inferno", "magma"]),
        opacity=opts("slider", limits=[0, 1], step=0.05),
        runOptions=[RunOptions.ON_CHANGED, RunOptions.ON_ACTION],
    )
    def set_styles(self, colormap="viridis", opacity=0.5):
        colormap = pg.colormap.get(colormap)
        self.mask_item.setOpts(colorMap=colormap, opacity=opacity)


def make_window(children: list[QtWidgets.QWidget] = None):
    window = QtWidgets.QMainWindow(None)
    layout = QtWidgets.QHBoxLayout()
    central = QtWidgets.QWidget(None)
    central.setLayout(layout)
    window.setCentralWidget(central)
    splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal, None)
    for child in children:
        splitter.addWidget(child)
    layout.addWidget(splitter)
    return window


def make_tree():
    tree = pg.parametertree.ParameterTree()
    tree.setParameters(params, showTop=False)
    return tree


pg.mkQApp()
model = FastSAM()
canvas = SAMCanvas()
window = make_window([canvas, make_tree()])
window.show()
pg.exec()

import inspect
import operator

import numpy as np
import pyqtgraph as pg
from pyqtgraph.functions import arrayToQPath
from pyqtgraph.parametertree import Parameter, RunOptions, interact
from qtpy import QtCore, QtWidgets
from scipy.ndimage import binary_fill_holes
from skimage import io
from skimage.measure import find_contours, label, regionprops
from skimage.morphology import flood
from skimage.transform import resize
from ultralytics.engine.results import Results
from ultralytics.models.fastsam import FastSAM, FastSAMPrompt

params = Parameter.create(
    name="Options",
    type="group",
    children=[dict(name="Selection Options", type="group")],
)
selection_parent = params.children()[0]


def opts(type: str, **kwargs):
    return dict(type=type, **kwargs)


def register(**kwargs):
    def wrapper(func):
        func.__opts__ = kwargs
        return func

    return wrapper


class ClickableImage(pg.ImageItem):
    sigClicked = QtCore.Signal(object, object)  # Image, (x, y) coordinate

    def mouseClickEvent(self, ev):
        if ev.button() == QtCore.Qt.MouseButton.LeftButton:
            self.sigClicked.emit(self.image, tuple(int(p) for p in ev.pos()))


class SelectedRegion(QtWidgets.QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.pen = pg.mkPen("w")
        self.brush = pg.mkBrush("r")
        self.mask = np.zeros((0, 0), dtype=bool)
        self.path = None
        self._bounding_rect = QtCore.QRectF()

    def paint(self, p, *args):
        if self.mask is None or self.path is None:
            return
        p.setPen(self.pen)
        p.setBrush(self.brush)
        p.drawPath(self.path)

    def update_mask(self, mask, operation):
        self.prepareGeometryChange()
        self.mask = operation(self.mask, mask)
        xy_coords = self.get_contours_as_xy_coords()
        self.path = arrayToQPath(*xy_coords.T, connect="finite")
        finite = xy_coords[np.isfinite(xy_coords).all(axis=1)]
        if len(finite):
            self._bounding_rect = QtCore.QRectF(*finite.min(0), *finite.ptp(0))
        else:
            self._bounding_rect = QtCore.QRectF()
        self.update()

    def reset_mask(self, mask):
        self.update_mask(mask, lambda a, b: b)

    def add_mask(self, mask):
        self.update_mask(mask, operator.or_)

    def subtract_mask(self, mask):
        self.update_mask(~mask, operator.and_)

    def get_contours_as_xy_coords(self):
        """
        ``find_contours` treats pixels in the mask borders as separate contours, so
        add a 1-pixel border to the mask to avoid this issue. Then, subtract 1 from
        the coordinates of the contours to align with the original mask
        """
        mask = np.pad(self.mask, 1, mode="constant", constant_values=0)
        contours = find_contours(mask, 0)
        if not len(contours):
            return np.zeros((0, 2))
        out_coords = []
        for contour in contours:
            contour -= 1
            out_coords.append(contour)
            out_coords.append([np.nan, np.nan])
        # skimage returns row-col, we want x-y
        return np.vstack(out_coords[:-1])[:, ::-1]

    def boundingRect(self):
        return self._bounding_rect


class SAMCanvas(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_item = pg.ImageItem(axisOrder="row-major")
        self.mask_item = ClickableImage(axisOrder="row-major")
        self.selected_region = SelectedRegion()
        for item in [self.image_item, self.mask_item, self.selected_region]:
            self.addItem(item)
        self.setAspectLocked(True)
        self.invertY()

        for name, func in type(self).__dict__.items():
            if hasattr(func, "__opts__"):
                interact(getattr(self, name), **func.__opts__, parent=params)

        self.set_styles()
        self.mask_item.sigClicked.connect(self.on_image_click)

    def on_image_click(self, image: np.ndarray, pos: tuple[int, int]):
        pos_rc = np.array(pos[::-1])
        if (
            self.image_item.image is None
            or (pos_rc < 0).any()
            or (pos_rc >= image.shape[:2]).any()
        ):
            return
        mask = flood(image, pos[::-1])
        self.selected_region.add_mask(mask)

    def reset_image(self, image):
        self.image_item.setImage(image)
        self.run_predictor()
        self.plotItem.getViewBox().autoRange()

    @register(
        path=opts("file", nameFilter="Images (*.png *.jpg *.jpeg *.bmp " "*.tiff)"),
        runOptions=[RunOptions.ON_CHANGED, RunOptions.ON_ACTION],
    )
    def load_local_image(self, path="flamingos.jpg"):
        self.reset_image(io.imread(path))

    @register()
    def load_random_image(self):
        self.reset_image(io.imread("https://source.unsplash.com/random"))

    def run_predictor(self):
        image = self.image_item.image
        if image is None:
            return
        results: Results = model.predict(image, verbose=False)
        assert len(results) == 1, "FastSAM only supports single-image predictions"
        if results[0].masks is None:
            self.mask_item.clear()
            return
        combined = results[0].masks.data.argmax(axis=0)
        foreground = combined.detach().cpu().numpy().astype(int)
        # Since regions are selected instead of one-shot, make everything contiguous
        label_mask = resize(foreground, image.shape[:2], order=0, anti_aliasing=False)
        self.mask_item.setImage(label_mask)
        self.selected_region.reset_mask(np.zeros_like(label_mask))

    @register(
        colormap=opts("list", values=sorted(pg.colormap.listMaps())),
        opacity=opts("slider", limits=[0, 1], step=0.05),
        runOptions=[RunOptions.ON_CHANGED, RunOptions.ON_ACTION],
    )
    def set_styles(self, colormap="viridis", opacity=0.5):
        colormap = pg.colormap.get(colormap)
        self.mask_item.setOpts(colorMap=colormap, opacity=opacity)

    @register()
    def fill_holes(self):
        self.selected_region.reset_mask(binary_fill_holes(self.selected_region.mask))

    @register()
    def reset_selection(self):
        self.selected_region.reset_mask(np.zeros_like(self.mask_item.image))


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
canvas.load_local_image()
canvas.run_predictor()
window.show()
pg.exec()

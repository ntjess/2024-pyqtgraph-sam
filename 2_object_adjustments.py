import functools
import inspect

from ultralytics.models.fastsam import FastSAM
import pyqtgraph as pg
from skimage import io
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


class ObjectsScatter(pg.ScatterPlotItem):
    def setLabelMask(self, mask):
        pass


class SAMCanvas(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_item = pg.ImageItem(axisOrder="row-major")
        self.mask_item = pg.ImageItem(axisOrder="row-major")
        self.addItem(self.image_item)
        self.addItem(self.mask_item)
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
        self.mask_item.hide()

    @register()
    def load_random_image(self):
        self.image_item.setImage(io.imread("https://source.unsplash.com/random"))
        self.mask_item.hide()

    @register()
    def run_predictor(self):
        image = self.image_item.image
        if image is None:
            return
        results: Results = model.predict(image, verbose=False)
        if len(results) == 0 or results[0].masks is None:
            self.mask_item.setImage(None)
            return
        combined = results[0].masks.data
        for component in results[1:]:
            combined += component.masks.data
        foreground = combined[0].detach().cpu().numpy()
        self.mask_item.setImage(foreground, rect=self.image_item.boundingRect())
        self.mask_item.show()

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

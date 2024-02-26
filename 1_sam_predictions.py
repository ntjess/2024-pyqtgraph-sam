from ultralytics.models.fastsam import FastSAM
import pyqtgraph as pg
from skimage import io
from ultralytics.engine.results import Results
from qtpy import QtWidgets, QtCore
from pyqtgraph.parametertree import Parameter, interact, RunOptions

params = Parameter.create(name="Options", type="group")
interact.setOpts(parent=params)


@interact.decorate(
    path=dict(type="file", nameFilter="Images (*.png *.jpg *.jpeg *.bmp " "*.tiff)"),
    runOptions=[RunOptions.ON_CHANGED, RunOptions.ON_ACTION],
)
def load_local_image(path="flamingos.jpg"):
    canvas.image_item.setImage(io.imread(path))
    canvas.mask_item.hide()


@interact.decorate()
def load_random_image():
    canvas.image_item.setImage(io.imread("https://source.unsplash.com/random"))
    canvas.mask_item.hide()


@interact.decorate()
def run_predictor():
    image = canvas.image_item.image
    if image is None:
        return
    results: Results = model.predict(image, verbose=False)
    if len(results) == 0 or results[0].masks is None:
        canvas.mask_item.setImage(None)
        return
    combined = results[0].masks.data
    for component in results[1:]:
        combined += component.masks.data
    foreground = combined[0].detach().cpu().numpy()
    canvas.mask_item.setImage(foreground, rect=canvas.image_item.boundingRect())
    canvas.mask_item.show()


@interact.decorate(
    colormap=dict(type="list", values=["viridis", "plasma", "inferno", "magma"]),
    opacity=dict(type="slider", limits=[0, 1], step=0.05),
    runOptions=[RunOptions.ON_CHANGED, RunOptions.ON_ACTION],
)
def set_styles(colormap="viridis", opacity=0.5):
    colormap = pg.colormap.get(colormap)
    canvas.mask_item.setOpts(colorMap=colormap, opacity=opacity)


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


class SAMCanvas(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_item = pg.ImageItem(axisOrder="row-major")
        self.mask_item = pg.ImageItem(axisOrder="row-major")
        self.addItem(self.image_item)
        self.addItem(self.mask_item)
        self.setAspectLocked(True)
        self.invertY()


pg.mkQApp()
model = FastSAM()
canvas = SAMCanvas()
set_styles()
window = make_window([canvas, make_tree()])
window.show()
pg.exec()

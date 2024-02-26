from ultralytics.models.fastsam import FastSAM
import pyqtgraph as pg
from skimage import io
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


@interact.decorate()
def load_random_image():
    canvas.image_item.setImage(io.imread("https://source.unsplash.com/random"))
    canvas.mask_item.setImage(None)


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
window = make_window([canvas, make_tree()])
window.show()
pg.exec()

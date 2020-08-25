from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

# Canvas used by the GraphGui to import a Matplotlib Figure into a PyQt5 GUI
# MplCanvas is referenced in GraphWindow.ui as a promoted class
class MplCanvas(FigureCanvasQTAgg):
  def __init__(self, parent=None, width=5, height=4, dpi=100):
    fig = Figure(figsize=(width, height), dpi=dpi)
    self.axes = fig.add_subplot(111)
    super(MplCanvas, self).__init__(fig)
import numpy as np
import os, sys

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import matplotlib as mpl
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic, QtCore
from scipy import interpolate

from constants.themes import *

# Set matplotlib settings
mpl.rcParams['toolbar'] = 'None' # Comment out to enable to toolbar
plt.rcParams['axes.xmargin'] = 0
plt.style.use('dark_background')

# The window that contains the matplotlib graph and a small toolbar on top
# Takes in the parent window to pass data directly back and forth
# This data includes buttons on the toolbar, and recieving the data to graph
class GraphWindow(QMainWindow):
  def __init__(self, mainWindow, *args, **kwargs):
    super(GraphWindow, self).__init__(*args, **kwargs)

    uic.loadUi(os.path.join(sys.path[0], 'UI/GraphWindow.ui'), self)

    self.setWindowTitle('Live Gold Graph')
    self.setAttribute(Qt.WA_DeleteOnClose)
    self.parentWindow = mainWindow
    self.show()

    self.toolbar = NavigationToolbar2QT(self.canvas, self)

    self.mul = 1
    self.SaveButton.clicked.connect(self.toolbar.save_figure)
    self.EndGame.clicked.connect(self.parentWindow.endGame)
    self.StartGame.clicked.connect(self.parentWindow.startGame)
    self.btn1.clicked.connect(lambda: self.parentWindow.updateTime(1 * self.mul))
    self.btn2.clicked.connect(lambda: self.parentWindow.updateTime(5 * self.mul))
    self.btn3.clicked.connect(lambda: self.parentWindow.updateTime(10 * self.mul))
    self.btn4.clicked.connect(lambda: self.parentWindow.updateTime(30 * self.mul))
    self.minus.toggled.connect(lambda selected: self.changeMul(selected, -1))
    self.plus.toggled.connect(lambda selected: self.changeMul(selected, 1))

    # Setup a timer to trigger the redraw by calling update_plot.
    self.timer = QtCore.QTimer()
    self.timer.setInterval(500)
    self.timer.timeout.connect(self.updatePlot)
    self.timer.start()

  def changeMul(self, selected, newMul):
    if selected:
      self.mul = newMul

  def updateTime(self):
    time = self.parentWindow.gameTime
    self.GameTimeLabel.setText(f'Current Game Time: {time.minute()}:{time.second()}')

  def updatePlot(self):
    self.updateTime()
    # Drop off the first y element, append a new one.
    redList = self.parentWindow.redData
    blueList = self.parentWindow.blueData
    if len(blueList) < 3:
      return

    data = []
    for i, blue in enumerate(blueList):
      # Red is updated first in other thread, so enumerate off of blue
      red = redList[i] 
      red = float(red[:4])
      blue = float(blue[:4])
      diff = (blue - red) * 1000
      data.append(diff)
    
    x = []
    y = []
    time = self.parentWindow.gameTime
    time = time.minute() * 60 + time.second()
    diff = time - len(data)

    if diff >= 0:
      for index, d in enumerate(data):
        x.append(index + diff)
        y.append(d)
    else: # len(data) > time
      for i in range(time):
        x.append(i)
        y.append(data[i - diff])

    if len(x) < 3:
      return
    f = interpolate.interp1d(x, y)

    newx = np.arange(x[0], x[-1], 0.1)
    newy = f(newx)
    
    self.canvas.axes.cla()  # Clear the canvas.
    self.canvas.axes.plot(newx, newy, 'w')

    # Formatting settings
    self.canvas.axes.fill_between(newx, newy, 0, where=newy < 0, color='red')
    self.canvas.axes.fill_between(newx, newy, 0, where=newy > 0, color='blue')
    self.canvas.axes.axhline(y=0, color='r', linestyle='--')
    self.canvas.axes.set_ylabel('gold difference')
    self.canvas.axes.set_title(f'Live Gold Graph: {self.parentWindow.teams[0]} vs {self.parentWindow.teams[1]}')

    if len(x) < 120:
      self.canvas.axes.set_xlabel('game time (sec)')
      self.canvas.axes.xaxis.set_major_locator(ticker.MultipleLocator(base=10))
      self.canvas.axes.xaxis.set_minor_locator(ticker.MultipleLocator(base=1))
    elif len(x) < 1200:
      self.canvas.axes.set_xlabel('game time (min)')
      self.canvas.axes.xaxis.set_major_formatter(ticker.FuncFormatter(self.numfmt))
      self.canvas.axes.xaxis.set_major_locator(ticker.MultipleLocator(base=60))
      self.canvas.axes.xaxis.set_minor_locator(ticker.MultipleLocator(base=10))
    else:
      self.canvas.axes.set_xlabel('game time (min)')
      self.canvas.axes.xaxis.set_major_formatter(ticker.FuncFormatter(self.numfmt))
      self.canvas.axes.xaxis.set_major_locator(ticker.MultipleLocator(base=300))
      self.canvas.axes.xaxis.set_minor_locator(ticker.MultipleLocator(base=60))

    if len(self.parentWindow.blueTeam) < 2:
      blueTeam, redTeam = self.parentWindow.teams
    else:
      blueTeam = self.parentWindow.blueTeam
      redTeam = self.parentWindow.redTeam
    blueLegend = mpatches.Patch(color='blue', label=blueTeam)
    redLegend = mpatches.Patch(color='red', label=redTeam)
    self.canvas.axes.legend(handles=[blueLegend, redLegend])

    
    # Trigger the canvas to update and redraw.
    self.canvas.draw()

  def numfmt(self, x, pos):
    return f'{int(x / 60)}'
  
  def closeEvent(self, *args, **kwargs):
    super(GraphWindow, self).closeEvent(*args, **kwargs)
    print('You just closed the graph window')
    self.parentWindow.ViewGraph.setEnabled(True)

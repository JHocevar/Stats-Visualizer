import time
import sys, os

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QTime, QThread
from PyQt5 import uic

from constants.urls import urls
from constants.themes import *  # Many default themes are defined in the ui file with QT Designer
from GraphWindow import GraphWindow

# The Tab that monitors the live statuses of the lolesports website runs a separate thread
# for the browser. Created 1 sub window to diaplay the graph
class LiveTab(QMainWindow):
  def __init__(self, *args, **kwargs):
    super(LiveTab, self).__init__(*args, **kwargs)
    uic.loadUi(os.path.join(sys.path[0], 'UI/MainWindow.ui'), self)

    # self.ViewGraph.setEnabled(False) # Enabled when there is enough data
    self.setFocus()
    self.gameTime = QTime(0, 0, 0)
    
    self.redData = list()
    self.blueData = list()

    self.StartGame.clicked.connect(self.startGame)
    self.ViewGraph.clicked.connect(self.showGraph)

    self.badStyle = f'background:{badColor}; padding: 5px;'
    self.goodStyle = f'background:{highlightColor}; padding: 5px;'

    # Status monitors for website statuses, None means 'Loading...'
    self.streamUp = None
    self.teams = None
    self.statsUp = None

    self.graphWindow = None # Defined early so we have a reference if never created
    self.gameOver = False # Stop data from being collected
    self.accurateSides = None # Keeps track if teams have swapped sides during a series

    # Create and run the selenium browser to gather data every second about the status and stats
    self.browserThread = BrowserThread(self)
    self.browserThread.start()

  def setStreamStatus(self, status):
    if self.streamUp == status:
      return
    self.streamUp = status
    if status:
      self.StreamStatusLabel.setText('LIVE')
      self.StreamStatusLabel.setStyleSheet(self.goodStyle)
    else:
      self.StreamStatusLabel.setText('Not Available')
      self.StreamStatusLabel.setStyleSheet(self.badStyle)

  def setTeams(self, teamList, blueTeam=None, redTeam=None):
    self.blueTeam = blueTeam
    self.redTeam = redTeam
    if self.teams == teamList:
      return
    self.teams = teamList
    if len(teamList) > 0:
      self.GameStatusLabel.setText(f'{teamList[0]} vs {teamList[1]}')
      self.GameStatusLabel.setStyleSheet(self.goodStyle)
    else:
      self.GameStatusLabel.setText('No Games Available')
      self.GameStatusLabel.setStyleSheet(self.badStyle)
    self.teams = teamList

  def setDataShown(self, dataShown):
    if dataShown is self.statsUp:
      return

    self.statsUp = dataShown
    if dataShown:
      self.StatsStatusLabel.setText('Stats Recording')
      self.StatsStatusLabel.setStyleSheet(self.goodStyle)
    else:
      self.StatsStatusLabel.setText('No Stats Available')
      self.StatsStatusLabel.setStyleSheet(self.badStyle)
    self.dataShown = dataShown

  def addData(self, red, blue):
    # Add data and increase the game clock unless the game is over
    if self.gameOver:
      return
    self.redData.append(red)
    self.blueData.append(blue)
    self.updateTime(1)

    if len(self.blueData) > 3:
      self.ViewGraph.setEnabled(True)
  
  def showStats(self, x):
    print(f'showing stats: {x}')
  
  def showGraph(self):
    print('showing graph')
    self.graphWindow = GraphWindow(self)
    self.graphWindow.show()
    self.ViewGraph.setEnabled(False)

  def saveGraph(self):
    print('saving graph')

  def updateTime(self, changeAmt=0):
    self.gameTime = self.gameTime.addSecs(changeAmt)

  def endGame(self):
    # Prevent data from being colleted
    self.gameOver = True
    self.StartGame.setEnabled(True)

  def startGame(self):
    # Clears the data and allows data to be collected again
    self.gameOver = False
    self.StartGame.setEnabled(False)
    self.redData = list()
    self.blueData = list()

  def closeEvent(self, *args, **kwargs):
    super(LiveTab, self).closeEvent(*args, **kwargs)
    try:
      self.graphWindow.close()
    except Exception:
      pass # The window failed to close because it was already closed
    self.browserThread.closeBrowser()
    self.browserThread.quit()

# A separate thread to run the browser and monitor the status of the website
# Runs 1 time a second and checks all statuses and retireves any data available
class BrowserThread(QThread):
  def __init__(self, gui, *args, **kwargs):
    super(BrowserThread, self).__init__(*args, **kwargs)
     # Selenium browser options
    options = Options()
    options.add_argument("--headless")
    options.add_argument('--log-level=3')
    self.browser = webdriver.Chrome(options=options)
    self.gui = gui

  def run(self):
    gui = self.gui
    url = urls['LCS']

    self.browser.get(url)

    time.sleep(3)

    startTime = time.time()

    while True:
      time.sleep(1 - ((time.time() - startTime) % 1))

      # Check if we were redirected from the stream -- There is not a stream live
      if url == self.browser.current_url:
        gui.setStreamStatus(True)
      else:
        gui.setStreamStatus(False)
        gui.setTeams([]) # There cannot be any other information available
        gui.setDataShown(False)
        continue

      # Try to find the teams currently playing
      teamElements = self.browser.find_elements_by_class_name('tricode')
      players = self.browser.find_elements_by_class_name('name')
      if len(teamElements) < 2:
        gui.setTeams([])
      else:
        if len(players) > 2:
          blueTeam = players[0].text.split()[0]
          redTeam = players[6].text.split()[0]
        else:
          blueTeam = ''
          redTeam = ''
        teams = []
        teams.append(teamElements[0].text)
        teams.append(teamElements[1].text)
        gui.setTeams(teams, blueTeam, redTeam) # passing in 2 sets of teams makes sure side swaps still work
      

      # Try and find stats from the stats menu
      redTotals = self.browser.find_elements_by_class_name('red-team')
      blueTotals = self.browser.find_elements_by_class_name('blue-team')
      if len(blueTotals) < 2:
        gui.setDataShown(False)
      else:
        gui.setDataShown(True)
        redGold = redTotals[2]
        blueGold = blueTotals[2]
        gui.addData(redGold.text, blueGold.text)

  def closeBrowser(self):
    self.browser.close()
    self.browser.quit()
  
if __name__ == '__main__':
  app = QApplication(sys.argv)
  window = LiveTab()
  window.show()

  print('showing the app')
  app.exec_() # Start the event loop
  sys.exit()
import matplotlib.pyplot as plt
from functools import partial
import tkinter as tk
import configparser
import pandas as pd
import numpy as np
import pickle
import os

# Read in the config settings
config = configparser.ConfigParser()
config.read('config.cfg')
FILENAME = config['settings']['filename']
checkPklFile = config.getboolean('settings', 'checkPkl')
data = None
name, extention = os.path.splitext(FILENAME)
if extention == '.pkl': # First check if we have a pickle file to read
  data = pd.read_pickle(FILENAME)
elif checkPklFile:  # Next check if we need to see if we need to look for one
  print(checkPklFile)
  filenameNoExtension = os.path.splitext(FILENAME)[0]
  pklFile = filenameNoExtension + '.pkl'
  if os.path.exists(pklFile):
    data = pd.read_pickle(pklFile)
else:
  data = pd.read_excel(FILENAME)

# Pandas DataFrame Variables
regionData = None  # DataFrame to contain the data for the selected region(s)
teamData = None  # DataFrame to contain the data for the selected team(s)

# Lists of options for the players
REGIONS = list(dict.fromkeys(data['league'].tolist()))
TEAMS = ['select team']   # Will be filled in when the user chooses a region
PLAYERS = ['select player']  # Will be filled in when the user chooses a team
STATS = ['k', 'd', 'a', 'wpm', 'cspm', 'goldspent', 'gspd', 'dmgshare', 'earnedgoldshare', 'goldat10', 'gdat10', 'goldat15', 'gdat15', 'xpat10', 'xpdat10', 'csat10', 'csdat10', 'csat15', 'csdat15']

# Other variables
numTeams = 0
numPlayers = 0
teamNames = [None] * 10 # Will contain a StringVar for each team button available
teamMenus = [None] * 10  # Will contain OptionMenu widgets
playerNames = [None] * 10
playerMenus = [None] * 10
configOpen = False

# Color Palette variables
backgroundColor = '#264653'
highlightColor = '#2a9d8f'
textColor = '#e9c46a'
buttonColor = '#f4a261'
badColor = '#e76f51'

# Create and configure the root
root = tk.Tk()
screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
root.configure(bg=backgroundColor)
root.geometry('+%d+%d' % (screenWidth / 3 - 200, screenHeight / 3 - 35))

class Config:
  def __init__(self, master):
    self.master = master
    master.title("Stat Visualizer Config")
    master.geometry('+%d+%d' % (screenWidth / 3, screenHeight / 3))
    master.protocol("WM_DELETE_WINDOW", self.closeWindow)
    master.configure(bg=backgroundColor)

    # Title
    self.title = tk.Label(master, text='Config', bg=highlightColor, font=('Montserrat', 30), padx=30, pady=5)
    self.save = tk.Button(master, text='Save', bg=highlightColor, command=self.saveConfig)
    self.cancel = tk.Button(master, text='Cancel', bg=badColor, command=self.closeWindow)
    self.fileLabel = tk.Label(master, text="Data file: ", bg=backgroundColor, font=('Open Sans', 16))
    self.filename = tk.Label(master, text=FILENAME, relief='solid', bg=textColor, font=('Open Sans', 16))
    self.changeFile = tk.Button(master, text='Change', bg=buttonColor, command=self.updateDataFile)

    # Checkbox
    self.checkFrame = tk.Frame(master, bg=backgroundColor)
    self.checkVar = tk.BooleanVar()
    self.checkPklLabel = tk.Label(self.checkFrame, text='Look for pkl file', bg=backgroundColor, font=('Open Sans', 12))
    self.checkPkl = tk.Checkbutton(self.checkFrame, text='', activebackground=backgroundColor, bg=backgroundColor, variable=self.checkVar)
    if checkPklFile:
      self.checkPkl.select()
    self.checkPklLabel.grid(row=1, column=1)
    self.checkPkl.grid(row=1, column=2)
    
    
    self.title.grid(row=1, columnspan=10, sticky='EW')
    self.fileLabel.grid(row=2, column=1, padx=5, pady=10)
    self.filename.grid(row=2, column=2, padx=5, pady=10, ipadx=3)
    self.changeFile.grid(row=2, column=3, padx=5, pady=10)
    self.checkFrame.grid(row=3, columnspan=3, padx=5, pady=10, sticky='w')
    self.save.grid(row=4, column=2, padx=5, pady=10, sticky='e')
    self.cancel.grid(row=4, column=3, padx=5, pady=10)

  def closeWindow(self):
    global configOpen
    configOpen = False
    self.master.destroy()

  def saveConfig(self):
    global checkPklFile
    config = configparser.ConfigParser()
    config['settings'] = {'filename': FILENAME, 'checkpkl': self.checkVar.get()}
    with open('config.cfg', 'w') as configfile:
      config.write(configfile)
    checkPklFile = self.checkVar.get()
    self.closeWindow()

  def updateDataFile(self, *args):
    global FILENAME, data, regionData, REGIONS
    newFilename = os.path.basename(tk.filedialog.askopenfilename(filetypes=[("Excel files", ".xlsx .xls"), ("Pickle files", ".pkl")]))
    if newFilename == '':
      return
    
    FILENAME = newFilename
    self.filename.configure(text=FILENAME)

class GUI:
  def __init__(self, master):
    self.master = master
    self.master.title('Stat Visualizer')

    # Title
    self.title = tk.Label(master, text='Stat Visualizer', bg=highlightColor, font=('Montserrat', 30), padx=30, pady=5)
    self.title.grid(row=1, columnspan=10, sticky='EW')

    # Options
    self.datafileFrame = tk.Frame(master, bg=backgroundColor, pady=8)  # Create frame to put other components on
    self.graphTeams = tk.BooleanVar()
    self.graphTeamsLabel = tk.Label(self.datafileFrame, text='Show teams on graph', bg=backgroundColor, font=('Open Sans', 12))
    self.graphTeamsCheckBtn = tk.Checkbutton(self.datafileFrame, text='', bg=backgroundColor, activebackground=backgroundColor, variable=self.graphTeams)
    self.openConfig = tk.Button(self.datafileFrame, text='Config', bg=buttonColor, command=self.openConfigWindow)
    
    self.graphTeamsLabel.grid(row=1, column=1,)
    self.graphTeamsCheckBtn.grid(row=1, column=2)
    self.openConfig.grid(row=1, column=10, padx=10, sticky='e')

    self.datafileFrame.grid(row=2, columnspan=10, padx=30) # Put the frame on the screen

    # Region Selection
    self.selectedRegion = tk.StringVar()
    self.selectedRegion.set("Select Region")
    self.selectedRegion.trace_add('write', self.updateTeams)

    self.regionsLabel = tk.Label(master, text="Regions", bg=backgroundColor, font=('Open Sans', 25))
    self.regions = tk.OptionMenu(master, self.selectedRegion, 'select region', *REGIONS)
    self.regions['menu'].configure(bg=buttonColor, activebackground=textColor)
    self.regions.configure(bg=buttonColor, activebackground=buttonColor, highlightbackground=backgroundColor)

    self.regionsLabel.grid(row=3, column=1, sticky='W', padx=5)
    self.regions.grid(row=4, column=1, sticky='W', padx=5)

    # Team Selection
    self.teamsFrame = tk.Frame(master, bg=backgroundColor) # Create frame to put other components on
    self.teamsLabel = tk.Label(master, text="Teams", bg=backgroundColor, font=('Open Sans', 25)) # The label goes directly on the main window
    self.addTeamBtn = tk.Button(self.teamsFrame, bg=buttonColor, text="add team", command=self.addTeam)
    self.addTeam() # Call our function to add a team, this function allows us to add more teams later

    self.teamsLabel.grid(row=5, column=1, sticky='W', padx=5) # The label goes directly on the main window
    self.addTeamBtn.grid(row=1, column=10)
    self.teamsFrame.grid(row=6, column=1, sticky='W', padx=5) # Put the frame on the screen

    # Player Selection
    self.playersFrame = tk.Frame(master, bg=backgroundColor)
    self.playersLabel = tk.Label(master, text="Players", bg=backgroundColor, font=('Open Sans', 25))
    self.addPlayerBtn = tk.Button(self.playersFrame, bg=buttonColor, text='add player', command=self.addPlayer)
    self.addPlayer()

    self.playersLabel.grid(row=7, column=1, sticky='W', padx=5)
    self.addPlayerBtn.grid(row=1, column=10)
    self.playersFrame.grid(row=8, column=1, sticky='W', padx=5)


    # Stat Selection
    self.selectedStat = tk.StringVar()
    self.selectedStat.set("select stat")
    self.selectedStat.trace_add('write', self.updateGenerate)

    self.statsLabel = tk.Label(master, text="Stats", bg=backgroundColor, font=("Open Sans", 25))
    self.stats = tk.OptionMenu(master, self.selectedStat, *STATS)
    self.stats['menu'].configure(bg=buttonColor, activebackground=textColor)
    self.stats.configure(bg=buttonColor, activebackground=buttonColor, highlightbackground=backgroundColor)

    self.statsLabel.grid(row=9, column=1, sticky='W', padx=5)
    self.stats.grid(row=10, column=1, sticky='W', padx=5)

    # Generate Graph
    self.generateBtn = tk.Button(master, text="Generate", bg=badColor, command=self.generate)
    self.generateBtn.grid(row=11, columnspan=10, pady=20)




  # Creates a new window with the config options, utilizes the Config class
  def openConfigWindow(self, *args):
    global configOpen
    if configOpen:
      return
    configOpen = True
    self.configWindow = tk.Toplevel(self.master)
    self.config = Config(self.configWindow)

  # Adds another drop down box to select a team
  def addTeam(self, *args):
    global numTeams, teamNames

    selectedTeam = tk.StringVar()
    selectedTeam.set("select team")
    if numTeams == 0:
      selectedTeam.trace_add('write', self.updateGenerate)
    # selectedTeam.trace_add('write', partial(self.deleteTeam, numTeams))
    selectedTeam.trace_add('write', self.updatePlayers)
    teamNames[numTeams] = selectedTeam

    team = tk.OptionMenu(self.teamsFrame, selectedTeam, *TEAMS)
    team['menu'].configure(bg=buttonColor, activebackground=textColor)
    team.configure(bg=buttonColor, activebackground=buttonColor, highlightbackground=backgroundColor, width=17)
    team.grid(row=1, column=numTeams + 1)
    teamMenus[numTeams] = team

    numTeams += 1

  # Adds another drop down box to select a player
  def addPlayer(self, *args):
    global numPlayers, numTeams

    selectedPlayer = tk.StringVar()
    selectedPlayer.set('select player')
    if numPlayers == 0:
      selectedPlayer.trace_add('write', self.updateGenerate)
    # selectedTeam.trace_add('write', partial(self.deletePlayer, numPlayers))
    playerNames[numPlayers] = selectedPlayer

    player = tk.OptionMenu(self.playersFrame, selectedPlayer, *PLAYERS)
    player['menu'].configure(bg=buttonColor, activebackground=textColor)
    player.configure(bg=buttonColor, activebackground=buttonColor, highlightbackground=backgroundColor, width=17)
    player.grid(row=1, column=numPlayers + 1)
    playerMenus[numPlayers] = player

    numPlayers += 1

  # Deletes a drop down box to select a team at inded id
  def deleteTeam(self, id, *args):
    if teamMenus[id] == None or not teamNames[id].get() == 'remove team':
      return
    
    teamMenus[id].destroy()

  # Updates the list of teams and the drop down menus to select a team
  def updateTeams(self, *args):
    global TEAMS, regionData, teamMenus
    regionData = data[data.league.eq(self.selectedRegion.get())]
    TEAMS = list(dict.fromkeys(regionData['team'].tolist()))
    for index in range(len(teamMenus)):
      team = teamMenus[index]
      if team == None or not team.winfo_exists() == 1:
        continue # Ignored deleted menus
      menu = team['menu']
      menu.delete(0, "end")
      for t in TEAMS:
        menu.add_command(label=t, command=updateTeamMenuItem(t, index))
      teamNames[index].set('select team')

  # Updates the list of players and the drop down menus to select a player
  def updatePlayers(self, *args):
    global PLAYERS, TEAMS, teamNames
    PLAYERS = []
    for index in range(len(teamNames)):
      team = teamNames[index]
      if team == None:
        continue
      teamData = regionData[regionData.team.eq(team.get())]
      for player in list(dict.fromkeys(teamData['player'].tolist())):
        if not player == 'Team':
          PLAYERS.append(player)
    for index in range(len(playerMenus)):
      player = playerMenus[index]
      if player == None or not player.winfo_exists() == 1:
        continue
      menu = player['menu']
      menu.delete(0, 'end')
      for p in PLAYERS:
        menu.add_command(label=p, command=updatePlayerMenuItem(p, index))
      playerNames[index].set('select player')

  # Checks conditions and sets the background color of the generate button
  def updateGenerate(self, *args):
    if self.canGenerate():
      self.generateBtn.config(bg=highlightColor)
    else:
      self.generateBtn.config(bg=badColor)
    
  # Updates the list of players
  def updatePlayerList(self, *args):
    global PLAYERS, regionData, teamData
    teamData = regionData[regionData.player.eq('Team')]
    PLAYERS = list(dict.fromkeys(regionData['player'].tolist()))

  # Generates the graphs from the selected options
  def generate(self, *args):
    if not self.canGenerate():
      return

    global regionData, teamNames, playerNames
    stat = self.selectedStat.get()


    fig, ax = plt.subplots()

    graphedPlayers = [] # List to store teams we graph to prevent duplicates
    for playerName in playerNames:
      if playerName == None:
        continue
      player = playerName.get()
      if player == 'select player' or player in graphedPlayers: # Skip over already graphed players
        continue
      graphedPlayers.append(player)
      playerStats = regionData[regionData.player.eq(player)]
      ax.plot(range(1, len(playerStats[stat]) + 1), playerStats[stat], label=player)

    if self.graphTeams.get():
      graphedTeams = [] # List to store teams we graph to prevent duplicates
      for teamName in teamNames:
        if teamName == None:
          continue
        team = teamName.get()
        if team == 'select team' or team in graphedTeams: # Skip over already graphed teams or empty teams
          continue
        graphedTeams.append(team)
        teamStats = regionData[regionData.team.eq(team) & regionData.player.eq('Team')]
        ax.plot(range(1, len(teamStats[stat]) + 1), teamStats[stat], label=team)

    ax.set(xlabel='game number', ylabel=stat)
    ax.grid()

    if len(graphedPlayers) == 1: # Dont place a team name in the title if there are multiple teams represented
      plt.title(graphedPlayers[0] + ' ' + stat)
    else:
      plt.title(stat)

    plt.legend()
    fig.show()

  # Checks the conditions set and determins if we can generate a graph
  def canGenerate(self):
    if self.selectedStat.get() == 'select stat':
      return False

    global playerNames
    for playeNames in playerNames:
      if playeNames == None:
        continue
      if not playeNames.get() == 'select player':
        return True
    
    return False
      
# Class to handle tooltips on widgets, added by the createToolTip function below
class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None

    def showtip(self, text):
        if self.tipwindow or not text:
            return
        x, y, cx, cy = self.widget.bbox() # Does "insert" need to be an argument
        x = x + cx + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=text, justify='left',
                      background="#ffffe0", relief='solid', borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# Adds a tooltip to the supplied widget, utilizes the ToolTip class
def createToolTip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

# Helper function to return the lambda command to update when you choose an item from drop down box
def updateTeamMenuItem(team, index):
    global teamNames
    return lambda value=team: teamNames[index].set(value)

def updatePlayerMenuItem(team, index):
    global teamNames
    return lambda value=team: playerNames[index].set(value)

mainGUI = GUI(root)
root.mainloop()
from functools import partial
import tkinter as tk
import configparser
import os, sys

import matplotlib.pyplot as plt
import pandas as pd

from themes import *

statsList = ['kills', 'deaths', 'assists', 'dpm', 'damageshare', 'csat10', 'xpat10', 'csdiffat10', 'golddiffat10', 'csat15', 'xpat15', 'csdiffat15', 'golddiffat15']

class Options(tk.Frame):
  def __init__(self, master, doGraphTeams, openConfig):
    super().__init__()
    self.configure(bg=backgroundColor, pady=8)
    self.graphTeamsLabel = tk.Label(self, text='Show teams on graph', bg=backgroundColor, font=('Open Sans', 12))
    self.graphTeamsCheckBtn = tk.Checkbutton(self, text='', bg=backgroundColor, activebackground=backgroundColor, variable=doGraphTeams)
    self.openConfig = tk.Button(self, text='Config', bg=buttonColor, command=openConfig)
    
    self.graphTeamsLabel.grid(row=1, column=1,)
    self.graphTeamsCheckBtn.grid(row=1, column=2)
    self.openConfig.grid(row=1, column=10, padx=10, sticky='e')

class Region(tk.Frame):
  def __init__(self, master, regions):
    super().__init__()
    self.configure(bg=backgroundColor, pady=8)
    self.selectedRegion = tk.StringVar()
    self.selectedRegion.set("select region")

    self.regionsLabel = tk.Label(self, text="Region: ", bg=backgroundColor, font=('Open Sans', 25))
    self.regions = tk.OptionMenu(self, self.selectedRegion, 'select region', *regions)
    self.regions['menu'].configure(bg=buttonColor, activebackground=textColor)
    self.regions.configure(bg=buttonColor, activebackground=buttonColor, highlightbackground=backgroundColor)

    self.regionsLabel.grid(row=1, column=1, sticky='W')
    self.regions.grid(row=1, column=2, sticky='W')

class Team(tk.Frame):
  def __init__(self, master, teams, data):
    super().__init__()
    self.teamOMs = [None] * 10  # Will contain an Option Menu item for each team
    self.selectedTeams = [None] * 10
    self.playersList = [None] * 10 # Contains a Player object for each team, the Player object maintains the list of players
    self.numTeams = 0
    self.teams = teams
    self.data = data

    self.configure(bg=backgroundColor)
    self.addTeamBtn = tk.Button(self, bg=buttonColor, text="add team", command=self.addTeam)

    teamsLabel = tk.Label(self, text="Teams and Players", bg=backgroundColor, font=('Open Sans', 25))
    teamsLabel.grid(row=1, columnspan=10, sticky='W')
    
    self.addTeam()

  def addTeam(self, *args):
    #pylint: disable=unused-argument
    if self.numTeams > 5:
      return
    
    teamFrame = tk.Frame(self, bg=backgroundColor, highlightbackground='black', highlightthickness=2)
    teamFrame.configure(padx=5, pady=5)

    selectedTeam = tk.StringVar()
    selectedTeam.set('select team')
    selectedTeam.trace_add('write', partial(self.updatePlayers, self.numTeams))
    team = tk.OptionMenu(teamFrame, selectedTeam, *self.teams)
    team.configure(bg=buttonColor, activebackground=buttonColor, highlightbackground=backgroundColor, width=17)
    team['menu'].configure(bg=buttonColor, activebackground=textColor)

    player = Player(teamFrame, ['select player'])

    team.grid(row=1, column=1)
    player.grid(row=2, column=1)
    teamFrame.grid(row=2, column=self.numTeams + 1, padx=5, sticky='NW')
    self.addTeamBtn.grid(row=2, column=self.numTeams + 2)

    self.teamOMs[self.numTeams] = team  # Add the team Option Menu to the list
    self.selectedTeams[self.numTeams] = selectedTeam
    self.playersList[self.numTeams] = player

    self.numTeams += 1

  def updateTeams(self, newTeams):
    self.teams = newTeams
    for index in range(len(self.teamOMs)):
      team = self.teamOMs[index]
      if team is None:
        continue
      menu = team['menu']
      menu.delete(0, 'end')
      for t in newTeams:
        menu.add_command(label=t, command=self.updateSelectedTeamCommand(t, index))
    
    for selectedTeam in self.selectedTeams:
      if selectedTeam is None:
        continue
      selectedTeam.set('select team')

  def updatePlayers(self, index, *args):
    #pylint: disable=unused-argument
    selectedTeam = self.selectedTeams[index].get()
    teamData = self.data[self.data['team'].eq(selectedTeam)]
    teamData = teamData[teamData['player'].ne('Team')]  # Remove the entries of the team
    playersList = list(dict.fromkeys(teamData['player'].tolist()))
    self.playersList[index].updatePlayers(playersList)

  def updateSelectedTeamCommand(self, team, index):
    return lambda value=team: self.selectedTeams[index].set(value)

  def getTeams(self):
    teams = []
    for team in self.selectedTeams:
      if team is None:
        continue
      teams.append(team.get())
    return teams

  def getPlayers(self):
    players = []
    for player in self.playersList:
      if player is None:
        continue
      teamPlayers = player.getPlayers()
      for p in teamPlayers:
        players.append(p)
    return players

class Player(tk.Frame):
  def __init__(self, master, players):
    super().__init__(master)
    self.playerOMs = [None] * 10
    self.selectedPlayers = [None] * 10
    self.numPlayers = 0
    self.players = players

    self.configure(bg=backgroundColor)
    self.addPlayerBtn = tk.Button(self, bg=buttonColor, text='add player', command=self.addPlayer)

    self.addPlayerBtn.grid(row=1, column=1)

  def addPlayer(self):
    if self.numPlayers > 5:
      return

    selectedPlayer = tk.StringVar()
    selectedPlayer.set('select player')
    player = tk.OptionMenu(self, selectedPlayer, *self.players)
    player.configure(bg=buttonColor, activebackground=buttonColor, highlightbackground=backgroundColor, width=17)
    player['menu'].configure(bg=buttonColor, activebackground=textColor)

    player.grid(row=self.numPlayers + 1, column=1)
    self.addPlayerBtn.grid(row=self.numPlayers + 2, column=1)
    
    self.playerOMs[self.numPlayers] = player
    self.selectedPlayers[self.numPlayers] = selectedPlayer

    self.numPlayers += 1

  def updatePlayers(self, newPlayersList):
    self.players = newPlayersList
    for index in range(len(self.playerOMs)):
      player = self.playerOMs[index]
      if player is None:
        continue
      menu = player['menu']
      menu.delete(0, 'end')
      for p in newPlayersList:
        menu.add_command(label=p, command=self.updateSelectedPlayerCommand(p, index))
    
    for selectedPlayer in self.selectedPlayers:
      if selectedPlayer is None:
        continue
      selectedPlayer.set('select player')

  def updateSelectedPlayerCommand(self, player, index):
    return lambda value=player: self.selectedPlayers[index].set(value)

  def getPlayers(self):
    players = []
    for player in self.selectedPlayers:
      if player is None:
        continue
      players.append(player.get())
    return players

class Stats(tk.Frame):
  def __init__(self, master, statList):
    super().__init__()
    self.configure(bg=backgroundColor)

    self.selectedStat = tk.StringVar()
    self.selectedStat.set('select stat')

    statsLabel = tk.Label(self, text='Stats', bg=backgroundColor, font=('Open Sans', 25))
    statsMenu = tk.OptionMenu(self, self.selectedStat, *statList)
    statsMenu.configure(bg=buttonColor, activebackground=buttonColor, highlightbackground=backgroundColor, width=12)
    statsMenu['menu'].configure(bg=buttonColor, activebackground=textColor)

    statsLabel.grid(row=1, column=1)
    statsMenu.grid(row=2, column=1)
    
  def getStat(self):
    return self.selectedStat.get()

class Config:
  def __init__(self, master, filename, saveFunction):
    self.master = master
    self.filename = filename
    self.configOpen = True
    self.saveFunction = saveFunction
    master.title("Stat Visualizer Config")
    master.geometry('+%d+%d' % (screenWidth / 3, screenHeight / 3))
    master.protocol("WM_DELETE_WINDOW", self.closeWindow)
    master.configure(bg=backgroundColor)


    # Title
    self.title = tk.Label(master, text='Config', bg=highlightColor, font=('Montserrat', 30), padx=30, pady=5)
    self.save = tk.Button(master, text='Save', bg=highlightColor, command=self.saveConfig)
    self.cancel = tk.Button(master, text='Cancel', bg=badColor, command=self.closeWindow)
    self.fileLabel = tk.Label(master, text="Data file: ", bg=backgroundColor, font=('Open Sans', 16))
    self.filenameLabel = tk.Label(master, text=self.filename, relief='solid', bg=textColor, font=('Open Sans', 16))
    self.changeFile = tk.Button(master, text='Change', bg=buttonColor, command=self.updateDataFile)    
    
    self.title.grid(row=1, columnspan=10, sticky='EW')
    self.fileLabel.grid(row=2, column=1, padx=5, pady=10)
    self.filenameLabel.grid(row=2, column=2, padx=5, pady=10, ipadx=3)
    self.changeFile.grid(row=2, column=3, padx=5, pady=10)
    self.save.grid(row=4, column=2, padx=5, pady=10, sticky='e')
    self.cancel.grid(row=4, column=3, padx=5, pady=10)

  def closeWindow(self):
    self.configOpen = False
    self.master.destroy()

  def saveConfig(self):
    config = configparser.ConfigParser()
    config['settings'] = {'filename': self.filename}
    with open(os.path.join(sys.path[0], 'config.cfg'), 'w') as configfile:
      config.write(configfile)
    self.saveFunction()
    self.closeWindow()

  def updateDataFile(self, *args):
    #pylint: disable=unused-argument
    newFilename = os.path.basename(tk.filedialog.askopenfilename(filetypes=[("CSV Files", ".csv"), ("Pickle files", ".pkl")]))
    if newFilename == '':
      return
    self.filename = newFilename
    self.filenameLabel.configure(text=newFilename)

class GUI(tk.Frame):
  def __init__(self, master):
    super().__init__(master)
    self.master = master
    master.title("Stat-Visualizer")
    self.configOpen = False

    self.readConfig() # Gets the setting from our config file
    self.readData() # Reads the data and creates dataframes 
    
    # Lists of available options to choose from
    self.regionsList = list(dict.fromkeys(self.data['league'].tolist()))
    self.statsList = ['k', 'd', 'a', 'wpm', 'cspm', 'goldspent', 'gspd', 'dmgshare', 'earnedgoldshare', 'goldat10', 'gdat10', 'goldat15', 'gdat15', 'xpat10', 'xpdat10', 'csat10', 'csdat10', 'csat15', 'csdat15']
    
    # Counts and lists / options CHOSEN by user
    self.configOpen = False
    self.doGraphTeams = tk.BooleanVar()
    self.doGraphTeams.set(False)

    # Create frames
    self.title = tk.Label(master, text='Stat Visualizer', bg=highlightColor, font=('Montserrat', 30))
    self.optionsMenu = Options(self, self.doGraphTeams, self.openConfigWindow)
    self.regionsMenu = Region(self, self.regionsList)
    self.teamsMenu = Team(self, ['select team'], self.data)
    self.generateBtn = tk.Button(master, text="Generate", bg=badColor, command=self.generate)
    self.statsMenu = Stats(self, statsList)
    
    self.regionsMenu.selectedRegion.trace_add('write', self.updateTeamsList)
    
    # Display widgets
    self.title.grid(row=1, columnspan=10, sticky='EW')
    self.optionsMenu.grid(row=2, columnspan=10, padx=30)
    self.regionsMenu.grid(row=3, column=1, padx=15, sticky='W')
    self.teamsMenu.grid(row=4, column=1, padx=15, sticky="W")
    self.statsMenu.grid(row=5, column=1, padx=15, sticky='W')
    self.generateBtn.grid(row=20, columnspan=20, pady=20)  # Make sure its always at the bottom and centered

  def readConfig(self):
    config = configparser.ConfigParser()
    config.read(os.path.join(sys.path[0], 'config.cfg'))
    self.FILENAME = config['settings']['filename']
  
  def readData(self):
    name, extention = os.path.splitext(self.FILENAME)
    self.data = None
    if extention == '.pkl': # Check if we have a pickle file to read
      self.data = pd.read_pickle(os.path.join(sys.path[0], self.FILENAME))

    # Always check for a pkl file (of the same base name) before reading the csv
    pklFile = name + '.pkl'
    if os.path.exists(pklFile):
      self.data = pd.read_pickle(os.path.join(sys.path[0], pklFile))
    else:
      self.data = pd.read_csv(os.path.join(sys.path[0], self.FILENAME))

    # Empty data frames to contain subsets of the data later on
    self.regionData = None
    self.teamData = None

  def openConfigWindow(self):
    #pylint: disable=attribute-defined-outside-init
    if self.configOpen:
      return
    self.configOpen = True
    self.configWindow = tk.Toplevel(self.master)
    self.config = Config(self.configWindow, self.FILENAME, self.updateFromConfig)

  def updateTeamsList(self, *args):
    #pylint: disable=unused-argument
    # Updates the list of available teams, and tells the team object to update itself
    region = self.regionsMenu.selectedRegion.get()
    teamsList = list(dict.fromkeys(self.data[self.data['league'].eq(region)]['team'].tolist()))
    self.teamsMenu.updateTeams(teamsList)

  def generate(self, *args):
    #pylint: disable=unused-argument
    teams = self.teamsMenu.getTeams()
    players = self.teamsMenu.getPlayers()
    graphTeams = self.doGraphTeams.get()
    stat = self.statsMenu.getStat() 
    data = self.data

    _, ax = plt.subplots()

    graphedPlayers = [] # Keep a list of who we graph, so we dont graph the same player twice
    for player in players or player == 'select player':
      if player in graphedPlayers:
        continue
      graphedPlayers.append(player)
      playerStats = data[data.player.eq(player)]
      ax.plot(range(1, len(playerStats) + 1), playerStats[stat], label=player)
    
    if graphTeams:
      graphedTeams = [] # Keep a list of who we graph, so we dont graph the same team twice
      for team in teams:
        if team in graphedTeams or team == 'select team':
          continue
        graphedTeams.append(team)
        teamStats = data[data.team.eq(team) & data.player.eq('Team')]
        ax.plot(range(1, len(teamStats[stat]) + 1), teamStats[stat], label=team)

    ax.set(xlabel='game number', ylabel=stat)
    ax.grid()
    plt.legend()
    plt.show()

  def updateFromConfig(self):
    self.readConfig()
    self.readData()

# Create and configure the root
root = tk.Tk()
screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
root.configure(bg=backgroundColor)
root.geometry('+%d+%d' % (screenWidth / 3 - 200, screenHeight / 3 - 35))

mainGUI = GUI(root)
root.mainloop()

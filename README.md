# Pro League of Legends Stat Visualizer

A variety of programs to create cool graphs of pro League of Legends data.

To install all dependencies of the apps, simply run this command
```
pip install -r requirements.txt
```
for the live gold graph run ```LiveWindow.py```
and for the season wide stats, run ```main-1.0.py or main-2.0.py```

##### NEW --- Live Gold Graph

The live gold grapher utilizes selenium and pyqt5 to create an interactive gui and graphs for live gold difference graphs while games are being played. Selenium scraper runs in a separate thread and polls the website for its status on streams live, games live, and stats live. 
####### Note: currently the change region drop down box does not work, but will be fixed in an update soon

##### Season wide stats
In the Old Tkinter Version folder lies main-1.0 and main-2.0. Both of these programs read a data file from Oracle's Elixer's match data files found [here](https://oracleselixir.com/tools/downloads)
A list of all stats and what they are can be found on their website [here](https://oracleselixir.com/definitions)
To change that available stats to graph, simply add or remove the stat from the  statsList defined at the top of the main file.

To increase load times, run the convertData.py script first and convert the csv file into a .pkl file which stores the pandas dataFrame and allows the app to read in the data much faster. Main-2.0 will automatically search for the .pkl file and use that if found. 

This app will eventually be condenced into 1 large GUI using pyqt5 and implementing all the features found here and several more.

# Update Notes
## Live Gold Graph Release
* Released a live gold grapher which uses selenium and threads to scrape the [lolesports](https://lolesports.com/schedule?leagues=lcs) website for live game data
* Shows status bars for when the stream is up, game is live, and stats are available.
* Plots the gold difference in a matplotlib grpah that updates once per second
* Switched from tkinter to pyqt5 for better GUIs
* GUIs now stored in ui files created with [QT Designer](https://www.qt.io/)

### Other updates
* Main app with tkinter versions 1 and 2 got minor updates to work with the new Oracle's Elixer format (CSV files and a few tweaks)
* Cleaned up some other portions of the code for better support running in a subdirectory
* Added requirements.txt file to install all dependencies quickly

## v 2.0
* Restructured the code into distint objects to organize better
* Removed global variables
* Overall clearner code
* Changed the structure of choosing teams and players. The app now allows you to add and choose players for each specific team, reducing the number of options in each option menu.
* Moved theme colors variables to a theme file that is imported
* Removed config option to search for pkl file, it now always checks for one with the same base name as the provided filename

# TODO
add option to choose stat options in the config menu                                                                
integrate matplotlib graph into a tkinter window with nicer buttons

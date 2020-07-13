# Pro League of Legends Stat Visualizer

This program utilizes tkinter, pandas and matplotlib to create nice graphs for many combinations of players and teams across all major League of Legends regions.

The stats are read in from the excel files provided by Oracle's Elixir found [here](https://oracleselixir.com/matchdata/)
A list of all stats and what they are can be found on their website [here](https://oracleselixir.com/matchdata/match-data-dictionary/)
To change that available stats to graph, simply add or remove the stat from the  statsList defined at the top of the main file. This will hopefully be added to the config options at some point in the future.
### NOTE: these links are now invalid as Oracle's Elixer is in the processess of updating their website, they will be updated when they finish and any changes are accounted for

To increase load times, run the convertData.py script first and convert the excel file into a .pkl file which stores the pandas dataFrame and allows the app to read in the data much faster. This will hopefully also be added into the config menu as an option at some point.

Make sure the to select the correct datafile in the config menu of the app. By default the app will look for 'data.xlsx' as the data file and will also check to see if 'data.pkl' exists, and use that instead if it finds it.

# Update Notes
## v 2.0
Restructured the code into distint objects to organize better
Removed global variables
Overall clearner code
Changed the structure of choosing teams and players. The app now allows you to add and choose players for each specific team, reducing the number of options in each option menu.
Moved theme colors variables to a theme file that is imported
Removed config option to search for pkl file, it now always checks for one with the same base name as the provided filename

# TODO
add option to choose stat options in the config menu                                                                
integrate matplotlib graph into a tkinter window with nicer buttons

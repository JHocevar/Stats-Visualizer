## Pro League Stat Visualizer

This program utilizes tkinter, pandas and matplotlib to create nice graphs for many combinations of players and teams across all major League of Legends regions.

The stats are read in from the excel files provided by Oracle's Elixer found [here](https://oracleselixir.com/matchdata/)
A list of all stats and what they are can be found on their website [here](https://oracleselixir.com/matchdata/match-data-dictionary/)
To change that available stats to graph, simply add or remove the stat from the STATS list defined in the main.py file. This will hopefully be added to the config options at some point in the future.

To increase load times, run the convertData.py script first and convert the excel file into a .pkl file which stores the pandas dataFrame and allows the app to read in the data much faster. This will hopefully also be added into the config menu as an option at some point.

Make sure the to select the correct datafile in the config menu of the app. By default the app will look for 'data.xlsx' as the data file and will also check to see if 'data.pkl' exists, and use that instead if it finds it.

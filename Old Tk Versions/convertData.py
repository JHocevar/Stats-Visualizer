import os, sys
from tkinter import filedialog
import tkinter as tk
import pandas as pd

root = tk.Tk()
root.withdraw()

filename = filedialog.askopenfilename(filetypes=[('CSV Files', ".csv")])

filename = os.path.basename(filename)
data = pd.read_csv(os.path.join(sys.path[0], filename))

filenameNoExtension = os.path.splitext(filename)[0]

data.to_pickle(os.path.join(sys.path[0], filenameNoExtension) + '.pkl')

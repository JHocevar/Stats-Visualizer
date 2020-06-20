from tkinter import filedialog
import tkinter as tk
import pandas as pd
import pickle
import os

root = tk.Tk()
root.withdraw()

filename = filedialog.askopenfilename(filetypes=[('Excel files', ".xlsx .xls")])

filename = os.path.basename(filename)
data = pd.read_excel(filename)

filenameNoExtension = os.path.splitext(filename)[0]

data.to_pickle(filenameNoExtension + '.pkl')

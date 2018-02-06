'''
Author: Archer Morgan
Date of Most recent Change: 8/28/2017

Functionality:
    This file contains the Expector and ScanIn classes, each necessary to perform the function of an expector
    in Clarity. Samples are read in from a 








'''

import tkinter as tk
from tkinter import *
from tkinter import ttk
import difflib
# import os
# import time

'''
this file adapts the code from Expextor.py to provide a locate-sample function
'''

class ScanIn(tk.Frame):
    def __init__(self, parent, sample_names):
        tk.Frame.__init__(self, parent)

        self.label_colors = []
        self.sample_names = sample_names
        self.sample_count = 0
        for i in sample_names:
            if i != "blank":
                self.sample_count += 1
        self.scanned = []
        self.my_Expector = None
        self.ScanIn = None
        self.gridFocusIndex = 0

        # widget declarations
        request = ("Enter the sample you would like to locate:")
        self.ask_for_sample_label = tk.Label(self, text=request)
        self.text = tk.Text(self, state='disabled',height=11, width=40)
        self.entry = tk.Entry(self)
        self.create_expector()

        # gui actions
        self.entry.bind("<Return>", self.focusOnSample)
        self.entry.focus()
        self.ask_for_sample_label.grid(row=1, column=2)
        self.entry.grid(row=2, column=2)
        self.text.grid(row=3, column=2, rowspan=6, padx=10)

    '''uppon pressing self.buttion, this method produces the toplevel window
    that is the expector view. It is a grid of labels currently read in from a
    csv with all of the values in one single column.'''

    def create_expector(self):
        self.my_Expector = ExpectorView(self, self.sample_names)

    def checkIfNoSamples(self):
        if self.sample_count == 0:
            return ""
        else:
            return self.sample_names[0]

    def focusOnSample(self, event):
        '''implements the find sample freature'''
        self.text.configure(state='normal')
        self.text.delete('1.0', 'end')
        found = False
        for i in range(len(self.my_Expector.labels_grid)):
            if self.my_Expector.labels_grid[i].cget("text") == self.entry.get():
                found = True
                self.my_Expector.labels_grid[i].configure(background="#8B008B")
            elif self.my_Expector.labels_grid[i].cget("text") == 'blank':
                self.my_Expector.labels_grid[i].configure(background="#D3D3D3")
            else:
                self.my_Expector.labels_grid[i].configure(background="#00FFFF")
        if not found:
            self.bell()
            self.text.insert('end', 'Sample Not Found')
            self.text.tag_add('red','1.0','2.0')
            self.text.tag_configure('red', foreground='red', underline=1)

            altquery = difflib.get_close_matches(self.entry.get(), self.sample_names, 1, 0.5)
            if len(altquery)==0:
                pass
            else:
                self.text.insert('end', '\n\nCLOSEST MATCH:    '+altquery[0])
        else:
            self.entry.delete(0, 'end')


'''# Takes the input string s, if it is the first time being called, and
# the value of if the entry was valid. It then writes it to a txt file
# called procedure log w/ added time stamp.

# TODO: writes what step Lims is on (if I can), which user did what to
# which samples, what procedure, what project; can be .txt
def write_log(entryText, valid):
    fname = "Procedure_Log.txt".format(time.strftime('%Y-%M-%d_%H.%M.%S'))
    if fname not in os.listdir():
        with open(fname, 'w', newline='') as text_file:
            text_file.write("sample " + entryText + " has been scanned."
                            + " It is the correct sample: " + str(valid)
                            + "\n")
    else:
        with open(fname, 'a', newline='') as text_file: #'a' = append
            text_file.write("sample " + entryText + " has been scanned."
                            + " It is the correct sample: " + str(valid)
                            + "\n")
    return'''


class ExpectorView:
    """
        " This should open a window that contains an expector grid",
        "with all of the samples from the CSV. Empty wells are color",
        "coded to be grey, full wells are color coded to be blue.",
        "currently, the grid focuses on a sample at a time, moving through",
        "the full grid according to the pressing of the enter key.",
        "parameters: self, master, String list of samples read in from",
        "the CSV."
        """

    def __init__(self, master, sample_names):
        self.labels_grid = []
        self.y_axis_labels = []
        self.x_axis_labels = []

        # establish plate axes (A,B,C... and 1,2,3...)
        letters = "ABCDEFGH"
        for x in range(8):
            self.y_axis_labels.append(
                ttk.Label(master, text=letters[x],
                          background="#D3D3D3", foreground="#8B008B"))
            self.y_axis_labels[x].grid(
                row=x + 2, column=3,
                sticky=tk.E + tk.W + tk.N + tk.S, padx=1, pady=1)

        for x in range(12):
            self.x_axis_labels.append(
                ttk.Label(master, text=str(x + 1),
                          background="#D3D3D3", foreground="#8B008B",
                          anchor="center", width=10))
            self.x_axis_labels[x].grid(
                row=1, column=x + 4,
                sticky=tk.E + tk.W + tk.N + tk.S, padx=1, pady=1)

        # fill with labels
        for i in range(len(sample_names)):
            self.rowVal = (i % 8 + 2)
            self.colVal = (i // 8 + 2)
            if (sample_names[i] == "blank"):
                self.labels_grid.append(
                    ttk.Label(master, text=sample_names[i],
                              background="#D3D3D3"))
                self.labels_grid[i].grid(
                    row=self.rowVal, column=self.colVal+2,
                    sticky=tk.E + tk.W + tk.N + tk.S, padx=1, pady=1)
            else:
                self.labels_grid.append(
                    ttk.Label(master, text=sample_names[i],
                              background="#00FFFF"))
                self.labels_grid[i].grid(row=self.rowVal, column=self.colVal+2,
                                         sticky=tk.E + tk.W + tk.N + tk.S,
                                         padx=1, pady=1)
            master.columnconfigure(self.colVal, minsize=70)
            master.rowconfigure(self.rowVal, minsize=30)


    def readInError(self, index):
        self.labels_grid[index].configure(background="#EE3B3B")



def build_list_from_dict(sample_dict):
    row = 'ABCDEFGH'
    x = 0
    sample_names = []
    for x in range(96):
        sample_names.append('blank')
    for key in sample_dict.keys():
        x = (int(key[-1]) - 1) * 8 + row.index(key[0])
        sample_names[x] = sample_dict[key]
    return(sample_names)


def main():
    test_dict_1 = {'A1':'Sample 1', 'B1':'Sample2', 'C1':'hog\'s blood', \
                    'D1':'next','F1':'Tears1', 'G1':'Tears2', 'H1':'Tears3', \
                    'A2':'Tears4', 'B2':'Tears5', 'C2':'Tears6', 'D2':'Tears7',\
                    'E2':'Tears8', 'F2':'Tears9', 'G2':'TEars10', 'H2':'veritaserum',\
                    'E1':'stuff'}
    test_dict_2 =  {'B1':'Sample2', \
                    'D1':'next','F1':'Tears1', 'G1':'Tears2', 'H1':'Tears3', \
                    'A2':'Tears4', 'C2':'Tears6', 'D2':'Tears7',\
                    'E2':'Tears8', 'F2':'Tears9', 'H2':'veritaserum'}

    sample_names = build_list_from_dict(test_dict_1)

    '''if len(sys.argv) > 2 or len(sys.argv) < 2:
        print("You put in the wrong number of arguments! Start Over!")
        quit()

    #sample_names=parse_csv(sys.argv[1])'''

    root = tk.Tk()
    root.title("Expector in Find Mode")
    ScanIn(root, sample_names).pack()
    root.mainloop()
    return


if __name__ == "__main__":
    main()

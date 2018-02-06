'''
Author: Archer Morgan
Date of Most recent Change: 8/28/2017

Functionality:
    This file contains the Expector and ScanIn classes, each necessary to perform the function of an expector
    in Clarity. Samples are read in from a 

'''



import tkinter as tk
import datetime
from tkinter import ttk
import sys
import re
import warnings
import glsapiutilP3
from optparse import OptionParser
from math import floor
from tkinter import messagebox
from bs4 import BeautifulSoup




user_inputted_uri = ''


class ScanIn(tk.Frame):

    def __init__(self, parent, sample_names):
        tk.Frame.__init__(self, parent)

        #this is the buffer where all log notes will be written, 
        #according to the specifications in the log spec file. When the program
        #complletes, the buffer will be written to a log file.
        self.log_buffer = 'Person:______   ' + 'Date/time: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n'

        #set on_closing to handle the window close method
        parent.protocol('WM_DELETE_WINDOW', self.on_closing)

        #prepare for gui
        #set first index to be index of first sample
        self.label_colors = []
        self.sample_names = sample_names
        self.sample_count = 0
        self.scanned = []
        self.my_Expector = None
        self.ScanIn = None
        self.completed = False

        #create expector window
        self.my_Expector = ExpectorView(self, self.sample_names)
        self.my_Expector.advanceCurLoc(True)

        # widget declarations
        request = ("Please scan your samples. First scan " +
                   sample_names[self.my_Expector.get_curloc()])
        self.ask_for_sample_label = tk.Label(self, text=request)
        self.text = tk.Text(self, state='disabled', height=10, width=30)
        self.entry = tk.Entry(self)

        # gui actions
        self.entry.bind("<Return>", self.enter)
        self.entry.focus()
        self.ask_for_sample_label.grid(row=1, column=2)
        self.entry.grid(row=2, column=2)
        self.text.grid(row=3, column=2, rowspan=6, padx=10)




    def enter(self, event):
        # reset if an error has been made
        self.text.configure(state='normal')
        self.text.tag_remove('red', '1.0', 'end')
        alreadyScanned = 0

        if self.my_Expector.isValidScan(self.entry.get()):
            self.entry.delete(0, 'end')
            self.my_Expector.advanceCurLoc()
            if self.my_Expector.get_curloc() == 96:
                self.end_of_plate()
                return
            self.text.delete(1.0, 2.0)
            self.scanned.append(self.sample_names[self.my_Expector.get_curloc()])
            self.text.insert('end', "You have scanned: " + self.sample_names[self.my_Expector.get_curloc()] +
                             "\n")
            # change text in ask_for_sample_label
            self.ask_for_sample_label.configure(
                text="Please scan " + self.sample_names[self.my_Expector.get_curloc()])
        else:
            self.bell()
            # delete the previous enter message
            self.text.delete(1.0, 2.0)
            self.my_Expector.readInError(self.my_Expector.get_curloc())
            # Case 3
            self.log_buffer += 'Incorrect scan for well\n'
            for x in self.scanned:
                if (self.entry.get() == x):
                    self.text.insert(
                        'end', 'You have already scanned ' + self.entry.get() +
                        ".\n", 'red')
                    alreadyScanned = 1
                    break
            if (not alreadyScanned):
                # Case 2
                if (self.entry.get() in self.sample_names):
                    self.text.insert(
                        'end', self.entry.get() +
                        " is not the sample currently requested.\n",
                        'red')
                else:
                    self.text.insert(
                        'end', self.entry.get() +
                        " is not in your ice bucket.\n", 'red')
            # Paint it red
            self.text.tag_add('red', '1.0', 'end')
            self.text.tag_configure('red', foreground='red', underline=1)
            self.entry.delete(0, 'end')


    def end_of_plate(self):
        self.completed = True
        self.text.config(state=NORMAL)
        self.text.delete(1.0,'end')
        self.text.insert('end', "You have scanned all your samples!")
        self.entry.delete(0, 'end')
        self.text.tag_add('green', '1.0', 'end')
        self.text.tag_configure('green', foreground='green')
        self.entry.configure(state='disabled')
        self.ask_for_sample_label.configure(
            text="All samples have been scanned.")
        self.entry.delete(0, 'end')
        self.focus()
       


    #this method is going to override tkinter's on_closing event, which is 
    #triggered by clicking the red X in the upper right hand corner
    def on_closing(self):
        self.write_log(self.log_buffer)
        self.quit()

        #writes log buff to log, adds success of failure message
    def write_log(self, entryText):
        with open("Procedure_log", 'w') as f:
            f.write(self.log_buffer)
            if self.completed:
                f.write("Process successfully completed\n")
            else:
                f.write("Process terminated prior to completion\n")
            f.close()




class ExpectorView:
    """
        "This should open a window that contains an expector grid",
        "with all of the samples from the CSV. Empty wells are color",
        "coded to be grey, full wells are color coded to be blue.",
        "currently, the grid focuses on a sample at a time, moving through",
        "the full grid according to the pressing of the enter key.",
        """

    def __init__(self, master, sample_names):
        self.master = master
        self.labels_grid = []
        self.y_axis_labels = []
        self.x_axis_labels = []
        self.sample_names = sample_names
        self.gridFocusIndex = 0

        # establish plate axes (A,B,C... and 1,2,3...)
        self.letters = "ABCDEFGH"
        for x in range(8):
            self.y_axis_labels.append(
                ttk.Label(master, text= '          ' +self.letters[x],
                          background="#D3D3D3", foreground="#8B008B",))
            self.y_axis_labels[x].grid(
                row=x + 2, column=3,
                sticky=tk.E + tk.W + tk.N + tk.S, padx=1, pady=1)

        for x in range(12):
            self.x_axis_labels.append(
                ttk.Label(master, text=str(x + 1),
                          background="#D3D3D3", foreground="#8B008B",
                          anchor="center", width = 10))
            self.x_axis_labels[x].grid(
                row=1, column=x + 4,
                sticky=tk.E + tk.W + tk.N + tk.S, padx=1, pady=1)

        # fill with labels
        for i in range(len(sample_names)):
            self.rowVal = (i % 8 + 2)
            self.colVal = (i // 8 + 2)
            if (sample_names[i] == ""):
                self.labels_grid.append(
                    ttk.Label(master, text=sample_names[i],
                              background="#D3D3D3"))
                self.labels_grid[i].grid(
                    row=self.rowVal, column=self.colVal + 2,
                    sticky=tk.E + tk.W + tk.N + tk.S, padx=1, pady=1)
            else:
                self.labels_grid.append(
                    ttk.Label(master, text=sample_names[i],
                              background="#00FFFF"))
                self.labels_grid[i].grid(row=self.rowVal, column=self.colVal + 2,
                                         sticky=tk.E + tk.W + tk.N + tk.S,
                                         padx=1, pady=1)
            master.columnconfigure(self.colVal, minsize=75)
            master.rowconfigure(self.rowVal, minsize=30)

    def advanceCurLoc(self, start=False):
        """ changes backgrouknd color of labels in the grid to visualize
        the advancement of the expector comparison focus"""
        if start:
            while self.labels_grid[self.gridFocusIndex].cget("text") == "":
                    self.gridFocusIndex += 1
            self.labels_grid[self.gridFocusIndex].configure(background="#8B008B")
            self.master.log_buffer += "expecting sample \'" + self.labels_grid[self.gridFocusIndex].cget("text") + "\' in well " + self.letters[self.gridFocusIndex%8] + str(floor(self.gridFocusIndex/8) + 1) + '\n'
            return

        self.labels_grid[self.gridFocusIndex].configure(background="#39FF14")
        letters = "ABCDEFGH"
        self.gridFocusIndex += 1
        if self.gridFocusIndex > 95:
            return
        while self.labels_grid[self.gridFocusIndex].cget("text") == "":
            self.gridFocusIndex += 1
            if self.gridFocusIndex == 96:
                return
        self.labels_grid[self.gridFocusIndex].configure(background="#8B008B")
        self.master.log_buffer += "expecting sample \'" + self.labels_grid[self.gridFocusIndex].cget("text") + "\' in well " + self.letters[self.gridFocusIndex%8] + str(floor(self.gridFocusIndex/8) + 1) + '\n'

    def readInError(self, index):
        self.labels_grid[index].configure(background="#EE3B3B")

    def isValidScan(self, scan):
        return (scan == self.labels_grid[self.gridFocusIndex].cget("text"))

    def get_curloc(self):
        return self.gridFocusIndex


def set_uri_inputted_by_user(uri, root):
    global user_inputted_uri
    user_inputted_uri = uri
    root.destroy()


def build_list_from_dict(sample_dict):
    row = 'ABCDEFGH'
    x = 0
    sample_names = []
    for x in range(96):
        sample_names.append('')
    for key in sorted(sample_dict.keys()):
        if len(key) > 2:
            x = (int(key[-2:]) - 1) * 8 + row.index(key[0])
        else:
            x = (int(key[-1]) - 1) * 8 + row.index(key[0])
        sample_names[x] = sample_dict[key]
    return(sample_names)






def main():


    username = ''
    password = ''
    global user_inputted_uri

    # read in credentials from super secret file
    f = open('.gitignore\\auth-credentials')
    lines = f.readlines()
    username = lines[0].strip()
    password = lines[1].strip()
    f.close()

    # quickly get url from user 
    query_root = tk.Tk()
    query_root.resizable(width=False, height=False)
    query_root.geometry('{}x{}'.format(400, 100))
    query_root.title('Expector')
    l = tk.Label(query_root, text='Please enter the URL from the Record Details page\nfor the samples you want to expect.')
    e = tk.Entry(query_root)
    e.configure(width=50)
    e.focus_set()
    e.bind('<Return>', lambda x: set_uri_inputted_by_user(e.get(), query_root))
    b = tk.Button(query_root,text='SUBMIT',command=lambda: set_uri_inputted_by_user(e.get(), query_root))
    b.configure(activebackground='#CC3232', background='#CD5555')
    l.grid(row=2, column=1)
    e.grid(row=3, column = 1,  padx=18, pady = 10)
    b.grid(row=3, column = 2, padx=0, pady = 10)
    query_root.mainloop() 

    # manipulate the user-inputted url to become the xml uri
    base = 'https://uagc-dev.claritylims.com/api/v2/steps/24-'
    resource_id = user_inputted_uri.split('/')[-1]
    user_inputted_uri = base + resource_id + '/details'

    # get samples using Clarity API
    sample_dict = {}
    api = glsapiutilP3.glsapiutil2()
    api.setURI('https://uagc-dev.claritylims.com/api/v2/')
    api.setup(
        username,
        password)
    xml = ''
    try:
        xml = b'\n'.join(api.GET(user_inputted_uri).split(b'\n')[1:])
    except:
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showinfo("Error", "The URL supplied was invalid")
        return

    if xml == '':
        root = tk.Tk()
        root.withdraw()
        tk.messagebox.showinfo("Error", "The URL supplied was invalid")
        return

    details_dom = BeautifulSoup(xml, 'lxml')

    analyte_artifacts = []
    for art in details_dom.findAll('output'):
        if art['type'] == "Analyte":
            analyte_artifacts.append(art['uri'])

    xml = b'\n'.join(api.getArtifacts(analyte_artifacts).split(b'\n')[1:])

    xml = BeautifulSoup(xml, 'lxml')

    samples = xml.findAll('name')
    names = xml.findAll('location')

    for i, name in enumerate(names):
        sample_dict[names[i].value.string.replace(':','')] = samples[i].string

    sample_names = build_list_from_dict(sample_dict)

    sample_count = 0
    for k in sample_names:
        if k != '':
            sample_count += 1

    if sample_count == 0:
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Title", "No samples to expect. It seems the ice bucket is empty.")
        return
    else:
        root = tk.Tk()
        root.title("Expector")
        ScanIn(root, sample_names).pack()
        root.mainloop()
        return



if __name__ == "__main__":
    main()

import matplotlib as mpl
import numpy as np
import os
import pandas as pd
import matplotlib.pyplot as plt
import tkinter 

import datetime
import struct
import ftplib
import glob
import tempfile
import pymongo
import requests
import sys

import scipy.signal as signal
import scipy.io.wavfile
import pywt

from unophysics import ladc, wavefuncs
from pathlib import Path
from scipy.io import savemat
from sshtunnel import SSHTunnelForwarder

root = tkinter.Tk()
root.title('LADC-GEMM Interactive')
root.geometry('540x260')
root.grid_columnconfigure(1, minsize=135)

# SET UP INFORMATION PAGE FOR EACH LOCATION
localcalls = []
def info_location_change():
    currentlocation.set(ladc.Stuff.brydes_calls[info_location.get()]['Location'])
    locationlabel.grid(column=1, row=0, sticky=tkinter.N+tkinter.W)

    global localcalls
    localcalls = ladc.Stuff.brydes_calls[info_location.get()]['Call(s) recorded']
    numcallsstring = ', '.join(localcalls)
    current_numcalls.set(numcallsstring)
    numcalls_label.grid(column=1, row=0, sticky=tkinter.N+tkinter.W, pady=5)
    callmenu.delete(0, tkinter.END)
    for x in localcalls:
        callmenu.insert(tkinter.END, x)
    current_date.set(ladc.Stuff.brydes_calls[info_location.get()]['Date'])
    date_label.grid(column=1, row=0, sticky=tkinter.N+tkinter.W, pady=5)
    current_minmax.set('')

# LOCATION BUTTONS
infobutton_box = tkinter.LabelFrame(root)
info_location = tkinter.StringVar()
info_location.set('ETP')

currentlocation=tkinter.StringVar()
locationlabel = tkinter.Label(root, textvariable=currentlocation, font=('bold', 13))

etp = tkinter.Radiobutton(infobutton_box, text='Eastern Tropical Pacific', variable=info_location, value='ETP', command=info_location_change)
scarib = tkinter.Radiobutton(infobutton_box, text='Southern Caribbean', variable=info_location, value='SCaribbean', command=info_location_change)
nwpac = tkinter.Radiobutton(infobutton_box, text='Northwest Pacific', variable=info_location, value='NWPacific', command=info_location_change)
goc = tkinter.Radiobutton(infobutton_box, text='Gulf of California', variable=info_location, value='GoC', command=info_location_change)
cabo = tkinter.Radiobutton(infobutton_box, text='Cabo Frio, Brazil', variable=info_location, value='CaboFrio', command=info_location_change)
gom = tkinter.Radiobutton(infobutton_box, text='Gulf of Mexico', variable=info_location, value='GoM', command=info_location_change)

# REGIONAL CALL INFORMATION WIDGETS
numcallsbox = tkinter.LabelFrame(root)
numcalls = tkinter.Label(numcallsbox, text='Call(s) recorded: ')
current_numcalls = tkinter.StringVar()
numcalls_label = tkinter.Label(numcallsbox, textvariable=current_numcalls, wraplength=200, justify='left')

datebox = tkinter.LabelFrame(root)
date = tkinter.Label(datebox, text='Date: ')
current_date = tkinter.StringVar()
date_label = tkinter.Label(datebox, textvariable=current_date, wraplength=200, justify='left')

# FREQUENCY INFORMATION WIDGETS
freqbox = tkinter.LabelFrame(root)
freq = tkinter.Label(freqbox, text='Frequency information: ')

def change_facts(event):
    selecttuple = event.widget.curselection()
    selectindex = selecttuple[0]
    callname = localcalls[selectindex]
    minmaxrange = ladc.Stuff.frequency_info[info_location.get()][callname]
    minbookmark = minmaxrange[0]
    maxbookmark = minmaxrange[1]
    minmax_string = f'{minbookmark} - {maxbookmark} Hz'
    current_minmax.set(minmax_string) 

callbox = tkinter.Frame(freqbox)
call = tkinter.Label(callbox, text='Call: ')
callmenu = tkinter.Listbox(callbox, selectmode='SINGLE', height=6) 
callmenu.bind('<<ListboxSelect>>', change_facts)

minmaxbox = tkinter.Frame(freqbox)
minmax = tkinter.Label(minmaxbox, text='Min/max frequencies: ')
current_minmax = tkinter.StringVar()
minmax_label = tkinter.Label(minmaxbox, textvariable=current_minmax) 

# MENU WIDGET CHANGES
def datapage():
    reset_inputs()

    root.grid_columnconfigure(index=1, minsize=135)
    root.grid_rowconfigure(index=0, minsize=10)
    root.grid_rowconfigure(index=2, minsize=10)
    
    widgetlist = [minmax_label, callbox, minmaxbox, freqbox, freq, call, callmenu, minmax, infobutton_box, etp, scarib, nwpac, goc, cabo, gom, datebox, date, numcallsbox, numcalls, locationlabel, numcalls_label, date_label]
    for widget in widgetlist:
        widget.grid_remove()

    onefilename_box.grid(column=1, row=0, sticky=tkinter.W+tkinter.E, padx=10, pady=10)
    enter_onefile.grid(column=1, row=0, pady=5, padx=3)

    skipval_box.grid(column=2, row=0, sticky=tkinter.W+tkinter.E, padx=10, pady=10)
    enter_skipval.grid(column=2, row=0, pady=5, padx=3)

    cmap_box.grid(column=1, row=1, padx=10, pady=10, sticky=tkinter.E+tkinter.W)
    colorschemes.grid(column=1, row=1, sticky=tkinter.E+tkinter.W)

    fileamount_box.grid(column=2, row=1, padx=10, pady=10, sticky=tkinter.E+tkinter.W)
    fileamounts.grid(column=2, row=1, sticky=tkinter.E+tkinter.W)

    reset.grid(column=1, row=2, sticky=tkinter.E+tkinter.W, pady=10, padx=10)

    show_button.grid(column=2, row=2, sticky=tkinter.E+tkinter.W, padx=10, pady=10)

    databutton_box.grid(column=0, row=0, rowspan=4, padx=10, pady=10, sticky=tkinter.N+tkinter.S)
    spec_plot.grid(row=0, sticky=tkinter.W, pady=15, padx=5)
    amp_plot.grid(row=1, sticky=tkinter.W, pady=15, padx=5)
    search_interesting.grid(row=2, sticky=tkinter.W, pady=15, padx=5)

def infopage():
    info_location.set(None)

    root.grid_columnconfigure(index=1, minsize=330)
    root.grid_rowconfigure(index=0, minsize=30)
    root.grid_rowconfigure(index=2, minsize=20)

    widgetlist = [onefilename_box, enter_onefile, skipval_box, enter_skipval, cmap_box, colorschemes, fileamount_box, fileamounts, reset, show_button, databutton_box, spec_plot, amp_plot, search_interesting]
    for widget in widgetlist:
        widget.grid_remove()

    infobutton_box.grid(column=0, row=0, padx=10, pady=10, rowspan=6, sticky=tkinter.N+tkinter.S)

    etp.grid(column=0, row=0, sticky=tkinter.W, padx=10, pady=5)
    scarib.grid(column=0, row=1, sticky=tkinter.W, padx=10, pady=5)
    nwpac.grid(column=0, row=2, sticky=tkinter.W, padx=10, pady=5)
    goc.grid(column=0, row=3, sticky=tkinter.W, padx=10, pady=5)
    cabo.grid(column=0, row=4, sticky=tkinter.W, padx=10, pady=5)
    gom.grid(column=0, row=5, sticky=tkinter.W, padx=10, pady=5)

    numcallsbox.grid(column=1, row=1, columnspan=2, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S)
    numcalls.grid(column=0, row=0, sticky=tkinter.W+tkinter.N, padx=10, pady=5)
    datebox.grid(column=1, row=2, columnspan=2, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S)
    date.grid(column=0, row=0, sticky=tkinter.W+tkinter.N, padx=10, pady=5)

    freqbox.grid(column=1, row=3, columnspan=2, sticky=tkinter.W+tkinter.E+tkinter.N+tkinter.S)
    freq.grid(column=0, row=0)

    callbox.grid(column=0, row=1)
    call.grid(column=0, row=0)
    callmenu.grid(column=1, row=0)

    minmaxbox.grid(column=1, row=1)
    minmax.grid(column=0, row=0)
    minmax_label.grid(column=1, row=0)
    callmenu.delete(0, tkinter.END)
    current_minmax.set('')

# CREATING MENU
menu = tkinter.Menu(root)
root.config(menu=menu)
datamenu = tkinter.Menu(menu)
menu.add_cascade(label='Data', menu=datamenu)
datamenu.add_command(label='Data', command=datapage)
infomenu = tkinter.Menu(menu)
menu.add_cascade(label='Information', menu=infomenu)
infomenu.add_command(label='Information', command=infopage)

# TYPE IN FILE NAME
onefilename_box = tkinter.LabelFrame(root, text='Filename')
onefilename_box.grid(column=1, row=0, sticky=tkinter.W+tkinter.E, padx=10, pady=10)
onefilename = tkinter.StringVar()
onefilename.set('')
enter_onefile = tkinter.Entry(onefilename_box, textvariable=onefilename, width=16)
enter_onefile.grid(column=1, row=0, pady=5, padx=3)

# TYPE IN SKIP VALUE
def skip_error_check(number):
    valid = False
    if number.isdigit():
        if (int(number) <= 10000) and (int(number) >= 0):
            valid = True
    elif number == '':
        valid = True
    return valid
validate_skip = (root.register(skip_error_check), '%P')
skipval_box = tkinter.LabelFrame(root, text='Skip Value')
skipval_box.grid(column=2, row=0, sticky=tkinter.W+tkinter.E, padx=10, pady=10)
skipval = tkinter.StringVar()
skipval.set(0)
enter_skipval = tkinter.Spinbox(skipval_box, from_=0, to=10000, textvariable=skipval, width=16, validate='all', validatecommand=validate_skip)
enter_skipval.grid(column=2, row=0, pady=5, padx=3)

# OPTION MENUS
def show_options():
    global cmap_box, colorschemes, fileamount_box, fileamounts, fileamount_str, enter_onefile
    if current_page.get() == 'spec':
        enter_onefile.configure(state='normal')
        fileamounts.configure(state='disabled')
        colorschemes.configure(state='normal')
        colorscheme_str.set(cmaps[2])
        skipval.set(0)
        fileamount_str.set(number_of_files[0])
        onefilename.set('')
    else: 
        colorschemes.configure(state='disabled')
    
    if current_page.get() == 'amp':
        enter_onefile.configure(state='normal')
        fileamounts.configure(state='disabled')
        colorschemes.configure(state='disabled')
        skipval.set(0)
        fileamount_str.set(number_of_files[0])
        onefilename.set('')
    
    if current_page.get() == 'interesting':
        enter_onefile.configure(state='disabled')
        fileamounts.configure(state='normal')
        colorschemes.configure(state='disabled')
        skipval.set(0)
        fileamount_str.set(number_of_files[0])
    else:
        fileamounts.configure(state='disabled')

    if current_page.get() != 'spec' and current_page.get() != 'amp' and current_page.get() != 'interesting':
        enter_onefile.configure(state='disabled')
        fileamounts.configure(state='disabled')
        colorschemes.configure(state='disabled')
        enter_skipval.configure(state='disabled')
        reset.configure(state='disabled')
        show_button.configure(state='disabled')

cmaps = ['hsv', 'Greys', 'nipy_spectral']
cmap_box = tkinter.LabelFrame(root, text='Color Scheme')
colorscheme_str = tkinter.StringVar()
colorscheme_str.set(cmaps[2])
colorschemes = tkinter.OptionMenu(cmap_box, colorscheme_str, *cmaps)
cmap_box.grid(column=1, row=1, padx=10, pady=10, sticky=tkinter.E+tkinter.W)
colorschemes.grid(column=1, row=1, sticky=tkinter.E+tkinter.W)

number_of_files = ['4','9','16']
fileamount_box = tkinter.LabelFrame(root, text='Number of Files')
fileamount_str = tkinter.StringVar()
fileamount_str.set(number_of_files[0])
fileamounts = tkinter.OptionMenu(fileamount_box, fileamount_str, *number_of_files)
fileamount_box.grid(column=2, row=1, padx=10, pady=10, sticky=tkinter.E+tkinter.W)
fileamounts.grid(column=2, row=1, sticky=tkinter.E+tkinter.W)

# PLOT TYPE RADIOBUTTONS
# RADIOBUTTON LABELFRAME
databutton_box = tkinter.LabelFrame(root)
databutton_box.grid(column=0, row=0, rowspan=4, padx=10, pady=10, sticky=tkinter.N+tkinter.S)

current_page = tkinter.StringVar()
current_page.set(None)
spec_plot = tkinter.Radiobutton(databutton_box, text='Create Spectrogram', command=show_options, variable=current_page, value='spec')
spec_plot.grid(row=0, sticky=tkinter.W, pady=15, padx=5)

amp_plot = tkinter.Radiobutton(databutton_box, text='Create Time Series', command=show_options, variable=current_page, value='amp')
amp_plot.grid(row=1, sticky=tkinter.W, pady=15, padx=5)

search_interesting = tkinter.Radiobutton(databutton_box, text= 'Find Interesting', command=show_options, variable=current_page, value='interesting')
search_interesting.grid(row=2, sticky=tkinter.W, pady=15, padx=5)

# RESET BUTTON
def reset_inputs():
    global onefilename, skipval, current_page, cmap_box, colorschemes, fileamount_box, fileamounts, fileamount_str, colorscheme_str
    onefilename.set('')
    skipval.set(0)
    current_page.set(None)
    fileamount_str.set(number_of_files[0])
    colorscheme_str.set(cmaps[2])
    enter_onefile.configure(state='normal')
    fileamounts.configure(state='normal')
    colorschemes.configure(state='normal')

reset = tkinter.Button(root, text='Reset All', command=reset_inputs)
reset.grid(column=1, row=2, sticky=tkinter.E+tkinter.W, pady=10, padx=10)

# FORMAT USER INPUT FOR _ladc FUNCTIONS
trueskip = 0
truefilename = ''
fileamount_int = 0

def recordswindow(recordfn=None, recordskip=None, recordnumber=None):
    global trueskip, truefilename, fileamount_int

    recordswindow = tkinter.Toplevel(root)
    recordswindow.title('Records')
    recordswindow.geometry('630x300')

    truerecords = tkinter.StringVar()
    truerecords.set('')

    trueheader = tkinter.StringVar()
    trueheader.set('')

    recordlabel = tkinter.Label(recordswindow, textvariable=truerecords, wraplength=600, font=('bold', 12), justify='left')
    headerlabel = tkinter.Label(recordswindow, textvariable=trueheader, font=(6))
    
    if current_page.get() == 'spec' or current_page.get() == 'amp':
        if recordfn is None:
            if recordskip is None:
                detect = ladc.find()
            elif recordskip is not None:
                detect = ladc.find(skip=recordskip)
        elif recordfn is not None:
            detect = ladc.find(filename=recordfn)

        detectbookmark = str(detect)
        truerecords.set(detectbookmark)
        
        filenamebookmark = detect['filename']
        headerbookmark = (f'File {filenamebookmark} Records')
        trueheader.set(headerbookmark)

    if current_page.get() == 'interesting':
        if recordnumber is not None:
            truerecords.set(ladc.find_interesting(skip_start=recordskip, number_of_files=recordnumber, Type=6, Buoy='13', Disk='0'))
            trueheader.set('File Records')

    recordlabel.grid(column=0, row=1, sticky=tkinter.E+tkinter.W, padx=5, pady=5)
    headerlabel.grid(column=0, row=0, sticky=tkinter.N+tkinter.W, padx=5, pady=5)
    print('window')

# POPUP WINDOW
def build_plot(): 
    global trueskip, truefilename, fileamount_int
    print('built plot')

    truefilename = onefilename.get()
    if truefilename == '':
        truefilename = None
    
    fileamount_int = int(fileamount_str.get())

    trueskip = int(skipval.get())
    if trueskip == 0:
        trueskip = None

    if current_page.get() == 'spec' or current_page.get() == 'amp':
        if (trueskip is not None) and (truefilename is not None):
            errorwindow = tkinter.Toplevel(root)
            errorwindow.title('Error')
            errormessage = tkinter.Label(errorwindow, text='Please enter only a filename OR a skip value.')
            errormessage.grid(column=0, row=0, sticky=tkinter.E+tkinter.W, padx=10, pady=10)
            okbutton = tkinter.Button(errorwindow, text='Okay', command=errorwindow.destroy)
            okbutton.grid(column=0, row=1, sticky=tkinter.E+tkinter.W, padx=10, pady=10)
        else:
            try:
                recordswindow(recordfn=truefilename, recordskip=trueskip, recordnumber=None)
                if current_page.get() == 'spec': # use the output from the window building function instead of getting it from the widget
                    ladc.create_spec(skip=trueskip, cmap=(colorscheme_str.get()), figsize=(6,4), save_fig=None, show_plt=True, filename=truefilename)
                if current_page.get() == 'amp':
                    ladc.create_timeseries(filename=truefilename, skip=trueskip, show_plt=True)
            except FileNotFoundError:
                errorwindow = tkinter.Toplevel(root)
                errorwindow.title('Error')
                errormessage = tkinter.Label(errorwindow,text='Sorry, that file does not exist.')
                errormessage.grid(column=0, row=0, sticky=tkinter.E+tkinter.W, padx=10, pady=10)
                okbutton = tkinter.Button(errorwindow, text='Okay', command=errorwindow.destroy)
                okbutton.grid(column=0, row=1, sticky=tkinter.E+tkinter.W, padx=10, pady=10)

    if current_page.get() == 'interesting':
        recordswindow(recordfn=None, recordskip=trueskip, recordnumber=fileamount_int)
        ladc.find_interesting(skip_start=trueskip, number_of_files=fileamount_int, Type=6, Buoy='13', Disk='0')
        ladc.MATLAB_format(plot=True, show_plt=True, save_plt=False, clip_length=577, number_of_files=fileamount_int, directory='data', records=None, Type=6, Buoy='13', Disk='0', skip_start=trueskip)

show_button = tkinter.Button(root, text='Create Figure(s)', command=build_plot)
show_button.grid(column=2, row=2, sticky=tkinter.E+tkinter.W, padx=10, pady=10)

root.mainloop()
# -*- coding: utf-8 -*-

import requests

import struct
import datetime
import ftplib
import glob
import sys
import os
import tempfile
from sshtunnel import SSHTunnelForwarder
import pymongo

import numpy as np
try:
    import matplotlib as mpl 
    import matplotlib.pyplot as plt
except:
    print(f'Matplotlib not found')
    mpl = None
    plt = None
from . import wavefuncs
import scipy.signal as signal
import scipy.io.wavfile
import pywt
import pandas as pd

from pathlib import Path
from scipy.io import savemat

from . import config

__all__ = ['EARS', 'getEARSFileUNO', 'getEARSFileUL', 'searchEARS2017',
           'ladcMongoDB', 'get', 'search', 'find', 'Stuff', 'memOpen',
           'create_timeseries', 'create_spec', 'find_interesting', 'MATLAB_format']


class ladcMongoDB():
    
    def __init__(self):
        SERVER_HOST = config.server_mongo_uno.address
        SERVER_USER = config.server_mongo_uno.username
        SERVER_PASS = config.server_mongo_uno.password

        self.server = SSHTunnelForwarder(
            SERVER_HOST,
            ssh_username=SERVER_USER,
            ssh_password=SERVER_PASS,
            remote_bind_address=('127.0.0.1', 27017)
        )

        self.server.start()

        self.client = pymongo.MongoClient('127.0.0.1', self.server.local_bind_port) # server.local_bind_port is assigned local port
        self.db = self.client.ladc

    def __enter__(self):
        return self.db
    
    def close(self):
        self.client.close()
        self.server.close()
        
    def __exit__(self, type, value, tb):
        self.close()

class Stuff(object):
    uno_filter = {
                'Buoy': {'$in': ['12', '13', '16', '18', '19', '21']},
                'Disk': '0',
                }

    brydes_calls = {
                    'ETP' : { 
                    'Location':'Eastern Tropical Pacific','Call(s) recorded':['Be1', 'Be2', 'Be3','Be4','Be5','Be6'],
                    'Date':'1999 - 2000'
                    }, 
                    
                    'SCaribbean': {
                    'Location':'Southern Caribbean','Call(s) recorded':['Be7'], 
                    'Date':'February 2000 - March 2000'
                    },
                    
                    'NWPacific': {
                    'Location':'Northwest Pacific','Call(s) recorded':['Be8a', 'Be8b'], 
                    'Date':'Precise date unknown. Recorded "between June and August."'
                    },
                    
                    'GoC' : {
                    'Location':'Gulf of California','Call(s) recorded':['Be10','Be11','Be12,','Be4'],
                    'Date':'1983 - 1986'
                    },
                    
                    'CaboFrio' : {
                    'Location':'Cabo Frio, Brazil','Call(s) recorded':['PSI','LFT','FMT','TM1','TM2'],
                    'Date': 'December 2010 - November 2012'
                    }, 

                    'GoM' : {
                    'Location':'Gulf of Mexico','Call(s) recorded':['Stranded calf', '"Long moans"', '"Downsweep sequences"', '"Tonal sequences"'],
                    'Date': '1988 - 1989 and 2010' 
                    }
                    }  

    # frequency ranges (Be calls) from Rice et al. "Potential Bryde's whale (Balaenoptera edeni) 
    # calls recorded in the northern Gulf of Mexico", add doi numbers
    # except for GoC (Viloria-Gomore et al.)
    frequency_info = { 
                    'ETP' : { 
                    'Be1':(20,23), 'Be2':(35.7,38.2), 'Be3':(2.44,26.9), 'Be4':(59.5,60.2), 'Be5':(26.0,26.8), 'Be6':(57.1,232.7)
                    }, 
                    
                    'SCaribbean': {
                    'Be7':(43.7,48.7)
                    },
                    
                    'NWPacific': {
                    'Be8a':(43.0,48.0), 'Be8b':(137,192)
                    },
                    
                    'GoC' : {
                    'Be10':(79,152), 'Be11':(111,247), 'Be12':(93,145), 'Free-range feeding study':(165,875), 'Calves':(700,900)
                    },
                    
                    'CaboFrio' : {
                    'PSI':(175,674), 'LFT':(7.57,20.39), 'FMT':(336,915), 'TM1':(85.7,123.6), 'TM2':(96,np.nan)
                    },

                    'GoM' : {
                    'Stranded calf':(200,900), '"Long moans"':(43,208), '"Down-sweep sequences"':(51,113), '"Tonal sequences"':(103,103)
                    }
                    } 

def find(skip=0, use_filter=True, **kwargs):
    ''' Find using Mongo object. 
        defaults to use UNO filter for available data in 2017
    '''
    with ladcMongoDB() as db:
        filt = {}
        if use_filter:
            filt = Stuff.uno_filter
        for k in kwargs:
            filt[k] = kwargs[k]
        d = db.detects_2017.find_one(filt, skip=skip)
        return d
'''
*****
EARS file Classes
*****
'''


class EARS():
    default_fn = r'../data/raw/5234C8C9.021'
    recN = 512
    headerN = 12
    epochs = {'2015': (2000, 1, 1), '2017': (2015, 10, 27)}
    fs = 192000
    fs_time = 32000

    def __init__(self, fn=None, epoch=None, year='2017'):
        self.data = []
        self.headers = []
        self.timestamps = []
        if fn is None:
            self.filename = self.default_fn
        else:
            self.filename = fn
        if year is not None:
            self.year = year
        else:
            if os.path.basename(self.filename)[0]=='7':
                self.year = '2017'
            else:
                self.year = '2015'
        if epoch is not None:
            self.epoch = epoch
        else:
            self.epoch = self.epochs.get(self.year, self.epochs['2015'])
        self.load(self.filename)

    def load(self, fn=None):
        if fn is not None:
            self.filename = fn
        with open(self.filename, 'rb') as f:
            d = f.read()
        data = []
        headers = []
        timestamps = []
        dataN = int(len(d) / self.recN)
        for i in range(dataN):
            data.extend(
                struct.unpack_from(
                    '>250h', d, offset=self.headerN + self.recN * i))
            if i == 0 or headers[-1] != d[0:self.headerN]:
                h = d[0:self.headerN]
                headers.append(h)
                timestamps.append(self.header2timestamp(h))
        self.time_0 = timestamps[0]
        self.time_f = self.time_0 + datetime.timedelta(
            seconds=len(data) / self.fs)
        self.timestamps = timestamps
        self.headers = headers
        self.data = data

    def header2timestamp(self, h):
        s = struct.unpack('6x6B', h)
        timestampSeconds = ((
            (s[0] - 14) / 16) * 2**40 + s[1] * 2**32 + s[2] * 2**24 +
                            s[3] * 2**16 + s[4] * 2**8 + s[5] * 2**0) / self.fs_time
        return (datetime.timedelta(seconds=timestampSeconds) +
                datetime.datetime(*self.epoch))

def getEARSFileUNO(fn=None, outDir='', warnings=False, directory=None):
    if not fn:
        return None
    try:
        if not directory:
            Buoy = int(fn[-3:][:2])
            Disk = int(fn[-3:][2:])
            directory = 'Buoy{:0>2d}{:0>1d}'.format(Buoy, Disk)
        ftp = ftplib.FTP(config.server_ftp_uno.address)
        ftp.login(user=config.server_ftp_uno.username, passwd=config.server_ftp_uno.password)
        
        ftp.cwd(directory)
        #print(directory)
        fn_out = os.path.join(outDir, fn)
        response = ftp.retrbinary('RETR {}'.format(fn),
                                  open(fn_out, 'wb').write)
        #print(response)
        ftp.close()
        return fn_out
    except Exception as e:
        if warnings:
            print(f'Problem getting {fn} Error: {str(e)}')
        return None


def getEARSFileUL(fn=None, outDir='', warnings=False):
    if not fn:
        return None
    try:
        Buoy = int(fn[-3:][:2])
        Disk = int(fn[-3:][2:])
        ftp = ftplib.FTP(config.server_ftp_ull.address)
        ftp.login(user=config.server_ftp_ull.username, passwd=config.server_ftp_ull.password)
        if Buoy < 6:
            directory = '/Volumes/FirstRAID/'
        elif Buoy == 6 and Disk == 1:
            directory = '/Volumes/FirstRAID/'
        elif Buoy == 6 and Disk == 0:
            directory = '/Volumes/FirstRAID/'
        else:
            directory = '/Volumes/SecondRAID/'
        directory += 'Buoy{:0>2d}_DISK{:0>1d}'.format(Buoy, Disk)
        ftp.cwd(directory)
        #print(directory)
        fn_out = os.path.join(outDir, fn)
        response = ftp.retrbinary('RETR {}'.format(fn),
                                  open(fn_out, 'wb').write)
        #print(response)
        ftp.close()
        return fn_out
    except Exception as e:
        if warnings:
            print(f'Problem getting {fn} Error: {str(e)}')
        return None

def searchEARS2017(searchData={}):
    searchJson = {k: str(v) for k,v in searchData.items()}
    r = requests.post(config.server_api_uno.address, json=searchJson)
    return r.json()

def search(searchData={}, year='2017'):
    ''' Search using requests api. '''
    if year=='2015':
        return searchEARS2015(searchData=searchData)
    if year=='2017':
        return searchEARS2017(searchData=searchData)
        

def get(fn=None, outDir='', warnings=True, directory=None):
    '''Gets a file, returns filename, else returns None'''
    if directory:
        return getEARSFileUNO(fn=fn, outDir=outDir, warnings=warnings, directory=directory)
    if not fn:
        fn = '5176009D.010'
    try:
        if fn[0]=='7':
            return getEARSFileUNO(fn=fn, outDir=outDir, warnings=warnings)
        elif fn[0]=='5':
            return getEARSFileUL(fn=fn, outDir=outDir, warnings=warnings)
        else:
            return None
    except Exception as e:
        if warnings:
            print(f'Problem getting {fn} Error: {str(e)}')
        return None

def memOpen(fn, warnings=True, directory=None):
    '''Gets file from network and returns EARS object, does not write to storage.'''
    with tempfile.TemporaryDirectory() as tmpdirname:
        fni = get(fn, outDir=tmpdirname, warnings=warnings, directory=directory)
        return EARS(fni)

def create_timeseries(filename=None, skip=None, show_plt=True):
    if filename is None:
        if skip is None:
            detect = find()
        elif skip is not None:
            detect = find(skip=skip)
        if detect is None:
            return False
        filename = detect['filename']
        b = EARS(fn=get(filename))
        timestamp = b.time_0
        plt.plot(b.data)
        plt.title(f'File {filename} - Recorded {timestamp}')
        if show_plt == True:
            plt.show()

def create_spec(skip=None, cmap='nipy_spectral', figsize=(6,4), save_fig=None, show_plt=True, filename=None, downloadname=None): 
    if filename is None:
        if skip is None:
            detect = find()
        elif skip is not None:
            detect = find(skip=skip)
        if detect is None:
            return False
        filename = detect['filename']
        b = EARS(fn=get(filename))
    elif filename is not None:
        b = EARS(fn=get(filename))
    timestamp = b.time_0
    fig, axes = plt.subplots(1,1,figsize=figsize)
    f, t, Sxx = signal.spectrogram(wavefuncs.wave_clean(b.data), b.fs, window='hann')
    axes.set_ylabel('Frequency [Hz]')
    axes.set_xlabel('Time [sec]')
    plt.tight_layout()
    plt.title(f'File {filename} - Recorded {timestamp}')
    axes.pcolormesh(t, f, 10*np.log10(Sxx), cmap=cmap)
    if show_plt == True:
        fig.show()
    if save_fig is not None:
        naming = downloadname
        getdir = os.getcwd()
        newfilename = (f'{getdir}\\{naming}')
        plt.savefig(newfilename)
        return filename
    else:
        if save_fig is None:
            return None

def find_interesting(skip_start=0, number_of_files=9, Type=6, Buoy='13', Disk='0'): 
    # change skip_start number to get a new set
    # keep number of files square to make plotting below work smoothly
    records = []
    with ladcMongoDB() as db:
        to_find = {
                'type': Type,  # type 6 is the highest frequency band ULL looked for
                'Buoy': Buoy,  # 13 is one of the buoys we have here at UNO and...
                'Disk': Disk  # disk 0 is one we have locally
                }
        cursor = db.detects_2017.find(to_find, skip=skip_start)
        '''found = cursor.count()
        if found < number_of_files:
            number_of_files = found'''
        for i in range(number_of_files):
            records.append(cursor.next())
    return records

def MATLAB_format(plot=True, show_plt=False, save_plt=True, clip_length=577, number_of_files=9, skip_start=0, directory='data', records=None, Type=6, Buoy='13', Disk='0'):
    save_folder = Path(directory)
    save_folder.mkdir(exist_ok=True)
    if plot:
        size_of_plots = int(round(np.sqrt(number_of_files)))
        fig, ax = plt.subplots(size_of_plots, size_of_plots, figsize=(16, 16))
        axF = ax.reshape(-1)
    clips = []
    if records is None:
        records = find_interesting(number_of_files=number_of_files, skip_start=skip_start, Type=Type, Buoy=Buoy, Disk=Disk)
    for i, record in enumerate(records):
        e = memOpen(record['filename'])
        start_n = record['startRecord'] * 250
        clipped = e.data[start_n:start_n + clip_length]
        savemat(str(save_folder.joinpath(f'click{i}.mat')), {'data': clipped, **record})
        clips.append(clipped)
        if plot:
            axF[i].plot(clipped)
    if plot:
        if save_plt:
            plt.savefig(str(save_folder.joinpath('clips.jpg')))
        if show_plt:
            plt.show()
        else:
            plt.close()
    clips_dictionary = {f'click{i}_data': c for i, c in enumerate(clips)}
    clips_dictionary['records'] = records
    savemat(str(save_folder.joinpath(f'ALL_clicks.mat')), clips_dictionary)
    savemat(str(save_folder.joinpath(f'ALL_clicksMAT.mat')), {'clips': clips})
# -*- coding: utf-8 -*-

import requests

import struct
import datetime
import ftplib
import glob
import sys
import os
from sshtunnel import SSHTunnelForwarder
import pymongo

__all__ = ['EARS', 'getEARSFileUNO', 'getEARSFileUL', 'searchEARS2017',
           'ladcMongoDB', 'get', 'search', 'find', 'Stuff']


class ladcMongoDB():
    
    def __init__(self):
        SERVER_HOST = "***REMOVED***"
        SERVER_USER = "***REMOVED***"
        SERVER_PASS = "***REMOVED***"

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
EARS Class
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
        ftp = ftplib.FTP('ftp.***REMOVED***')
        ftp.login(user='***REMOVED***', passwd='***REMOVED***')
        
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
        ftp = ftplib.FTP('***REMOVED***')
        ftp.login(user='***REMOVED***', passwd='***REMOVED***')
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
    r = requests.post('http://matlab.***REMOVED***/ull_detection_2017_available_data', json=searchJson)
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
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
           'ladcMongoDB', 'get', 'search']


class ladcMongoDB():
    
    def __init__(self):
        SERVER_HOST = "uno.colorsynth.systems"
        SERVER_USER = "joseph"
        SERVER_PASS = "fourier"

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

'''
*****
EARS Class
*****
'''


class EARS():
    default_fn = r'../data/raw/5234C8C9.021'
    recN = 512
    headerN = 12
    epoch = (2017, 1, 1)
    fs = 192000

    def __init__(self, fn=None, epoch=None):
        self.data = []
        self.headers = []
        self.timestamps = []
        if fn is None:
            self.filename = self.default_fn
        else:
            self.filename = fn
        if epoch is not None:
            self.epoch = epoch
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
                            s[3] * 2**16 + s[4] * 2**8 + s[5] * 2**0) / self.fs
        return (datetime.timedelta(seconds=timestampSeconds) +
                datetime.datetime(*self.epoch))

def getEARSFileUNO(fn=None, outDir=''):
    if fn is None:
        fn = '5176009D.010'
    try:
        Buoy = int(fn[-3:][:2])
        Disk = int(fn[-3:][2:])
        ftp = ftplib.FTP('ftp.uno.colorsynth.systems')
        ftp.login(user='joseph', passwd='fourier')
        directory = 'Buoy{:0>2d}{:0>1d}'.format(Buoy, Disk)
        ftp.cwd(directory)
        print(directory)
        fn_out = os.path.join(outDir, fn)
        response = ftp.retrbinary('RETR {}'.format(fn),
                                  open(fn_out, 'wb').write)
        print(response)
        ftp.close()
        return fn_out
    except Exception as e:
        print(e)
        return False


def getEARSFileUL(fn=None, outDir=''):
    if fn is None:
        fn = '5176009D.010'
    try:
        Buoy = int(fn[-3:][:2])
        Disk = int(fn[-3:][2:])
        ftp = ftplib.FTP('phys-ladc-store.louisiana.edu')
        ftp.login(user='ul-phys-user', passwd='uluser.ftp')
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
        print(directory)
        fn_out = os.path.join(outDir, fn)
        response = ftp.retrbinary('RETR {}'.format(fn),
                                  open(fn_out, 'wb').write)
        print(response)
        ftp.close()
        return fn_out
    except Exception as e:
        print(e)
        return False

def searchEARS2017(searchData={}):
    searchJson = {k: str(v) for k,v in searchData.items()}
    r = requests.post('http://matlab.uno.colorsynth.systems/ull_detection_2017_available_data', json=searchJson)
    return r.json()

def search(searchData={}, year='2015'):
    if year=='2015':
        return searchEARS2015(searchData=searchData)
    if year=='2017':
        return searchEARS2017(searchData=searchData)
        

def get(fn=None, outDir=''):
    if fn[0]=='7':
        return getEARSFileUNO(fn=fn, outDir=outDir)
    elif fn[0]=='5':
        return getEARSFileUL(fn=fn, outDir=outDir)
# -*- coding: utf-8 -*-
"""Main module."""

import struct
import datetime
import ftplib
import glob
import sys
import os
'''
*****
EARS Class
*****
'''


class EARS():
    default_fn = r'../data/raw/5234C8C9.021'
    recN = 512
    headerN = 12
    epoch = (2000, 1, 1)
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
        return True
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
        return True
    except Exception as e:
        print(e)
        return False

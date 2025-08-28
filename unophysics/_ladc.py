import struct
import datetime
import os
from dataclasses import dataclass
from typing import List
from numbers import Number

# import numpy as np
# import matplotlib as mpl
# import matplotlib.pyplot as plt
# import scipy.signal as signal

from pathlib import Path

__all__ = [
    "EARS",
]

"""
*****
EARS file Classes
*****
"""


@dataclass
class EARS_data:
    data: List[Number]
    headers: List[bytes]
    timestamps: List[datetime.datetime]
    time_0: datetime.datetime
    time_f: datetime.datetime
    filename: Path
    year: str
    epoch: tuple
    norm: bool
    fs: int
    fs_time: int
    recN: int
    headerN: int


@dataclass
class EARS:
    default_fn = Path("sample_data") / Path("71621DC7.190")
    recN = 512
    headerN = 12
    epochs = {"2015": (2000, 1, 1), "2017": (2015, 10, 27)}
    fs = 192000
    fs_time = 32000

    def __repr__(self):
        return f"EARS file: {self.filename} - {self.year} - {self.epoch}"

    def __init__(self, fn=None, epoch=None, year=None, norm=False):
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
            if os.path.basename(self.filename)[0] == "7":
                self.year = "2017"
            else:
                self.year = "2015"
        if epoch is not None:
            self.epoch = epoch
        else:
            self.epoch = self.epochs.get(self.year, self.epochs["2015"])
        self.norm = norm
        self.load(self.filename)

    def load(self, fn=None):
        if fn is not None:
            self.filename = fn
        with open(self.filename, "rb") as f:
            d = f.read()
        data = []
        headers = []
        timestamps = []
        dataN = int(len(d) / self.recN)
        x = 0
        for i in range(dataN):
            if i > 50:
                pass  # exit()
            data.extend(
                struct.unpack_from(">250h", d, offset=self.headerN + self.recN * i)
            )
            header = struct.unpack_from(">16H", d, offset=self.recN * i)
            headers.append(header)
            # print(f"Length of header: {len(header)}")
            # print(f"i: {i} Header: {headers[-1]}")
            a = d[self.recN * i : self.recN * (i + 1)]
            # print(a)
            aa = struct.unpack_from(">16H", a)
            # print(f"{aa[5]}: {aa[5] - x}")
            xx = (aa[5]) + (aa[4] ** 8)
            # print(xx - x)
            if xx - x > 50:
                print(aa)
                print(struct.unpack_from(">32B", a))
            x = xx
            # print(aa)
            # print("".join([f"{aaa:#08b}"[2:].zfill(8) for aaa in aa]))
            # aa = struct.unpack_from("<16B", a)
            # print("".join([f"{aaa:#08b}"[2:].zfill(8) for aaa in aa]), "\n*****")

            # print(a[7])
            # print(a[8])
            dd = self.decode_ears_timestamp(header)
            # print(dd)
            # print()
            # timestamps.append(self.header2timestamp(header))

        self.time_0 = timestamps[0]
        self.time_f = self.time_0 + datetime.timedelta(seconds=len(data) / self.fs)
        self.timestamps = timestamps
        self.headers = headers
        self.data = data

    def decode_ears_timestamp(self, header):
        """Decodes a 16-byte EARS header, discarding the first four bytes,
        and extracts the timestamp from the remaining 12 bytes.

        Args:
            header: bytes object containing the 16-byte header.

        Returns:
            datetime object representing the timestamp.
        """

        # Discard the first four bytes
        # header = header[4:]

        # Decode timestamp from the remaining 12 bytes
        print("Header: ", header)
        print(header[3])
        dum = (header[3] >> 8) << 8  # Clear low bits of byte 7 (now index 6)

        print(dum)
        dum = dum ^ 0xFF  # Bitwise complement
        print(dum)
        a = dum  # & header[3]
        print(a)
        timecode = (
            1  # a**16
            + header[4]
            + header[5]
            # + header[5] ** 24
            # + header[6] ** 16
            # + header[7] ** 8
            # header[2]
            # + (header[3] << 8)
            # + (header[4] << 16)
            # + (header[5] << 24)
            # + (header[6] << 40)
            # + (a << 32)
        )

        timecode = timecode  # / 32000.0  # Convert to seconds
        return timecode
        # Calculate datetime object
        seconds_since_epoch = (
            timecode + 946684800
        )  # Add seconds from 2000-01-01 to epoch
        return datetime.datetime.fromtimestamp(seconds_since_epoch)

    def header2timestamp(self, h):
        s = struct.unpack("7x5B", h)
        # print(s)
        timestampSeconds = (
            ((s[0] - 14) / 16) * 2**40
            + s[1] * 2**32
            + s[2] * 2**24
            + s[3] * 2**16
            + s[4] * 2**8
            + s[5] * 2**0
        ) / self.fs_time
        print(f"\n\nTimestamp second: {timestampSeconds}")
        return datetime.timedelta(seconds=timestampSeconds) + datetime.datetime(
            *self.epoch
        )

import struct
import datetime
import os
from dataclasses import dataclass, field
from typing import List, Dict
from numbers import Number
from pathlib import Path


@dataclass
class EARS:
    filename: Path = field(
        default_factory=lambda: Path("sample_data") / Path("71621DC7.190")
    )
    recN: int = 512
    headerN: int = 12
    epochs: Dict = field(
        default_factory=lambda: {"2015": (2000, 1, 1), "2017": (2015, 10, 27)}
    )
    fs: int = 192000
    fs_time: int = 32000
    data: List[Number] = field(default_factory=lambda: [])
    headers: List[bytes] = field(default_factory=lambda: [])
    timestamps: List[datetime.datetime] = field(default_factory=lambda: [])
    year: str = field(default_factory=lambda: "")
    epoch: tuple = field(default_factory=lambda: (2000, 1, 1))
    norm: bool = False

    # def __post_init__(self):
    #     if self.year != "":
    #         if os.path.basename(self.filename)[0] == "7":
    #             self.year = "2017"
    #         else:
    #             self.year = "2015"
    #     # self.load(self.filename)

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
            a = d[self.recN * i : self.recN * (i + 1)]
            aa = struct.unpack_from(">16H", a)
            xx = (aa[5]) + (aa[4] ** 8)
            x = xx
            dd = self.decode_ears_timestamp(header)

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
        dum = (header[3] >> 8) << 8  # Clear low bits of byte 7 (now index 6)

        dum = dum ^ 0xFF  # Bitwise complement
        a = dum  # & header[3]
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
        timestampSeconds = (
            ((s[0] - 14) / 16) * 2**40
            + s[1] * 2**32
            + s[2] * 2**24
            + s[3] * 2**16
            + s[4] * 2**8
            + s[5] * 2**0
        ) / self.fs_time
        return datetime.timedelta(seconds=timestampSeconds) + datetime.datetime(
            *self.epoch
        )

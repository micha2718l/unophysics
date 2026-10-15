import struct
import datetime
from pathlib import Path

import numpy as np


# Fast, modern EARS file loader class
class EARSFile:
    recN = 512
    headerN = 12
    fs = 192000
    fs_time = 32000
    epochs = {"2015": (2000, 1, 1), "2017": (2015, 10, 27)}

    def __init__(self, filename, norm=False):
        self.filename = filename
        self.norm = norm
        self.year = self._infer_year()
        self.epoch = self.epochs.get(self.year, self.epochs["2015"])
        self.data = None
        self.headers = []
        self.timestamps = []
        self.time_0 = None
        self.time_f = None
        self.load()

    def _infer_year(self):
        fn = Path(self.filename)
        if fn.name[0] == "7":
            return "2017"
        else:
            return "2015"

    def load(self):
        with open(self.filename, "rb") as f:
            d = f.read()
        dataN = int(len(d) / self.recN)
        # Read all data at once, skipping headers
        raw = np.frombuffer(d, dtype=">i2")  # big-endian int16
        # Each record: headerN bytes header, then 250 samples (500 bytes)
        samples_per_record = 250
        total_samples = dataN * samples_per_record
        # Extract data samples
        data = np.empty(total_samples, dtype=np.int16)
        for i in range(dataN):
            start = self.recN * i + self.headerN
            end = start + samples_per_record * 2
            data[i * samples_per_record : (i + 1) * samples_per_record] = np.frombuffer(
                d[start:end], dtype=">i2"
            )
            if i == 0 or (
                self.headers
                and d[self.recN * i : self.recN * i + self.headerN] != self.headers[-1]
            ):
                h = d[self.recN * i : self.recN * i + self.headerN]
                self.headers.append(h)
                self.timestamps.append(self.header2timestamp(h))
        self.data = data.astype(np.float32)
        if self.norm:
            self.data -= np.mean(self.data)
            maxabs = np.max(np.abs(self.data))
            if maxabs > 0:
                self.data /= maxabs
        self.time_0 = self.timestamps[0] if self.timestamps else None
        self.time_f = (
            (self.time_0 + datetime.timedelta(seconds=len(self.data) / self.fs))
            if self.time_0
            else None
        )

    def header2timestamp(self, h):
        s = struct.unpack("6x6B", h)
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

    @property
    def sampling_rate(self):
        return self.fs

    def audio_data(self):
        """Return data normalized to [-1, 1] float32 for audio playback."""
        d = self.data.astype(np.float32)
        maxabs = np.max(np.abs(d))
        if maxabs > 0:
            d = d / maxabs
        return d

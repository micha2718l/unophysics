import code
from pprint import pprint as pp
import struct
from datetime import datetime

from matplotlib import pyplot as plt
from ear import EARS

# f = "/Users/mjhaas/data/Buoy180_100000_100099/718585BD.180"
f = "/Users/mjhaas/data/Buoy180_100200_100299/718587B4.180"
f = "/Users/mjhaas/data/Buoy180_100300_100399/71858826.180"

fs_timestamp = 32000
epoch = datetime(2015, 10, 27)
formats = {"header": ">12B", "data": ">250h"}
Ns = {"header": 12, "record": 250}
with open(f, "rb") as f:
    d = f.read()

data = []
dates = []
for i in range(len(d) // Ns["record"]):
    record = d[Ns["record"] * i : Ns["record"] * (i + 1)]

    header = struct.unpack_from(formats["header"], record)
    timestamp = (
        header[11]
        + header[10] * (2**8)
        + header[9] * (2**16)
        + header[8] * (2**24)
        + header[7] * (2**32)
        + (header[6] & 0b00001111) * (2**36)
    ) / fs_timestamp
    date = datetime.fromtimestamp(timestamp + epoch.timestamp())
    dates.append(date)

    data.extend(struct.unpack_from(formats["data"], record, offset=Ns["header"]))

import code

code.interact(local={**locals(), **globals()})

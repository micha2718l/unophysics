from unophysics import ladc
import pytest
import datetime
from pathlib import Path

class TestEARS:

    fn2017 = Path('sample_data') / Path('71621DC7.190')

    def test_EARS_datetime(self):
        e = ladc.EARS(self.fn2017)
        assert isinstance(e.time_0, datetime.datetime), 'Should be datetime object.'

    def test_EARS_fs_2017(self):
        e = ladc.EARS(self.fn2017)
        assert e.fs == 192_000, 'Sampling frequency for 2017 data should be 192,000'
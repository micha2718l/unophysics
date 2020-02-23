from unophysics import ladc
import pytest
import datetime
from pathlib import Path
from numpy.testing import assert_almost_equal
import numpy as np

class TestEARS:

    fn2017 = Path('sample_data') / Path('71621DC7.190')

    def test_EARS_datetime(self):
        e = ladc.EARS(self.fn2017)
        assert isinstance(e.time_0, datetime.datetime), 'Should be datetime object.'

    def test_EARS_fs_2017(self):
        e = ladc.EARS(self.fn2017)
        assert e.fs == 192_000, 'Sampling frequency for 2017 data should be 192,000'

    def test_EARS_normalized(self):
        e = ladc.EARS(self.fn2017, norm=True)
        assert np.max(e.data) <= 1, 'Max should be <= 1'
        assert np.min(e.data) >= -1, 'Min should be >= -1'
        mean = np.mean(e.data)
        assert_almost_equal(mean, 0, err_msg='Mean should be ~0')
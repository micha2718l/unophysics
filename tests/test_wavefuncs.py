from unophysics import ladc
from unophysics import wavefuncs

import pytest

from numpy.testing import assert_almost_equal
import numpy as np

class TestWaveClean:
    e = ladc.EARS()
    def test_wave_clean_defaults_CorrectType(self):
        
        cleaned = wavefuncs.wave_clean(self.e.data)
        assert isinstance(cleaned, np.ndarray), 'Should be ndarray'
    
    def test_wave_clean_return_threshold(self):
        cleaned, thresh = wavefuncs.wave_clean(self.e.data, ret_thresh=True)
        assert isinstance(thresh, np.float64), 'Threshold should be numpy.float64'

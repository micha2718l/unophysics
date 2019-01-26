import numpy as np
import pywt

__all__ = ['threshold', 'thresh_wave_coeffs', 'threshold']

default_wavelet = 'db20'
default_thresh = 50

def threshold(x_in, delta=default_thresh, hard=False):
    x_thresh_indicies = np.abs(x_in) < delta
    if not hard:     
        x_in = np.sign(x_in)*(np.abs(x_in) - delta)
    x_in[x_thresh_indicies] = 0
    return x_in

def thresh_wave_coeffs(d_w, delta=default_thresh):
    d_w_out = [np.asarray(threshold(d, delta = delta, hard=False)) for d in d_w]
    return d_w_out


def wave_clean(data, wavelet=None, wavelet_thresh = default_thresh):
    if not wavelet:
        wavelet = default_wavelet
    d_w = pywt.wavedec(data, wavelet)
    d_w_t = thresh_wave_coeffs(d_w, delta=wavelet_thresh)
    clean = pywt.waverec(d_w_t, wavelet)
    return clean
import numpy as np
import pywt

__all__ = ['threshold', 'thresh_wave_coeffs', 'wave_clean']

default_wavelet = 'db20'
default_thresh = 50

def threshold(x_in, delta=default_thresh, hard=False):
    x_thresh_indicies = np.abs(x_in) < delta
    if not hard:     
        x_in = np.sign(x_in)*(np.abs(x_in) - delta)
    x_in[x_thresh_indicies] = 0
    return x_in

def thresh_wave_coeffs(d_w, delta=default_thresh, hard=False):
    d_w_out = [np.asarray(threshold(d, delta = delta, hard=hard)) for d in d_w]
    return d_w_out


def wave_clean(data, wavelet=None, wavelet_thresh=None, ret_thresh=False, hard=False):
    if wavelet is None:
        wavelet = default_wavelet
    data = np.asarray(data)
    data = data - data.mean()
    d_w = pywt.wavedec(data, wavelet)
    if wavelet_thresh is None:
        #coeffs = pywt.dwtn(e.data, wavelet='db2')
        detail_coeffs = d_w[-1]
        denom = 0.6744897501960817
        sigma = np.median(np.abs(detail_coeffs)) / denom
        wavelet_thresh = sigma*np.sqrt(2*np.log(len(data)))
    d_w_t = thresh_wave_coeffs(d_w, delta=wavelet_thresh, hard=hard)
    clean = pywt.waverec(d_w_t, wavelet)
    if ret_thresh:
        return clean, wavelet_thresh
    return clean
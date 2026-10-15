import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import butter, filtfilt, hilbert, find_peaks, stft
from EARSFile import EARSFile


def bandpass(data, fs, low, high, order=4):
    nyq = 0.5 * fs
    if high >= nyq:
        high = nyq - 1000
    b, a = butter(order, [low / nyq, high / nyq], btype="band")
    return filtfilt(b, a, data)


def moving_threshold(signal, window_size, n_std=6):
    pad = window_size // 2
    padded = np.pad(signal, (pad, pad), mode="reflect")
    cumsum = np.cumsum(padded)
    cumsum2 = np.cumsum(padded**2)
    means = (cumsum[window_size:] - cumsum[:-window_size]) / window_size
    sq_means = (cumsum2[window_size:] - cumsum2[:-window_size]) / window_size
    stds = np.sqrt(sq_means - means**2)
    return means + n_std * stds


# --- Main detection logic ---
fn = "../sample_data/71621DC7.190"
e = EARSFile(fn)

filtered = bandpass(e.audio_data(), e.sampling_rate, 20000, 90000)
analytic = hilbert(filtered)
envelope = np.abs(analytic)

window_ms = 50
window_size = int(window_ms * 1e-3 * e.sampling_rate)
if window_size < 1:
    window_size = 1
local_thresh = moving_threshold(envelope, window_size, n_std=6)
local_thresh = np.concatenate(
    [
        np.full(window_size // 2, local_thresh[0]),
        local_thresh,
        np.full(window_size // 2, local_thresh[-1]),
    ]
)[: len(envelope)]

min_dist = int(0.001 * e.sampling_rate)
peaks, props = find_peaks(envelope, height=local_thresh, distance=min_dist)

times = np.arange(len(e.data)) / e.sampling_rate

# --- Interactive plot ---
plt.ion()
fig, ax = plt.subplots(figsize=(16, 4))
ax.plot(times, e.data, linewidth=0.5, label="Waveform")
ax.plot(
    times,
    envelope * np.max(np.abs(e.data)) / np.max(envelope),
    alpha=0.5,
    label="Envelope",
)
ax.scatter(
    times[peaks], e.data[peaks], color="red", marker="o", label="Detected Clicks"
)
ax.set_title("Interactive Waveform with Detected Dolphin Clicks")
ax.set_xlabel("Time (seconds)")
ax.set_ylabel("Amplitude")
ax.legend()
plt.tight_layout()
plt.show()
input("Press Enter to continue and see the STFT plot...")

# --- STFT plot ---
f, t, Zxx = stft(e.audio_data(), fs=e.sampling_rate, nperseg=1024, noverlap=512)
plt.ioff()
plt.figure(figsize=(16, 6))
plt.pcolormesh(t, f, np.abs(Zxx), shading="gouraud")
plt.title("Short-Time Fourier Transform (STFT) Magnitude")
plt.ylabel("Frequency [Hz]")
plt.xlabel("Time [sec]")
plt.colorbar(label="Magnitude")
plt.ylim(0, 120000)
plt.tight_layout()
plt.show()

# Optionally, you could add a wavelet decomposition plot here as well.

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from EARSFile import EARSFile  # adjust import if needed
import unophysics.wavefuncs as wavefuncs

# --- Parameters from best set ---
params = {
    "band_low": 10000,
    "band_high": 60000,
    "window_ms": 1,
    "n_std": 1,
    "min_width_ms": 0.2,
    "max_width_ms": 2.0,
}

# --- Load data ---
filename = "../sample_data/71621DC7.190"  # adjust path if needed
ears = EARSFile(filename)
sig = ears.data
fs = ears.fs

# --- Wavelet denoising ---
sig_clean = wavefuncs.wave_clean(sig)


def bandpass_filter(sig, fs, low, high, order=4):
    nyq = 0.5 * fs
    low = low / nyq
    high = high / nyq
    b, a = butter(order, [low, high], btype="band")
    return filtfilt(b, a, sig)


# --- Filtered signal ---
filtered = bandpass_filter(sig_clean, fs, params["band_low"], params["band_high"])

# --- Envelope and threshold ---
from scipy.signal import hilbert, find_peaks

window_len = int(params["window_ms"] * 1e-3 * fs)
if window_len < 1:
    window_len = 1
envelope = np.abs(hilbert(filtered))
mov_avg = np.convolve(envelope, np.ones(window_len) / window_len, mode="same")
threshold = mov_avg + params["n_std"] * np.std(envelope)

# --- Peak detection ---
min_width = int(params["min_width_ms"] * 1e-3 * fs)
max_width = int(params["max_width_ms"] * 1e-3 * fs)
peaks, props = find_peaks(envelope, height=threshold, width=(min_width, max_width))
peak_times = peaks / fs

# --- Downsample for plotting ---
max_plot_points = 20000
if len(sig) > max_plot_points:
    step = int(np.ceil(len(sig) / max_plot_points))
    plot_x = np.arange(0, len(sig), step) / fs
    plot_y = sig[::step]
else:
    plot_x = np.arange(len(sig)) / fs
    plot_y = sig

# --- Plot ---
plt.figure(figsize=(12, 5))
plt.plot(plot_x, plot_y, label="Signal", color="gray", linewidth=0.8)
# Mark detected clicks
for t in peak_times:
    if t >= plot_x[0] and t <= plot_x[-1]:
        plt.axvline(t, color="red", alpha=0.5, linewidth=1)
plt.title("Signal with Detected Clicks")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.tight_layout()
plt.show()

print(f"Detected {len(peaks)} clicks.")
print("First 10 click times (s):", np.round(peak_times[:10], 4))

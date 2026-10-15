import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import butter, filtfilt, hilbert, find_peaks
from EARSFile import EARSFile


def bandpass(data, fs, low, high, order=4):
    nyq = 0.5 * fs
    # Ensure high cutoff is below Nyquist
    if high >= nyq:
        high = nyq - 1000  # 1 kHz below Nyquist for safety
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

# Adaptive threshold
window_ms = 50  # 50 ms window
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

# Peak detection with adaptive threshold
min_dist = int(0.001 * e.sampling_rate)  # 1 ms between clicks
peaks, props = find_peaks(envelope, height=local_thresh, distance=min_dist)

times = np.arange(len(e.data)) / e.sampling_rate

# Plot 1: Waveform with detected clicks (for continuity)
plt.figure(figsize=(12, 4))
plt.plot(times, e.data, linewidth=0.5, label="Waveform")
plt.plot(
    times,
    envelope * np.max(np.abs(e.data)) / np.max(envelope),
    alpha=0.5,
    label="Envelope",
)
plt.scatter(
    times[peaks], e.data[peaks], color="red", marker="o", label="Detected Clicks"
)
plt.title("Waveform with Detected Dolphin Clicks")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.legend()
plt.tight_layout()
plt.savefig("dolphin_clicks_detected.png", dpi=150)
print("Plot saved as dolphin_clicks_detected.png")

# Plot 2: Diagnostic plot with envelope, adaptive threshold, and detected clicks
plt.figure(figsize=(16, 8))
plt.subplot(2, 1, 1)
plt.plot(times, e.data, linewidth=0.5, label="Waveform")
plt.title("Waveform (Full)")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(times, envelope, label="Envelope", color="orange", alpha=0.7)
plt.plot(
    times,
    local_thresh,
    label="Adaptive Threshold",
    color="green",
    linestyle="--",
    alpha=0.7,
)
plt.scatter(
    times[peaks], envelope[peaks], color="red", marker="o", label="Detected Clicks"
)
plt.title("Envelope, Adaptive Threshold, and Detected Clicks")
plt.xlabel("Time (seconds)")
plt.ylabel("Envelope Amplitude")
plt.legend()
plt.tight_layout()
plt.savefig("dolphin_clicks_adaptive.png", dpi=150)
print("Plot saved as dolphin_clicks_adaptive.png")

# 5. Print summary
print(f"Detected {len(peaks)} dolphin clicks.")
if len(peaks) > 0:
    print("First 10 click times (s):", np.round(times[peaks[:10]], 4))
    print(
        "Mean interval between clicks (ms):",
        np.round(np.diff(times[peaks]).mean() * 1000, 2) if len(peaks) > 1 else "N/A",
    )
else:
    print("No clicks detected above threshold.")

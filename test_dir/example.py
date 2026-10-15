import numpy as np

import matplotlib.pyplot as plt
from scipy.io import wavfile

from EARSFile import EARSFile


from scipy.signal import butter, filtfilt, hilbert, find_peaks

fn = "../sample_data/71621DC7.190"
e = EARSFile(fn)


# --- Dolphin click detection ---
# 1. Bandpass filter (20-100 kHz)
def bandpass(data, fs, low, high, order=4):
    nyq = 0.5 * fs
    # Ensure high cutoff is below Nyquist
    if high >= nyq:
        high = nyq - 1000  # 1 kHz below Nyquist for safety
    b, a = butter(order, [low / nyq, high / nyq], btype="band")
    return filtfilt(b, a, data)


    # 3. Adaptive thresholding (moving window)
    def moving_threshold(signal, window_size, n_std=6):
        # Pad for edge effects
        pad = window_size // 2
        padded = np.pad(signal, (pad, pad), mode='reflect')
        cumsum = np.cumsum(padded)
        cumsum2 = np.cumsum(padded ** 2)
        means = (cumsum[window_size:] - cumsum[:-window_size]) / window_size
        sq_means = (cumsum2[window_size:] - cumsum2[:-window_size]) / window_size
        stds = np.sqrt(sq_means - means ** 2)
        return means + n_std * stds

    window_ms = 50  # 50 ms window
    window_size = int(window_ms * 1e-3 * e.sampling_rate)
    if window_size < 1:
        window_size = 1
    local_thresh = moving_threshold(envelope, window_size, n_std=6)
    local_thresh = np.concatenate([
        np.full(window_size//2, local_thresh[0]),
        local_thresh,
        np.full(window_size//2, local_thresh[-1])
    ])[:len(envelope)]

    # 4. Peak detection with adaptive threshold
    min_dist = int(0.001 * e.sampling_rate)  # 1 ms between clicks
    peaks, props = find_peaks(envelope, height=local_thresh, distance=min_dist)

# 2. Envelope
analytic = hilbert(filtered)
envelope = np.abs(analytic)

# 3. Peak detection (threshold: mean+6*std, min distance 0.002s)
threshold = np.mean(envelope) + 6 * np.std(envelope)
min_dist = int(0.002 * e.sampling_rate)  # 2 ms between clicks
peaks, props = find_peaks(envelope, height=threshold, distance=min_dist)

# 4. Plot waveform with detected clicks
times = np.arange(len(e.data)) / e.sampling_rate

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
    plt.figure(figsize=(16, 8))
    plt.subplot(2,1,1)
    plt.plot(times, e.data, linewidth=0.5, label="Waveform")
    plt.title("Waveform (Full)")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.legend()

    plt.subplot(2,1,2)
    plt.plot(times, envelope, label="Envelope", color='orange', alpha=0.7)
    plt.plot(times, local_thresh, label="Adaptive Threshold", color='green', linestyle='--', alpha=0.7)
    plt.scatter(times[peaks], envelope[peaks], color="red", marker="o", label="Detected Clicks")
    plt.title("Envelope, Adaptive Threshold, and Detected Clicks")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Envelope Amplitude")
    plt.legend()
    plt.tight_layout()
    plt.savefig("dolphin_clicks_adaptive.png", dpi=150)
    print("Plot saved as dolphin_clicks_adaptive.png")
plt.title("Waveform with Detected Dolphin Clicks")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.legend()
plt.tight_layout()
plt.savefig("dolphin_clicks_detected.png", dpi=150)
print("Plot saved as dolphin_clicks_detected.png")
# plt.show()

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


# Commented code is left here to serve as working examples of how to use the EARSFile class

# # Plot waveform
# plt.figure(figsize=(12, 4))
# plt.plot(np.arange(len(e.data)) / e.sampling_rate, e.data, linewidth=0.5)
# plt.title("Waveform of EARS File")
# plt.xlabel("Time (seconds)")
# plt.ylabel("Amplitude")
# plt.tight_layout()
# plt.show()

# # Save as wav file (normalize to int16)
# audio = e.audio_data()
# audio_int16 = np.int16(audio * 32767)
# wavfile.write("ears_output.wav", e.sampling_rate, audio_int16)
# print("WAV file saved as ears_output.wav")

import numpy as np
from scipy.signal import butter, filtfilt, hilbert, find_peaks
from EARSFile import EARSFile
import unophysics.wavefuncs as wavefuncs
import csv
import matplotlib.pyplot as plt


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
sig_clean = wavefuncs.wave_clean(e.data)

# --- Get suggested threshold from wave_clean ---
sig_clean, suggested_thresh = wavefuncs.wave_clean(e.data, ret_thresh=True)

# --- Try 8 thresholds: suggested * linspace(100, 200, 8) ---
mults = np.linspace(100, 200, 8)
thresholds = [m for m in mults]
cleaned_signals = [
    wavefuncs.wave_clean(e.data, wavelet_thresh=thresh) for thresh in thresholds
]

# --- Plot all 8 cleaned signals on a grid ---
max_plot_points = 20000  # for downsampling plots
fig, axes = plt.subplots(4, 2, figsize=(14, 10), sharex=True, sharey=True)
axes = axes.flatten()
for i, (ax, sig_c, thresh, mult) in enumerate(
    zip(axes, cleaned_signals, thresholds, mults)
):
    if len(sig_c) > max_plot_points:
        step = int(np.ceil(len(sig_c) / max_plot_points))
        plot_x = np.arange(0, len(sig_c), step) / e.sampling_rate
        plot_y = sig_c[::step]
    else:
        plot_x = np.arange(len(sig_c)) / e.sampling_rate
        plot_y = sig_c
    ax.plot(plot_x, plot_y, color="blue", linewidth=0.7)
    ax.set_title(f"Thresh: {thresh:.2f} (x{mult:.1f})")
plt.suptitle(
    "Wavelet-cleaned waveform for 8 thresholds (suggested × multipliers 100–200)"
)
plt.tight_layout(rect=[0, 0, 1, 0.97])
plt.show()

# --- Use threshold multiplier 150 for wavelet cleaning ---
thresh_mult = 150
thresh = thresh_mult
sig_clean = wavefuncs.wave_clean(e.data, wavelet_thresh=thresh)

# --- Main detection logic with cleaned signal ---
results = []
# focused_params is not defined in the provided code, assuming it should be the same as in the original context
focused_params = [
    {
        "band_low": 60000,
        "band_high": 100000,
        "window_ms": 3,
        "n_std": 6,
        "min_width_ms": 1,
        "max_width_ms": 100,
    },
    # Add or modify parameter sets as needed
]
for params in focused_params:
    band_low = params["band_low"]
    band_high = params["band_high"]
    window_ms = params["window_ms"]
    n_std = params["n_std"]
    min_width_ms = params["min_width_ms"]
    max_width_ms = params["max_width_ms"]
    filtered = bandpass(sig_clean, e.sampling_rate, band_low, band_high)
    analytic = hilbert(filtered)
    envelope = np.abs(analytic)
    window_size = int(window_ms * 1e-3 * e.sampling_rate)
    if window_size < 1:
        window_size = 1
    local_thresh = moving_threshold(envelope, window_size, n_std=n_std)
    local_thresh = np.concatenate(
        [
            np.full(window_size // 2, local_thresh[0]),
            local_thresh,
            np.full(window_size // 2, local_thresh[-1]),
        ]
    )[: len(envelope)]
    min_width = int(min_width_ms * 1e-3 * e.sampling_rate)
    max_width = int(max_width_ms * 1e-3 * e.sampling_rate)
    min_dist = min_width
    peaks, props = find_peaks(
        envelope, height=local_thresh, distance=min_dist, width=(min_width, max_width)
    )
    if "widths" in props:
        peak_widths_ms = props["widths"] / e.sampling_rate * 1000
    else:
        peak_widths_ms = np.array([])
    result = {
        "band_low": band_low,
        "band_high": band_high,
        "window_ms": window_ms,
        "n_std": n_std,
        "min_width_ms": min_width_ms,
        "max_width_ms": max_width_ms,
        "num_peaks": len(peaks),
        "mean_width_ms": (
            float(np.mean(peak_widths_ms)) if len(peak_widths_ms) > 0 else 0
        ),
        "std_width_ms": float(np.std(peak_widths_ms)) if len(peak_widths_ms) > 0 else 0,
        "first_10_times": np.round(peaks[:10] / e.sampling_rate, 4).tolist(),
    }
    results.append(result)

# --- Print summary table ---
print(
    f"{'band_low':>8} {'band_high':>9} {'window':>6} {'n_std':>6} {'min_w':>6} {'max_w':>6} {'n_peaks':>8} {'mean_w':>8} {'std_w':>8} {'first_10_times (s)'}"
)
for r in results:
    print(
        f"{r['band_low']:8} {r['band_high']:9} {r['window_ms']:6} {r['n_std']:6} {r['min_width_ms']:6.2f} {r['max_width_ms']:6.2f} {r['num_peaks']:8} {r['mean_width_ms']:8.3f} {r['std_width_ms']:8.3f} {r['first_10_times']}"
    )

# --- Dump all results to CSV ---
with open("click_detection_results.csv", "w", newline="") as csvfile:
    fieldnames = [
        "band_low",
        "band_high",
        "window_ms",
        "n_std",
        "min_width_ms",
        "max_width_ms",
        "num_peaks",
        "mean_width_ms",
        "std_width_ms",
        "first_10_times",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for r in results:
        r_copy = r.copy()
        r_copy["first_10_times"] = str(r_copy["first_10_times"])
        writer.writerow(r_copy)

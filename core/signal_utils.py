import numpy as np
import tkinter as tk
from tkinter import ttk
import pandas as pd
from scipy.signal import resample
from scipy.stats import skew, kurtosis, mode, entropy
from tkinter import simpledialog, messagebox
from core import settings

def amplitud_scaling(signal): 
    gain = simpledialog.askfloat  ("Constant Value:", "Value:", initialvalue=1.0)
    return gain * np.array(signal)

def amplitud_log(signal):
    return np.log(signal)

def amplitud_exponential(signal):
    power = simpledialog.askfloat  ("Constant Value:", "Value:", initialvalue=1.0)
    return power**np.array(signal)

def amplitud_inversion(signal):
    return 1/np.array(signal)

def amplitud_power(signal):
    power = simpledialog.askfloat  ("Constant Value:", "Value:", initialvalue=1.0)
    return np.array(signal)**power

def amplitud_none(signal):
    return np.array(signal)

def amplitud_selector(name: str, signal: list[float] | np.ndarray)-> np.ndarray:
    options = {
        settings.opera_amp[0]: amplitud_scaling,
        settings.opera_amp[1]: amplitud_log,
        settings.opera_amp[2]: amplitud_exponential,
        settings.opera_amp[3]: amplitud_inversion,
        settings.opera_amp[4]: amplitud_power,
        settings.opera_amp[5]: amplitud_none
    }

    y = options[name](signal)
    y = verification(y)
    return y

def downsampling(signal, n0, fs, type, duration):
    k = abs(simpledialog.askinteger("Downsampling for integer k", "Value:",minvalue = 0, initialvalue=2))
    if k == 0:
        y = np.zeros(len(signal))
        y[:] = signal[0]
    else:
        y = signal[::k]
    n = axis_time(len(y), fs, n0, type, duration)
    return n, y

def upsampling(signal, n0, fs, type, duration):
    k = simpledialog.askinteger("Upsampling for integer k", "Value:",minvalue = 1 , initialvalue=3)
    y = np.zeros(len(signal) * k - (k-1))
    n = axis_time(len(y), fs, n0, type, duration)

    y[::k] = signal
    for i in range(0, len(y)):
        if i % k != 0 and i:
            idx_prev = i // k
            idx_next = idx_prev + 1
            
            if idx_next >= len(signal):
                idx_next = idx_prev
            
            alpha = (i % k) / k
            y[i] = signal[idx_prev] * (1 - alpha) + signal[idx_next] * alpha
            
    return n, y

def sampling_none(signal, n0, fs, type, duration):
    n = axis_time(len(signal), fs, n0, type, duration)
    return n, np.asarray(signal)

def time_sampling(name: str, signal: list[float] | np.ndarray, fs:int, n0:int, duration:float, type:str)-> tuple[np.ndarray, np.ndarray]:
    options = {
        settings.sampling_method[0]: downsampling,
        settings.sampling_method[1]: upsampling,
        settings.sampling_method[2]: sampling_none
    }
    n, y = options[name](signal, n0, fs, type, duration)

    return n, y

def axis_time(n_samples: int, fs: int, n0: float, type: str, duration: float) -> np.ndarray:   
    if type == settings.signal_types[1]: #signal
        n = n0 + np.arange(n_samples) / fs
    elif type == settings.signal_types[0]: #audio
        n0_samples = int(n0 * fs)
        n = np.arange(n0_samples, n0_samples + n_samples)
        n = n / fs 
    return n

def resample_and_align(y1, fs1, y2, fs2):
    if fs1 >= fs2:
        fs_target = fs2
    else:
        fs_target = fs1
    fs_target = abs(simpledialog.askinteger("Warning", "Frequency value:", initialvalue=int(fs_target)))
    dur1 = len(y1) / fs1
    dur2 = len(y2) / fs2

    n1_target = int(fs_target * dur1)
    n2_target = int(fs_target * dur2)

    y1_resampled = resample(y1, n1_target)
    y2_resampled = resample(y2, n2_target)

    ly1 = len(y1_resampled)
    ly2 = len(y2_resampled)
    pad = abs(ly1 - ly2)

    if ly1 > ly2:
        y2_resampled = np.pad(y2_resampled, (0, pad), mode='constant', constant_values=0)
    elif ly1 < ly2:
        y1_resampled = np.pad(y1_resampled, (0, pad), mode='constant', constant_values=0)
    
    y1_resampled = verification(y1_resampled)
    y2_resampled = verification(y2_resampled)

    return y1_resampled, y2_resampled, fs_target

def resample_signal(y1, fs1, y2, fs2):
    fs_target = max(fs1, fs2)
    fs_target = abs(simpledialog.askinteger("Warning", "Frequency value:", initialvalue=int(fs_target)))
    dur1 = len(y1) / fs1
    dur2 = len(y2) / fs2

    n1_target = int(fs_target * dur1)
    n2_target = int(fs_target * dur2)

    y1_resampled = resample(y1, n1_target)
    y2_resampled = resample(y2, n2_target)

    return y1_resampled, y2_resampled, fs_target

def signals_padding(y1:list[float] | np.ndarray, n0_1:float, y2:list[float] | np.ndarray, n0_2:float, fs:int):
    start = min(n0_1, n0_2)
    end = max(n0_1 + len(y1) / fs, n0_2 + len(y2) / fs)
    total_length = int((end - start) * fs)

    y1_extended = np.zeros(total_length)
    y2_extended = np.zeros(total_length)

    y1_start_index = int((n0_1 - start) * fs)
    y2_start_index = int((n0_2 - start) * fs)

    y1_extended[y1_start_index:y1_start_index + len(y1)] = y1
    y2_extended[y2_start_index:y2_start_index + len(y2)] = y2

    n = np.linspace(start, end, total_length, endpoint=False)

    return n, y1_extended, y2_extended

def stadistics(y1, fs1, y2, fs2, y3, fs3):
    signals = [y1, y2, y3]
    sampling_freqs = [fs1, fs2, fs3]
    signal_names = ["Y1", "Y2", "Y3"]
    all_features = []

    for y, fs in zip(signals, sampling_freqs):
        if y is None or len(y) == 0:
            features = {key: None for key in settings.feature_keys}
        else:
            features = {
                'Energy': np.sum(np.abs(y) ** 2),
                'Power': np.mean(np.abs(y) ** 2),
                'Mean': np.mean(y),
                'Variance': np.var(y),
                'Standard Deviation': np.std(y),
                'Minimum': np.min(y),
                'Maximum': np.max(y),
                'Mode': mode(y, keepdims=False).mode,
                'Median': np.median(y),
                'Skewness': skew(y),
                'Kurtosis': kurtosis(y),
                'Entropy': entropy(np.abs(y)),
                'Dominant Frequency': get_dominant_frequency(y, fs),
                'Sampling Frequency': fs
            }
        all_features.append(features)

    window = tk.Toplevel()
    window.title("Signals Statistics")
    window.geometry("1000x400")

    columns = ["Feature"] + signal_names
    tree = ttk.Treeview(window, columns=columns, show="headings")
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=200, anchor="center")

    feature_keys = list(all_features[0].keys())
    for key in feature_keys:
        row = [key] + [f"{features[key]:.4f}" if features[key] is not None else "NULL" for features in all_features]
        tree.insert('', 'end', values=row)

    tree.pack(fill="both", expand=True)

def verification(y: list[float] | np.ndarray)-> np.ndarray:
    y = np.asarray(y, dtype=np.float32)
    mask = np.isfinite(y)
    if not np.all(mask):
        messagebox.showwarning("Warning", "Value nan or inf deleted...")
        y = y[mask]
    return y

def get_dominant_frequency(y: np.ndarray, fs: int) -> float:
    if y is None or len(y) == 0:
        return None

    y = np.squeeze(y)

    spectrum = np.fft.fft(y)
    freqs = np.fft.fftfreq(len(y), d=1/fs)

    positive_freqs = freqs[:len(freqs)//2]
    positive_spectrum = np.abs(spectrum[:len(spectrum)//2])

    idx = np.argmax(positive_spectrum)
    dominant_freq = positive_freqs[idx]

    return dominant_freq

def show_features(features, title):
    root = tk.Toplevel()
    root.title(title)

    text = tk.Text(root, width=80, height=20)
    text.pack(padx=10, pady=10)

    for key, value in features.items():
        text.insert(tk.END, f"{key}: {value}\n")

    root.mainloop()
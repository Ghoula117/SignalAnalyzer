import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from scipy.signal import lfilter, lfilter_zi
from tkinter import messagebox, simpledialog
from core import settings
from ui.plotter import ProcessedSignalPlot
from core.signal_utils import resample_signal, signals_padding
from core.file_manager import load_coeficients, load_signal
from scipy.fftpack import dct, idct
#import pywt

processed_plot = ProcessedSignalPlot()

def basic_operations(action: str, y1: list[float] | np.ndarray, fs1:int, n01:float, y2: list[float] | np.ndarray, fs2:int, n02:float)-> np.ndarray: 
    actions = {
        settings.basicOperation[0]: addition,
        settings.basicOperation[1]: subtraction,
        settings.basicOperation[2]: multiply,
        settings.basicOperation[3]: division,
        settings.basicOperation[4]: power,
    }
    n, result, freq = actions[action](y1, fs1, n01, y2, fs2, n02)

    return n, result, freq

def addition(y1, fs1, n01, y2, fs2, n02):
    y1_resampled, y2_resampled, freq = resample_signal(y1, fs1, y2, fs2)
    n, y1_pad, y2_pad = signals_padding(y1_resampled, n01, y2_resampled, n02, freq)
    result = y1_pad + y2_pad

    generate_result(n, result)
    return n, result, freq

def subtraction(y1, fs1, n01, y2, fs2, n02):
    y1_resampled, y2_resampled, freq = resample_signal(y1, fs1, y2, fs2)
    n, y1_pad, y2_pad = signals_padding(y1_resampled, n01, y2_resampled, n02, freq)
    result = y1_pad - y2_pad

    generate_result(n, result)
    return n, result, freq

def multiply(y1, fs1, n01, y2, fs2, n02):
    y1_resampled, y2_resampled, freq = resample_signal(y1, fs1, y2, fs2)
    n, y1_pad, y2_pad = signals_padding(y1_resampled, n01, y2_resampled, n02, freq)
    result = y1_pad * y2_pad

    generate_result(n, result)
    return n, result, freq

def division(y1, fs1, n01, y2, fs2, n02):
    y1_resampled, y2_resampled, freq = resample_signal(y1, fs1, y2, fs2)
    n, y1_pad, y2_pad = signals_padding(y1_resampled, n01, y2_resampled, n02, freq)
    result = y1_pad / y2_pad

    generate_result(n, result)
    return n, result, freq

def power(y1, fs1, n01, y2, fs2, n02):
    y1_resampled, y2_resampled, freq = resample_signal(y1, fs1, y2, fs2)
    n, y1_pad, y2_pad = signals_padding(y1_resampled, n01, y2_resampled, n02, freq)
    result = y1_pad ** y2_pad

    generate_result(n, result)
    return n, result, freq

def preprocessing_operations(action: str, y: list[float] | np.ndarray):
    actions = {
        settings.preprocessing_operation[0]: min_max_normalization,
        settings.preprocessing_operation[1]: signed,
        settings.preprocessing_operation[2]: standard_normalization
    }
    y = actions[action](y)
    return y

def min_max_normalization(y):
    return (y - np.min(y)) / (np.max(y) - np.min(y))

def signed(y):
    return y / np.max(np.abs(y))

def standard_normalization(y):
    return (y - np.mean(y)) / np.std(y)

def filtering_operation(action: str, **kwargs):
    actions = {
        settings.filter_type[0]: fir_filter,
        settings.filter_type[1]: iir_filter,
    }
    n, result, fs = actions[action](**kwargs)
    generate_result(n, result)

    return n, result, fs

def fir_filter(x, nx0, fs1, h, nh0, fs2):
    indx = simpledialog.askinteger("Convolution method", "\n1 Load parameters\n2 Set parameters", minvalue=1, maxvalue=2, initialvalue=1)
    block_size = simpledialog.askinteger("Block Size","Value:", minvalue=1, initialvalue=4)

    if indx == 1:
        hi = nh0
        h_fix= h
        if h_fix is None:
            messagebox.showerror("Warning", "h(n) not found")
            return None, None
        
    elif indx == 2:
        hi = simpledialog.askinteger("Initial value","h(n1):", initialvalue=0)
        while True:
            h_values = simpledialog.askstring("h(n)", "Value:", initialvalue=settings.default_h_parameters)
            if h_values is None:
                return None, None
            try:
                h_fix = np.array(list(map(float, h_values.split()))) 
            except ValueError as e:
                messagebox.showerror("Warning" , e)
            else:
                break
        
    x_resampled, h_fix, freq = resample_signal(x, fs1, h, fs2)       

    Lx = len(x_resampled)
    Lh = len(h_fix)
    Ly = Lx + Lh - 1
    yi = nx0 + hi
    yf = yi + Ly - 1

    y_total = np.zeros(Ly)
    
    for i in range(0, Lx, block_size):
        x_block = x_resampled[i : i + block_size]
        nx_block = nx0 + i

        n_block, y_block = convolution(x_block, nx_block, h_fix, hi)

        start_index = int(n_block[0] - yi)
        end_index = int(start_index + len(y_block))

        if start_index < 0:
            y_block = y_block[-start_index:]
            start_index = 0

        if end_index > Ly:
            y_block = y_block[:Ly - start_index]
            end_index = Ly

        y_total[start_index:end_index] += y_block

    n_total = np.arange(yi, yf + 1)
    n_total = n_total / freq

    return n_total, y_total, freq

def iir_filter(x, nx0, fs1, **kwargs):
    indx = simpledialog.askinteger("Convolution method", "\n1 Load coefficient\n2 Set coefficient", minvalue=1, maxvalue=2, initialvalue=1)
    block_size = simpledialog.askinteger("Block Size","Value:", minvalue=1, initialvalue=4)

    if indx == 1:
        ax, bx = load_coeficients()
        if ax is None or bx is None:
            messagebox.showerror("Warning", "a(n) or b(n) not found")
            return None, None, None
        
    elif indx == 2:
        ax = []
        bx = []
        while True:
            ax_str = simpledialog.askstring("a_k", "Enter a_k coefficients:", initialvalue=settings.ax)
            bx_str = simpledialog.askstring("b_k", "Enter b_k coefficients:", initialvalue=settings.bx)
            try:
                ax = np.array(list(map(float, ax_str.split())))
                bx = np.array(list(map(float, bx_str.split())))
            except Exception as e:
                messagebox.showerror("Warning" , f"Invalid input: {e}")
                return None, None, None
            else:
                break

    a0 = ax[0]
    try:
        a_norm = [coef / a0 for coef in ax]
        b_norm = [coef / a0 for coef in bx]
    except:
        messagebox.showerror("Warning", "Invalid a0 filter coefficient")
        return None, None, None
    
    y_total = []

    zi = lfilter_zi(b_norm, a_norm) * x[0]
    for i in range(0, len(x), block_size):
        x_bloque = x[i:i+block_size]
        y_bloque, zi = lfilter(b_norm, a_norm, x_bloque, zi=zi)
        y_total.extend(y_bloque)

    y_total = np.array(y_total)
    n = np.arange(len(y_total))
    n = n * (1 / fs1)

    return n, y_total, fs1

def convolution(x, nx0, h, nh0):
    Lx = len(x)
    Lh = len(h)

    xf = nx0 + Lx - 1
    hf = nh0 + Lh - 1

    Ly = Lx + Lh - 1
    yi = nx0 + nh0
    yf = xf + hf

    """y = np.zeros(Ly)
    for n in range(Ly): 
        for k in range(Lh): 
            if 0 <= n - k < Lx:
                 y[n] += h[k] * x[n - k]
                 
    n = np.arange(yi, yf + 1)
    return n, y"""

    y = np.convolve(x, h)
    n = np.linspace(yi, yf, Ly)
    
    return n, y

def fourier_operation(action: str, **kwargs):
    actions = {
        settings.fourier_operation[0]: fourier_magnitude_phase,
        settings.fourier_operation[1]: fourier_filtering,
    }
    actions[action](**kwargs)

def compute_fft(sig, fs):
    N = len(sig)
    X = np.fft.fft(sig)
    freqs = np.fft.fftfreq(N, d=1/fs)
    magnitude = np.abs(X)
    phase = np.angle(X)
    return np.fft.fftshift(freqs), np.fft.fftshift(magnitude), np.fft.fftshift(phase)

def plot_fft_signals(x, h, fs):
    plt.close('all')
    f_x, mag_x, phase_x = compute_fft(x, fs)
    f_h, mag_h, phase_h = compute_fft(h, fs)

    plt.figure(figsize=(12, 8))

    plt.subplot(2, 2, 1)
    plt.plot(f_x, mag_x, color='blue')
    plt.title('Magnitude Spectrum - x[n]')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('|X(f)|')
    plt.grid(True)

    plt.subplot(2, 2, 2)
    plt.plot(f_x, phase_x, color='orange')
    plt.title('Phase Spectrum - x[n]')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Phase [rad]')
    plt.grid(True)

    plt.subplot(2, 2, 3)
    mag_h_db = 20 * np.log10(mag_h + 1e-12) 
    plt.plot(f_h, mag_h_db, color='green')
    plt.title('Magnitude Spectrum (dB) - h[n]')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('|H(f)| [dB]')
    plt.grid(True)

    plt.subplot(2, 2, 4)
    plt.plot(f_h, phase_h, color='red')
    plt.title('Phase Spectrum - h[n]')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Phase [rad]')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

def fourier_magnitude_phase(x, fs1, h, fs2):
    try:
        x_resampled, h_resampled, freq = resample_signal(x, fs1, h, fs2)
        plot_fft_signals(x_resampled, h_resampled, freq)
    except:
        messagebox.showwarning("Warning", "Select both signals.")
        return

def fourier_filtering(x, fs1, h, fs2):
    plt.close('all')
    x_resampled, h_resampled, freq = resample_signal(x, fs1, h, fs2)

    N = len(x_resampled) + len(h_resampled) - 1
    x_pad = np.pad(x_resampled, (0, N - len(x_resampled)))
    h_pad = np.pad(h_resampled, (0, N - len(h_resampled)))

    X = np.fft.fft(x_pad)
    H = np.fft.fft(h_pad)
    Y = X * H
    y = np.fft.ifft(Y).real

    Y_fft = np.fft.fft(y)
    freqs = np.fft.fftfreq(len(Y_fft), d=1/freq)

    plt.figure(figsize=(10, 8))
    plt.specgram(x, Fs=freq, NFFT=256, noverlap=128, cmap='viridis')
    plt.title("Espectrogram - Signal Y1")
    plt.xlabel("Time (s)")
    plt.ylabel("Freq (Hz)")
    plt.colorbar()
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 3))
    plt.specgram(h, Fs=freq, NFFT=256, noverlap=128, cmap='viridis')
    plt.title("Espectrogram - Signal Y2")
    plt.xlabel("Time (s)")
    plt.ylabel("Freq (Hz)")
    plt.colorbar()
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 4))
    plt.plot(freqs[:len(freqs)//2], np.abs(Y_fft[:len(Y_fft)//2]))
    plt.title("Frequency Spectrum - Signal Out")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 3))
    plt.specgram(y, Fs=freq, NFFT=256, noverlap=128, cmap='viridis')
    plt.title("Espectrogram - Signal Out")
    plt.xlabel("Time (s)")
    plt.ylabel("Freq (Hz)")
    plt.colorbar()
    plt.tight_layout()
    plt.show()

def cosine_operation(action: str, **kwargs):
    actions = {
        settings.cosine_operation[0]: cosine_magnitude_phase,
        settings.cosine_operation[1]: cosine_filtering,
    }
    actions[action](**kwargs)

def cosine_magnitude_phase(x, fs1, h, fs2):
    plt.close('all')
    x_resampled, h_resampled, freq_resampled = resample_signal(x, fs1, h, fs2)

    dct_x = dct(x_resampled, norm='ortho')
    freq_x = np.linspace(0, freq_resampled/2, len(dct_x))
    dct_h = dct(h_resampled, norm='ortho')
    freq_h = np.linspace(0, freq_resampled/2, len(dct_h))
    
    plt.figure(figsize=(10, 4))
    plt.plot(freq_x, np.abs(dct_x))
    plt.title("Magnitude T. Cosine x(n)")
    plt.xlabel("Freq (Hz)")
    plt.ylabel("Magnitude")

    plt.figure(figsize=(10, 4))
    plt.plot(freq_h, np.abs(dct_h))
    plt.title("Magnitude T. Cosine h(n)")
    plt.xlabel("Freq (Hz)")
    plt.ylabel("Magnitude")

    plt.grid(True)
    plt.tight_layout()
    plt.show()

def cosine_filtering(signal, fs, cutoff=1000):
    dct_signal = dct(signal, norm='ortho')

    N = len(dct_signal)
    freqs = np.linspace(0, fs/2, N)
    filter_mask = freqs <= cutoff
    dct_filtered = dct_signal * filter_mask

    signal_filtered = idct(dct_filtered, norm='ortho')

    t = np.arange(len(signal)) / fs

    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t, signal, label='Original')
    plt.plot(t, signal_filtered, label='Filter', linestyle='--')
    plt.legend()
    plt.title("Señal original vs filtrada (dominio temporal)")
    plt.xlabel("Time [s]")

    plt.subplot(2, 1, 2)
    plt.plot(freqs, np.abs(dct_signal), label='DCT original')
    plt.plot(freqs, np.abs(dct_filtered), label='DCT filtered', linestyle='--')
    plt.legend()
    plt.title("DCT original vs filter")
    plt.xlabel("Freq (Hz)")
    plt.tight_layout()
    plt.show()

def wavelet_transform(x):
    plt.close('all')
    wavelet = 'db6'
    level = 3
    coeffs = pywt.wavedec(x, wavelet, level=level)
    labels = ['A3', 'D3', 'D2', 'D1']

    plt.figure(figsize=(12, 8))
    for i, coef in enumerate(coeffs):
        plt.subplot(len(coeffs), 1, i + 1)
        plt.plot(coef, color='teal')
        plt.title(f'Wavelet Coefficients: {labels[i] if i < len(labels) else f"Detail {i}"}')
        plt.grid(True)

    plt.tight_layout()
    plt.show()

def generate_result(n, y):
    root = tk.Tk()
    root.withdraw()
    try:
        processed_plot.show(root, n, y)
    except:
        messagebox.showwarning("Warning", "Signal first...")
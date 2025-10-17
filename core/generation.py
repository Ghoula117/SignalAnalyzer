import numpy as np
from tkinter import simpledialog
from core import settings

def signal_impulse(fa, fs, gain, n0, duration, shift):
    n = np.linspace(n0, n0 + duration, int(duration * fs), endpoint=False)
    y = np.zeros_like(n, dtype=np.float32)

    idx = round((shift - n0) * fs)
    if 0 <= idx < len(y):
        y[idx] = gain
    elif idx == len(y):
        y[-1] = gain
    return n, y

def signal_step(fa, fs, gain, n0, duration, shift):
    n = np.linspace(n0, n0 + duration, int(duration * fs), endpoint=False)
    y = np.zeros_like(n, dtype=np.float32) 

    idx = round((shift - n0) * fs)
    if 0 <= idx < len(y):
        y[idx:] = gain 
    elif idx == len(y):
        y[-1] = gain

    return n, y

def signal_ramp(fa, fs, gain, n0, duration, shift):
    n = np.linspace(n0, n0 + duration, int(duration * fs), endpoint=False)
    y = np.zeros_like(n, dtype=np.float32)
    
    idx = round((shift - n0) * fs)
    if 0 <= idx < len(y):
        y[n >= shift] = gain*(n[n >= shift]-shift) 
    elif idx == len(y):
        y[-1] = 0

    return n, y

def signal_triangular(fa, fs, gain, n0, duration, shift):
    Offset = simpledialog.askfloat  ("Offset","valor:", initialvalue=0  )
    n = np.linspace(n0, n0 + duration, int(duration * fs), endpoint=False)  
    y = np.zeros_like(n, dtype=np.float32)

    idx = round((shift - n0) * fs)
    if 0 <= idx < len(y):
        y = gain * 2 * np.abs(2 * (fa * (n - shift) % 1) - 1) - gain + Offset
    elif idx == len(y):
        y[-1] = 0
    y[n < shift] = 0

    return n, y

def signal_sawtooth(fa, fs, gain, n0, duration, shift):
    Offset = simpledialog.askfloat  ("Offset","valor:", initialvalue=0  )
    n = np.linspace(n0, n0 + duration, int(duration * fs), endpoint=False) 
    y = np.zeros_like(n, dtype=np.float32)

    idx = round((shift - n0) * fs)
    if 0 <= idx < len(y):
        y = gain * (2 * (fa * (n - shift) % 1) - 1) + Offset
    elif idx == len(y):
        y[-1] = 0
    y[n < shift] = 0

    return n, y

def signal_sine(fa, fs, gain, n0, duration, shift):
    An = simpledialog.askfloat  ("Fase (Rad)","valor:", initialvalue=0  )
    n = np.linspace(n0, n0 + duration, int(duration * fs), endpoint=False) 
    y = np.zeros_like(n, dtype=np.float32)

    idx = round((shift - n0) * fs)
    if 0 <= idx < len(y):
        g = 2 * np.pi * fa * (n + shift)
        y = gain * np.sin(g + An)
    elif idx == len(y):
        y[-1] = 0
    y[n < shift] = 0

    return n, y

def signal_cosine(fa, fs, gain, n0, duration, shift):
    An = simpledialog.askfloat  ("Fase (Rad)",      "valor:", initialvalue=0  )
    n = np.linspace(n0, n0 + duration, int(duration * fs), endpoint=False) 
    y = np.zeros_like(n, dtype=np.float32)

    idx = round((shift - n0) * fs)
    if 0 <= idx < len(y):
        g = 2 * np.pi * fa * (n + shift)
        y = gain * np.cos(g + An)
    elif idx == len(y):
        y[-1] = 0
    y[n < shift] = 0

    return n, y

def signal_sinc(fa, fs, gain, n0, duration, shift):
    An = simpledialog.askfloat  ("Fase (Rad)",      "valor:", initialvalue=0  )
    n = np.linspace(n0, n0 + duration, int(duration * fs), endpoint=False) 
    y = np.zeros_like(n, dtype=np.float32)

    idx = round((shift - n0) * fs)
    if 0 <= idx < len(y): 
        g = 2 * np.pi * fa * (n + shift)
        y = gain * np.sinc(g + An)
    elif idx == len(y):
        y[-1] = 0

    return n, y

def signal_chirp(fa, fs, gain, n0, duration, shift):
    n = np.linspace(n0, n0 + duration, int(duration * fs), endpoint=False) 
    y = np.zeros_like(n, dtype=np.float32)
    An = simpledialog.askfloat  ("Fase",        "Value: (Rad)", initialvalue=0)
    fb  = simpledialog.askfloat ("Final freq",  "Value: Hz",   initialvalue=20)
    indx = simpledialog.askinteger("Select Operation", "\n1Chirp Lineal\n2Chirp Expo",initialvalue=1, minvalue=1, maxvalue=2)
    
    idx = round((shift - n0) * fs)
    if 0 <= idx < len(y):
        if indx == 1:
            K = (fb - fa) / duration
            phase = 2 * np.pi * (fa *(n + shift) + 0.5 * K * (n + shift)**2)
        else:
            """while True:
                B  = simpledialog.askfloat("Base Real",      "valor:", initialvalue=0.9)
                if B <= 0:
                    messagebox.showwarning("Error", "Debe ingresar un valor real mayor a 0.")
                    continue
                break"""
            B = (fb / fa)**(1/duration)
            phase = 2 * np.pi * (fa / np.log(B)) * (B**(n + shift) - 1)
        y = gain * np.sin(phase + An)
    elif idx == len(y):
        y[-1] = 0

    return n, y

def signal_selector(
    name: str, fa: float, fs: int, gain: float, n0: int, duration: float, shift: float) -> tuple[np.ndarray, np.ndarray]:

    options = {
        settings.signalSelector[0]: signal_impulse,
        settings.signalSelector[1]: signal_step,
        settings.signalSelector[2]: signal_ramp,
        settings.signalSelector[3]: signal_triangular,
        settings.signalSelector[4]: signal_sawtooth,
        settings.signalSelector[5]: signal_sine,
        settings.signalSelector[6]: signal_cosine,
        settings.signalSelector[7]: signal_sinc,
        settings.signalSelector[8]: signal_chirp
    }

    n, y = options[name](fa, fs, gain, n0, duration, shift)

    return n, y
source_controls = [
    {"label": "Source", "relx": 0.075, "rely": 0.005, "values": ["Sintetic", "Board", "Dataset"], "dependents": {"Sintetic": ["Signal"], "Board": ["Baudrate"]}},
    {"label": "Signal", "relx": 0.775, "rely": 0.005, "values": ["Impulse", "Step", "Ramp", "Triangular", "Sawtooth", "Sine", "Cosine", "SinC", "Chirp"]},
    {"label": "Baudrate", "relx": 0.775, "rely": 0.005, "values": ["9600", "115200", "230400", "460800", "921600"]},
    {"label": "Channel", "relx": 0.075, "rely": 0.25, "values": ["y1", "y2"]},
    {"label": "Amplitude", "relx": 0.425, "rely": 0.005, "values": ["A*x(n)", "log(x(n))", "A^x(n)", "1/x(n)", "x(n)^k", "None"]},
    {"label": "Normalization", "relx": 0.6, "rely": 0.005, "values": ["Normalization 0 & 1", "Normalization -1 & 1", "Standard normalization"]},
    {"label": "Resample", "relx": 0.6, "rely": 0.25, "values": ["Downsampling", "Upsampling", "None"]}
]

source_entries = [
    {"name": "Duration", "placeholder": "Duration (s)", "relx": 0.25, "rely": 0.005},
    {"name": "Start", "placeholder": "Start (s)", "relx": 0.25, "rely": 0.25},
    {"name": "Shift", "placeholder": "Shift (s)", "relx": 0.25, "rely": 0.495},
    {"name": "Gain", "placeholder": "Gain", "relx": 0.425, "rely": 0.25},
    {"name": "Sampling", "placeholder": "Sampling Rate (Hz)", "relx": 0.6, "rely": 0.495},
]

operation_controls = [
    {"label": "Fourier Transform", "relx": 0.25, "rely": 0.005, "values": ["DFT Magnitude/Phase", "DFT Filtering"]},
    {"label": "Cosine Transform" , "relx": 0.425, "rely": 0.005, "values": ["Cosine Magnitude", "Cosine Filtering"]},
    {"label": "Wavelet Transform", "relx": 0.6, "rely": 0.005, "values": ["Wavelet 1", "Wae"]},
]
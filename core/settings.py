sourceOptions = ["Sintetic", "Board", "Dataset"]
signalSelector = ["Impulse", "Step", "Ramp", "Triangular", "Sawtooth", "Sine", "Cosine", "SinC", "Chirp"]
baudrate = ["9600", "115200", "230400", "460800", "921600"]
channelOptions = ["y1", "y2"]
amplitudeOperations = ["A*x(n)", "log(x(n))", "A^x(n)", "1/x(n)", "x(n)^k", "None"]
normalizationMethods = ["Normalization 0 & 1", "Normalization -1 & 1", "Standard normalization"]
resampleMethods = ["Downsampling", "Upsampling", "None"]
operationOptions = ["Fourier Transform", "Cosine Transform", "Wavelet Transform"]
fourierOptions = ["DFT Magnitude/Phase", "DFT Filtering"]
cosineOptions = ["Cosine Magnitude", "Cosine Filtering"]
waveletOptions = ["Wavelet 1", "Wae"]


source_controls = [
    {"label": "Source", "relx": 0.075, "rely": 0.005, "values": sourceOptions, "dependents": {"Sintetic": ["Signal"], "Board": ["Baudrate"]}},
    {"label": "Signal", "relx": 0.775, "rely": 0.005, "values": signalSelector},
    {"label": "Baudrate", "relx": 0.775, "rely": 0.005, "values": baudrate},
    {"label": "Channel", "relx": 0.075, "rely": 0.25, "values": channelOptions},
    {"label": "Amplitude", "relx": 0.6, "rely": 0.495, "values": amplitudeOperations},
    {"label": "Normalization", "relx": 0.6, "rely": 0.005, "values": normalizationMethods},
    {"label": "Resample", "relx": 0.6, "rely": 0.25, "values": resampleMethods}
]

source_entries = [
    {"name": "Duration", "placeholder": "Duration (s)", "relx": 0.25, "rely": 0.005},
    {"name": "Start", "placeholder": "Start (s)", "relx": 0.25, "rely": 0.25},
    {"name": "Shift", "placeholder": "Shift (s)", "relx": 0.25, "rely": 0.495},
    {"name": "Fa", "placeholder": "Analog Frequency (Hz)", "relx": 0.425, "rely": 0.005},
    {"name": "Fs", "placeholder": "Sampling Rate (Hz)", "relx": 0.425, "rely": 0.25},
    {"name": "Gain", "placeholder": "Gain", "relx": 0.425, "rely": 0.495},
]

operation_controls = [
    {"label": "Operation", "relx": 0.25, "rely": 0.005, "values": operationOptions, "dependents": {"Fourier Transform": ["Fourier"], "Cosine Transform": ["Cosine"], "Wavelet Transform": ["Wavelet"]}},
    {"label": "Fourier", "relx": 0.25, "rely": 0.25, "values": fourierOptions},
    {"label": "Cosine" , "relx":  0.25, "rely": 0.25, "values": cosineOptions},
    {"label": "Wavelet", "relx":  0.25, "rely": 0.25, "values": waveletOptions},
]
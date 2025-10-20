sourceOptions = ["Synthetic", "Board", "Dataset"]
signalSelector = ["Impulse", "Step", "Ramp", "Triangular", "Sawtooth", "Sine", "Cosine", "SinC", "Chirp"]
baudrate = ["9600", "115200", "230400", "460800", "921600"]
channelOptions = ["y1", "y2"]
basicOperation = ["y1 + y2", "y1 - y2", " y1 * y2", "y1 / y2", "y1 ** y2"]
amplitudeOperations = ["A*x(n)", "log(x(n))", "A^x(n)", "1/x(n)", "x(n)^k", "None"]
normalizationMethods = ["Normalization 0 & 1", "Normalization -1 & 1", "Standard normalization", "None"]
resampleMethods = ["Downsampling", "Upsampling", "None"]
operationOptions = ["Fourier Transform", "Cosine Transform", "Wavelet Transform"]
fourierOptions = ["DFT Magnitude/Phase", "DFT Filtering"]
cosineOptions = ["Cosine Magnitude", "Cosine Filtering"]
waveletOptions = ["db1", "db2", "db3", "db4", "db5", "db6"]
signalTypes = ["audio", "signal"]
fileTypes = [("JSON files", "*.json"), ("All files", "*.*")]
filterType = ["FIR Filter", "IIR Filter"]
default_h_parameters = "0.5  1  0.5  0  -0.5  -1  -0.5  0  0.5"
ax = [1.0, -2.474416174978162796804781464743427932262,  2.811006311911582233875606107176281511784, -1.703772240915468749733463482698425650597,  0.544432694888534296495663511450402438641, -0.072315669102958557434845943134860135615]

bx = [0.003279216306360205161751775193579305778 , 0.016396081531801026676120613956300076097 , 0.032792163063602053352241227912600152194 , 0.032792163063602053352241227912600152194 , 0.016396081531801026676120613956300076097 , 0.003279216306360205161751775193579305778 ]

feature_keys = [
    'Energy',
    'Power',
    'Mode',
    'Median',
    'Mean',
    'Variance',
    'Standard Deviation',
    'Minimum',
    'Maximum',
    'Skewness',
    'Kurtosis',
    'Entropy',
    'Dominant Frequency',
    'Sampling Frequency'
]

source_controls = [
    {"label": "Source", "relx": 0.075, "rely": 0.005, "values": sourceOptions, "dependents": {"Synthetic": ["Signal"], "Board": ["Baudrate"]}},
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
    {"label": "Filtering", "relx": 0.075, "rely": 0.005, "values": filterType},
    {"label": "Transform", "relx": 0.25, "rely": 0.005, "values": operationOptions, "dependents": {"Fourier Transform": ["Fourier"], "Cosine Transform": ["Cosine"], "Wavelet Transform": ["Wavelet"]}},
    {"label": "Fourier", "relx": 0.25, "rely": 0.25, "values": fourierOptions},
    {"label": "Cosine" , "relx":  0.25, "rely": 0.25, "values": cosineOptions},
    {"label": "Wavelet", "relx":  0.25, "rely": 0.25, "values": waveletOptions},
]
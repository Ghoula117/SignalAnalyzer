import json
import numpy as np
from tkinter import filedialog, messagebox
from core import settings

def load_signal(n0): 
    file_path = filedialog.askopenfilename(filetypes=settings.file_in_types)
    if not file_path:
        messagebox.showwarning("Warning", "No file selected")
        return None

    with open(file_path, 'r') as f:
        data = json.load(f)

    h = np.array(data["y1"])
    fs = int(data["fs"])

    nf = n0 + len(h) - 1
    n = np.linspace(n0, nf, len(h))

    return n, h, fs

def load_coeficients(): 
    file_path = filedialog.askopenfilename(filetypes=settings.file_in_types)
    if not file_path:
        messagebox.showwarning("Warning", "No file selected")
        return None

    with open(file_path, 'r') as f:
        data = json.load(f)

    ax = np.array(data["ax"])
    bx = np.array(data["bx"])

    return ax, bx

def save_signal(fs, y1, y2, y3):
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=settings.file_in_types)
    if not file_path:
        messagebox.showwarning("Warning", "No file selected")
        return
    
    metadata = {
        "fs": fs,
        "duration_y1_seg": len(y1) / fs,
        "duration_y2_seg": len(y2) / fs,
        "duration_y3_seg": len(y3) / fs,
        "y1": y1.tolist(), 
        "y2": y2.tolist(),
        "y3": y3.tolist(),
        "Created by": "Alejandro M.",
    }

    with open(file_path, "w") as f:
        json.dump(metadata, f, indent=4)

    messagebox.showinfo("Done", "File successfully saved")
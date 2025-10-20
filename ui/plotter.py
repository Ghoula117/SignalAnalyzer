# ui/plotter.py
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PlotFrame(ctk.CTkFrame):
    def __init__(self, parent, title="Gráfica", theme="dark"):
        super().__init__(parent)

        self.title = title
        self.theme = theme

        self.fg_color = "white"
        self.bg_color = "#1e1e1e"
        self.grid_color = "#444"

        # --- Crear figura y ejes ---
        plt.style.use("seaborn-v0_8-darkgrid")
        self.fig, self.ax = plt.subplots(figsize=(6, 2.5), dpi=100)
        self._apply_theme()

        # --- Integrar figura en CustomTkinter ---
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        widget = self.canvas.get_tk_widget()
        widget.configure(bg=self.bg_color, highlightthickness=0)
        widget.pack(fill="both", expand=True, padx=10, pady=10)

    # --- Aplicar esquema de color al gráfico ---
    def _apply_theme(self):
        self.fig.patch.set_facecolor(self.bg_color)
        self.ax.set_facecolor(self.bg_color)
        self.ax.tick_params(colors=self.fg_color)
        self.ax.title.set_color(self.fg_color)
        self.ax.grid(True, color=self.grid_color)
        self.ax.set_title(self.title)

    # --- Actualizar la gráfica ---
    def update_plot(self, x_data, y_data):

        if "Y1" in self.title.upper():
            color = "#FF0000" 
        elif "Y2" in self.title.upper():
            color = "#0080FF"  
        else:
            color = "#FFFFFF"

        # Limpiar y reconfigurar
        self.ax.clear()
        self._apply_theme()

        # Dibujar señal discreta
        markerline, stemlines, baseline  = self.ax.stem(
            x_data, y_data,
            linefmt=color,
            markerfmt="o",
            basefmt=" ",
        )

        plt.setp(stemlines, linewidth=1.5)
        plt.setp(markerline, markersize=4)

        # Ajustes visuales
        self.ax.axhline(0, color=self.grid_color, linestyle="--", linewidth=0.8)
        self.ax.set_xlim(min(x_data), max(x_data))

        # Redibujar
        self.canvas.draw()

class ProcessedSignalPlot:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(6, 2))
        self.ax.set_title("Processed Signal")

    def show(self, root, x_data, y_data):
        from tkinter import Toplevel
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        new_window = Toplevel(root)
        new_window.title("Processed Signal")
        new_window.geometry("700x250")

        self.ax.clear()


        self.ax.stem(x_data, y_data)
        self.ax.set_title("Processed Signal")
        self.ax.grid(True)
        self.ax.set_xlim([min(x_data), max(x_data)])

        if min(x_data) < 0 < max(x_data):
            self.ax.axvline(0, color='gray', linestyle='--')

        canvas = FigureCanvasTkAgg(self.fig, master=new_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
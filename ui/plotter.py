# ui/plotter.py
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PlotFrame(ctk.CTkFrame):
    def __init__(self, parent, title="Gráfica"):
        super().__init__(parent)

        self.title = title

        # --- Configurar figura matplotlib ---
        plt.style.use("seaborn-v0_8-darkgrid")
        self.fig, self.ax = plt.subplots(figsize=(5, 2.5), dpi=100)

        # Fondo oscuro compatible con CTk
        self.fig.patch.set_facecolor("#1e1e1e")
        self.ax.set_facecolor("#1e1e1e")
        self.ax.tick_params(colors="white")
        self.ax.title.set_color("white")
        self.ax.grid(True, color="#444")

        self.ax.set_title(self.title)

        # --- Integrar la figura en CustomTkinter ---
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        widget = self.canvas.get_tk_widget()
        widget.configure(bg="#1e1e1e", highlightthickness=0)
        widget.pack(fill="both", expand=True, padx=10, pady=10)

    def update_plot(self, x_data, y_data, color="C0"):
        """Actualiza la gráfica con nuevos datos."""
        self.ax.clear()
        self.ax.set_facecolor("#1e1e1e")
        self.ax.grid(True, color="#444")
        self.ax.tick_params(colors="white")
        self.ax.set_title(self.title, color="white")

        # Dibujar señal
        self.ax.plot(x_data, y_data, color=color, linewidth=1.5)
        self.ax.set_xlim(min(x_data), max(x_data))

        # Redibujar
        self.canvas.draw()

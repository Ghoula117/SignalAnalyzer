import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class PlotFrame(ctk.CTkFrame):
    def __init__(self, parent, title="Grafica"):
        super().__init__(parent, corner_radius=4)

        label = ctk.CTkLabel(self, text=title, font=("Arial", 16))
        label.pack(pady=5)

        self.figure = Figure(figsize=(4, 3), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.plot([], []) 

        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_plot(self, x, y, color="blue"):
        self.ax.clear()
        self.ax.plot(x, y, color=color)
        self.canvas.draw()

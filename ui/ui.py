import customtkinter as ctk
from core import math
from core.generation import signal_selector
from ui.plotter import PlotFrame
from core import settings

class AppUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Signal Analyzer")
        self.geometry("1000x600")

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)
        self.grid_columnconfigure((0, 1), weight=1)

        # --- Frame de configuración (arriba) ---
        self.settings_frame = SettingsFrame(self)
        self.settings_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # --- Plots (abajo) ---
        self.plot1 = PlotFrame(self, title=settings.channelOptions[0])
        self.plot1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.plot2 = PlotFrame(self, title=settings.channelOptions[1])
        self.plot2.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # --- Variables de señales ---
        self.y1 = None
        self.n1 = None  
        self.fs1 = None
        self.y2 = None
        self.n2 = None
        self.fs2 = None
        self.y3 = None
        self.n3 = None
        self.fs3 = None

        # Referencia circular: para que SettingsFrame acceda a AppUI
        self.settings_frame.main_app = self

class SettingsFrame(ctk.CTkTabview):
    def __init__(self, parent):
        super().__init__(parent, width=400, height=150)
        self.main_app = None
        self.grid(row=0, column=0, sticky="nsew")

        # Crear tabs
        self.add("Source")
        self.add("Operation")
        self.add("Statistics")

        self.set("Source")

        # Llamar constructores de cada pestaña
        self._create_tab_source()
        self._create_tab_operation()
        self._create_tab_statistics()

    # --- SOURCE TAB ---
    def _create_tab_source(self):
        tab = self.tab("Source")

        self.entry_vars = {}
        self.combo_vars = {}
        self.dynamic_widgets = {}
        self.active_dependents = {} 

        for config in settings.source_controls:
            placeholder = config.get("placeholder", config["label"])
            var = ctk.StringVar(value=placeholder)

            combo = ctk.CTkComboBox(
                tab,
                values=config["values"],
                variable=var,
                state="readonly",
                width=150,
                command=lambda selected, label=config["label"]: self._on_selection_change(label, selected),
            )
            combo.set(placeholder)
            self.dynamic_widgets[config["label"]] = combo

            if not self._is_dependent(config["label"]):
                combo.place(relx=config["relx"], rely=config["rely"], anchor="n")
                self.combo_vars[config["label"]] = var
            else:
                combo.place_forget()

        for config in settings.source_entries:
            entry = ctk.CTkEntry(tab, placeholder_text=config["placeholder"], width=150)
            entry.place(relx=config["relx"], rely=config["rely"], anchor="n")
            self.entry_vars[config["name"]] = entry

        self.btn_synthetic = ctk.CTkButton(tab, text="Generate", command=self._generate_signal)
        ctk.CTkButton(tab, text="Set Signal", command=self._generate_signal).place(relx=0.775, rely=0.25, anchor="n")

        ctk.CTkButton(tab, text="Get Output", command=self._output_channel).place(relx=0.775, rely=0.495, anchor="n")

    # --- OPERATION TAB ---
    def _create_tab_operation(self):
        tab = self.tab("Operation")

        ctk.CTkLabel(tab, text="Basic").place(relx=0.075, rely=0.005, anchor="n")
        ctk.CTkButton(tab, text="FIR Filter").place(relx=0.075, rely=0.005, anchor="n")
        ctk.CTkButton(tab, text="IIR Filter").place(relx=0.075, rely=0.25, anchor="n")

        option = ctk.StringVar(value="Parameters")
        radio_texts = [("Load", 0.06), ("Set", 0.14)]
        for text, relx in radio_texts:
            ctk.CTkRadioButton(tab, text=text, variable=option, value=text).place(relx=relx, rely=0.495, anchor="n")

        ctk.CTkButton(tab, text="Clear Parameters").place(relx=0.075, rely=0.74, anchor="n")

        for config in settings.operation_controls:
            placeholder = config.get("placeholder", config["label"])
            var = ctk.StringVar(value=placeholder)
            combo = ctk.CTkComboBox(
                tab,
                values=config["values"],
                variable=var,
                state="readonly",
                width=150,
                command=lambda selected, label=config["label"]: self._on_selection_change(label, selected),
            )
            combo.set(placeholder)
            self.dynamic_widgets[config["label"]] = combo

            if not self._is_dependent(config["label"]):
                combo.place(relx=config["relx"], rely=config["rely"], anchor="n")
                self.combo_vars[config["label"]] = var
            else:
                combo.place_forget()

        operation_var = ctk.StringVar(value="Operation")
        operation_combo = ctk.CTkComboBox(
            tab,
            values=settings.basicOperation,
            variable=operation_var,
            state="readonly",
            width=150,
            command=lambda selected, label=config["label"]: self._on_selection_change(label, selected)
        )
        operation_combo.set("Operation")
        operation_combo.place(relx=0.75, rely=0.35, anchor="center")
        self.dynamic_widgets["Operation"] = operation_combo
        self.combo_vars["Operation"] = operation_var
        
        ctk.CTkButton(tab, text="Operate", command=self._operate_signals).place(relx=0.425, rely=0.005, anchor="n")

    # --- STATISTICS TAB ---
    def _create_tab_statistics(self):
        tab = self.tab("Statistics")
        entry_cutoff = ctk.CTkEntry(tab, placeholder_text="Frecuencia de corte (Hz)")
        entry_cutoff.pack(padx=20, pady=10)

    def _is_dependent(self, label):
        all_controls = settings.source_controls + settings.operation_controls
        for cfg in all_controls:
            deps = cfg.get("dependents", {})
            if isinstance(deps, dict):
                for dep_list in deps.values():
                    if label in dep_list:
                        return True
        return False

    def _on_selection_change(self, label, selected):
        # Determinar si el evento viene de SOURCE o OPERATION
        if label in [cfg["label"] for cfg in settings.source_controls]:
            configs = settings.source_controls
        elif label in [cfg["label"] for cfg in settings.operation_controls]:
            configs = settings.operation_controls

        # Remover dependientes anteriores de este label
        self._remove_dependents_of(label)

        parent_cfg = next(cfg for cfg in configs if cfg["label"] == label)
        dependents = parent_cfg.get("dependents", {}).get(selected, [])

        # Mostrar los dependientes asociados
        if dependents:
            self.active_dependents[label] = dependents
            for dep_label in dependents:
                dep_cfg = next(cfg for cfg in configs if cfg["label"] == dep_label)
                combo = self.dynamic_widgets[dep_label]
                combo.place(relx=dep_cfg["relx"], rely=dep_cfg["rely"], anchor="n")
                self.combo_vars[dep_label] = combo.cget("variable")
        
        if self.combo_vars.get("Source") and self.combo_vars.get("Source").get() == settings.sourceOptions[0]:
            self.btn_synthetic.place(relx=0.775, rely=0.25, anchor="center")
        else:
            self.btn_synthetic.place_forget()

    def _remove_dependents_of(self, label):
        deps = self.active_dependents.pop(label, [])
        for dep_label in deps:
            combo = self.dynamic_widgets.get(dep_label)
            if combo:
                combo.place_forget()
            self.combo_vars.pop(dep_label, None)

    def _generate_signal(self):
        data = {}

        for label, combo in self.dynamic_widgets.items():
            try:
                data[label] = combo.get()
            except Exception:
                data[label] = None


        # Recolectar valores de entradas
        for name, entry in self.entry_vars.items():
            data[name] = entry.get()

        print("\n📊 Datos recopilados:")
        for k, v in data.items():
            print(f"  {k}: {v}")

        n, y = signal_selector(
            name=data.get("Signal"),
            fa=float(data.get("Fa")),
            fs=int(data.get("Fs")),
            gain=float(data.get("Gain")),
            n0=int(data.get("Start")),
            duration=int(data.get("Duration")),
            shift=int(data.get("Shift")),
        )

        app = self.main_app
        output = data.get("Channel")
        if output == settings.channelOptions[0]:
            app.y1 = y
            app.n1 = n
            app.fs1 = int(data.get("Fs"))
            app.plot1.update_plot(n, y)
        elif output == settings.channelOptions[1]:
            app.y2 = y
            app.n2 = n
            app.fs2 = int(data.get("Fs"))
            app.plot2.update_plot(n, y)

        return data
    
    def _operate_signals(self):
        app = self.main_app
        app.n3, app.y3, app.fs3 = math.basic_operations(self.dynamic_widgets.get("Operation").get(), app.y1, app.fs1, app.n1, app.y2, app.fs2, app.n2)

    def _output_channel(self):
        app = self.main_app
        data = {}

        target_channel = data.get("Channel")
        if target_channel == settings.channelOptions[0]:
            source_signal = app.y1
        elif target_channel == settings.channelOptions[1]:
            source_signal = app.y2
        if source_signal is None:
            return
        
        n = list(range(len(source_signal)))  # eje temporal genérico

        if target_channel.lower() ==  settings.channelOptions[0]:
            app.y1 = source_signal
            app.plot1.update_plot(n, source_signal)
        elif target_channel.lower() == settings.channelOptions[1]:
            app.y2 = source_signal
            app.plot2.update_plot(n, source_signal)
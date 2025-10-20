import customtkinter as ctk
from tkinter import messagebox
from core import math, signal_utils, file_manager, settings
from core.generation import signal_selector
from ui.plotter import PlotFrame

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

        self.set("Source")

        # Llamar constructores de cada pestaña
        self._create_tab_source()
        self._create_tab_operation()

    # --- SOURCE TAB ---
    def _create_tab_source(self):
        app = self.main_app
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

        ctk.CTkButton(tab, text="Set Signal", command=self._generate_signal).place(relx=0.775, rely=0.25, anchor="n")
        ctk.CTkButton(tab, text="Get Output", command=self._apply_output_channel).place(relx=0.775, rely=0.495, anchor="n")

    # --- OPERATION TAB ---
    def _create_tab_operation(self):
        tab = self.tab("Operation")

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

        convolution_var = ctk.StringVar(value="Convolution")
        convolution_combo = ctk.CTkComboBox(
            tab,
            values=settings.filterType,
            variable=convolution_var,
            state="readonly",
            width=150,
            command=lambda selected, label=config["label"]: self._on_selection_change(label, selected)
        )
        convolution_combo.set("Convolution")
        convolution_combo.place(relx=0.075, rely=0.005, anchor="n")
        self.dynamic_widgets["Convolution"] = convolution_combo
        self.combo_vars["Convolution"] = convolution_var

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
        operation_combo.place(relx=0.425, rely=0.005, anchor="n")
        self.dynamic_widgets["Operation"] = operation_combo
        self.combo_vars["Operation"] = operation_var
        
        ctk.CTkButton(tab, text="Operate", command=self._operate_signals).place(relx=0.425, rely=0.25, anchor="n")
        ctk.CTkButton(tab, text="Apply Convolution", command=self._apply_convolution).place(relx=0.075, rely=0.25, anchor="n")
        ctk.CTkButton(tab, text="Apply Transform", command=self._apply_transforms).place(relx=0.25, rely=0.495, anchor="n")
        ctk.CTkButton(tab, text="Statistics", command=self._apply_statistics).place(relx=0.25, rely=0.495, anchor="n")

    def _is_dependent(self, label):
        all_controls = settings.source_controls + settings.operation_controls
        for cfg in all_controls:
            deps = cfg.get("dependents", {})
            if isinstance(deps, dict):
                for dep_list in deps.values():
                    if label in dep_list:
                        return True
        return False

    def _remove_dependents_of(self, label):
        deps = self.active_dependents.pop(label, [])
        for dep_label in deps:
            combo = self.dynamic_widgets.get(dep_label)
            if combo:
                combo.place_forget()
            self.combo_vars.pop(dep_label, None)

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

    def _collect_signal_parameters(self):
        data = {}

        # --- Obtener combos dinámicos ---
        for label, combo in self.dynamic_widgets.items():
            try:
                data[label] = combo.get()
            except Exception:
                data[label] = None

        # --- Obtener entradas numéricas ---
        for name, entry in self.entry_vars.items():
            try:
                val = entry.get()
                # Intentar convertir a número si aplica
                if val.replace('.', '', 1).isdigit():
                    val = float(val) if '.' in val else int(val)
                data[name] = val
            except Exception:
                data[name] = None

        # --- Verificar canal de salida ---
        output_channel = data.get("Channel")
        if output_channel not in settings.channelOptions:
            output_channel = settings.channelOptions[0]  # fallback

        data["OutputChannel"] = output_channel
        return data

    def _apply_processing(self, y, n, fs, n0, duration, signal_type):
        amp_op = self.dynamic_widgets.get("Amplitude").get()
        if amp_op != "None" and amp_op != "Amplitude":

            y = signal_utils.amplitud_selector(amp_op, y)

        # --- 2. Normalización ---
        norm_op = self.dynamic_widgets.get("Normalization").get()
        if norm_op and norm_op != "None" and norm_op != "Normalization":

            y = signal_utils.preprocessing_operations(norm_op, y)

        # --- 3. Remuestreo ---
        resample_op = self.dynamic_widgets.get("Resample").get()
        if resample_op != "None" and resample_op != "Resample":
            n, y = signal_utils.time_sampling(resample_op, y, fs, n0, duration, signal_type)

        return n, y, fs

    def _apply_transforms(self):
        app = self.main_app
        data = self._collect_signal_parameters()

        if data.get("Transform") == settings.operationOptions[0]:  #Fourier
            operation=data.get("Fourier")
            math.fourier_operation(operation, x=app.y1, fs1=app.fs1, h=app.y2, fs2=app.fs2)

        elif data.get("Transform") == settings.operationOptions[1]: #Cosine
            operation=data.get("Cosine")
            math.cosine_operation(operation, x=app.y1, fs1=app.fs1, h=app.y2, fs2=app.fs2)

        elif data.get("Transform") == settings.operationOptions[2]: #Wavelet
            Woperation=data.get("Wavelet")
            if app.y1 is not None:
                math.wavelet_transform(app.y1, Woperation, level=3)
            else:
                messagebox.showwarning("Warning", "No signal available for Wavelet transform.")

    def _apply_statistics(self):
        app = self.main_app
        signal_utils.stadistics(app.y1, app.fs1, app.y2, app.fs2, app.y3, app.fs3)

    def _generate_signal(self):
        data = self._collect_signal_parameters()

        if data.get("Source") == settings.sourceOptions[0]:  # synthetic
            n, y = signal_selector(
                name=data.get("Signal"),
                fa=float(data.get("Fa")),
                fs=int(data.get("Fs")),
                gain=float(data.get("Gain")),
                n0=int(data.get("Start")),
                duration=float(data.get("Duration")),
                shift=float(data.get("Shift")),
            )
            fs=int(data.get("Fs"))
            n0=int(data.get("Start"))
            duration=float(data.get("Duration"))
            signal_type=settings.signalTypes[0]  # synthetic

            n, y, fs = self._apply_processing(y, n, fs, n0, duration, signal_type)
            self._apply_signal_to_channel(n, y, int(data.get("Fs", 1000)), int(data.get("Start", 0)), data)

        elif data.get("Source") == "board":
            # Aquí podrías leer datos desde el ADC, UART, etc.
            # y luego pasarlos también a apply_signal_to_channel(...)
            pass

        elif data.get("Source") == settings.sourceOptions[2]:
            n0=int(data.get("Start"))
            signal_type=settings.signalTypes[0]
            try:
                n, y, fs = file_manager.load_signal(n0)
                duration = len(y)
                n, y, fs = self._apply_processing(y, n, fs, n0, duration, signal_type)
                self._apply_signal_to_channel(n, y, fs, n0, data)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load dataset")
                return

        print("\n📊 Parámetros usados:")
        for k, v in data.items():
            print(f"  {k}: {v}")

    def _operate_signals(self):
        app = self.main_app
        app.n3, app.y3, app.fs3 = math.basic_operations(self.dynamic_widgets.get("Operation").get(), app.y1, app.fs1, app.n1[0], app.y2, app.fs2, app.n2[0])

    def _apply_convolution(self):
        app = self.main_app
        action = self.dynamic_widgets.get("Convolution").get()
        
        app.n3, app.y3, app.fs3 = math.filtering_operation(
            action,
            x=app.y1,
            nx0=app.n1[0],
            fs1=app.fs1,
            h=app.y2,
            nh0=app.n2[0],
            fs2=app.fs2
        )

    def _apply_output_channel(self):
        app = self.main_app
        data = {}

        target_channel = self.dynamic_widgets.get("Channel").get()
        if target_channel == settings.channelOptions[0]:
            app.y1, app.n1, app.fs1 = app.y3, app.n3, app.fs3
            app.plot1.update_plot(app.n1, app.y1)
        elif target_channel == settings.channelOptions[1]:
            app.y2, app.n2, app.fs2 = app.y3, app.n3, app.fs3
            app.plot2.update_plot(app.n2, app.y2)

    def _apply_signal_to_channel(self, n, y, fs, n0, data):
        app = self.main_app
        output = self.dynamic_widgets.get("Channel").get()

        if output == settings.channelOptions[0]:
            app.y1, app.n1, app.fs1 = y, n, fs
            app.plot1.update_plot(n, y)
        elif output == settings.channelOptions[1]:
            app.y2, app.n2, app.fs2 = y, n, fs
            app.plot2.update_plot(n, y)
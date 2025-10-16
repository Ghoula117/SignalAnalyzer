import customtkinter as ctk
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

        settings_frame = SettingsFrame(self)
        settings_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        plot1 = PlotFrame(self, title="Gráfica 1")
        plot1.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        plot2 = PlotFrame(self, title="Gráfica 2")
        plot2.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

class SettingsFrame(ctk.CTkTabview):
    def __init__(self, parent):
        super().__init__(parent, width=400, height=150)
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

        ctk.CTkButton(
            tab, text="Aplicar Configuración", command=self.collect_all_values
        ).place(relx=0.75, rely=0.85, anchor="center")


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

    # --- STATISTICS TAB ---
    def _create_tab_statistics(self):
        tab = self.tab("Statistics")
        entry_cutoff = ctk.CTkEntry(tab, placeholder_text="Frecuencia de corte (Hz)")
        entry_cutoff.pack(padx=20, pady=10)

    # ------------------- DEPENDENCIAS -------------------
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
        print(f"🔁 Cambio en {label}: {selected}")

        # Determinar si el evento viene de SOURCE o OPERATION
        if label in [cfg["label"] for cfg in settings.source_controls]:
            configs = settings.source_controls
        elif label in [cfg["label"] for cfg in settings.operation_controls]:
            configs = settings.operation_controls
        else:
            print(f"⚠️ No se encontró configuración para {label}")
            return

        # Remover dependientes anteriores de este label
        self._remove_dependents_of(label)

        # Buscar configuración del padre
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

    def _remove_dependents_of(self, label):
        deps = self.active_dependents.pop(label, [])
        for dep_label in deps:
            combo = self.dynamic_widgets.get(dep_label)
            if combo:
                combo.place_forget()
            self.combo_vars.pop(dep_label, None)

    # ------------------- RECOLECCIÓN -------------------
    def collect_all_values(self):
        data = {}
        for label, var in self.combo_vars.items():
            if isinstance(var, str):
                data[label] = self.nametowidget(var).get()
            else:
                data[label] = var.get()

        for name, entry in self.entry_vars.items():
            data[name] = entry.get()

        print("\n Datos recopilados:")
        for k, v in data.items():
            print(f"  {k}: {v}")
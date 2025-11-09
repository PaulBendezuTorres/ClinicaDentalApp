# gui/ventana_formulario_paciente.py (VERSIÓN CON CENTRADO)

import ttkbootstrap as ttk
from tkinter import messagebox

class VentanaFormularioPaciente(ttk.Toplevel):
    def __init__(self, parent, callback, paciente_existente=None):
        title = "Editar Paciente" if paciente_existente else "Agregar Nuevo Paciente"
        super().__init__(title=title)
        
        self.transient(parent)
        self.grab_set()

        self.callback = callback
        self.paciente_existente = paciente_existente
        self.result = None

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill="both")

        campos = ["Nombre Completo", "DNI", "Teléfono", "Correo Electrónico", "Dirección"]
        self.entries = {}
        for i, campo in enumerate(campos):
            ttk.Label(main_frame, text=f"{campo}:").grid(row=i, column=0, sticky="w", padx=5, pady=8)
            entry = ttk.Entry(main_frame, width=40)
            entry.grid(row=i, column=1, sticky="ew", padx=5)
            self.entries[campo] = entry

        ttk.Label(main_frame, text="Género:").grid(row=len(campos), column=0, sticky="w", padx=5, pady=8)
        self.cmb_genero = ttk.Combobox(main_frame, state="readonly", values=["Masculino", "Femenino", "Otro"])
        self.cmb_genero.grid(row=len(campos), column=1, sticky="ew", padx=5)
        
        main_frame.columnconfigure(1, weight=1)
        
        if self.paciente_existente:
            self._rellenar_formulario()
        else: # Ponemos un valor por defecto al crear
            self.cmb_genero.set("Masculino")

        btn_frame = ttk.Frame(main_frame, padding=(0, 15))
        btn_frame.grid(row=len(campos)+1, column=0, columnspan=2, sticky="e")
        ttk.Button(btn_frame, text="Guardar", command=self._on_guardar, bootstyle="success").pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy, bootstyle="secondary").pack(side="right")

        # --- CAMBIO CLAVE: Llamamos a la función de centrado ---
        self._centrar_ventana(parent)

    # --- NUEVA FUNCIÓN PARA CENTRAR LA VENTANA ---
    def _centrar_ventana(self, parent):
        self.update_idletasks() # Asegura que las dimensiones de la ventana estén actualizadas

        # Coordenadas y tamaño de la ventana padre
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        # Tamaño de esta ventana modal
        my_width = self.winfo_width()
        my_height = self.winfo_height()

        # Calcular la posición para centrar
        x = parent_x + (parent_width // 2) - (my_width // 2)
        y = parent_y + (parent_height // 2) - (my_height // 2)

        self.geometry(f"+{x}+{y}")

    def _rellenar_formulario(self):
        # Usamos el truco 'valor or ""' que convierte None en una cadena vacía.
        nombre_val = self.paciente_existente.get("nombre", "") or ""
        dni_val = self.paciente_existente.get("dni", "") or ""
        telefono_val = self.paciente_existente.get("telefono", "") or ""
        correo_val = self.paciente_existente.get("correo", "") or ""
        direccion_val = self.paciente_existente.get("direccion", "") or ""
        genero_val = self.paciente_existente.get("genero", "Otro") or "Otro"

        # Ahora insertamos los valores, garantizando que son cadenas
        self.entries["Nombre Completo"].insert(0, nombre_val)
        self.entries["DNI"].insert(0, dni_val)
        self.entries["Teléfono"].insert(0, telefono_val)
        self.entries["Correo Electrónico"].insert(0, correo_val)
        self.entries["Dirección"].insert(0, direccion_val)
        self.cmb_genero.set(genero_val)

    def _on_guardar(self):
        # ... (este método no cambia)
        self.result = {
            "nombre": self.entries["Nombre Completo"].get().strip(),
            "telefono": self.entries["Teléfono"].get().strip(),
            "dni": self.entries["DNI"].get().strip(),
            "direccion": self.entries["Dirección"].get().strip(),
            "correo": self.entries["Correo Electrónico"].get().strip(),
            "genero": self.cmb_genero.get()
        }
        if not self.result["nombre"] or not self.result["telefono"] or not self.result["dni"]:
            messagebox.showwarning("Campos incompletos", "Nombre, DNI y Teléfono son obligatorios.", parent=self)
            self.result = None
            return

        if self.paciente_existente:
            self.result["id"] = self.paciente_existente["id"]

        self.destroy()
        self.callback(self.result)
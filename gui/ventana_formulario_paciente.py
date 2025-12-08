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

        # Frame principal con más padding
        main_frame = ttk.Frame(self, padding=25)
        main_frame.pack(expand=True, fill="both")

        # --- Frame para los campos del formulario ---
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="x", expand=True)

        # --- Creación de una cuadrícula de 4 columnas ---
        form_frame.columnconfigure((1, 3), weight=1)

        self.entries = {}
        
        # --- Fila 0: Nombre Completo (ocupa las 4 columnas) ---
        ttk.Label(form_frame, text="Nombre Completo:").grid(row=0, column=0, sticky="w", padx=5, pady=10)
        e_nombre = ttk.Entry(form_frame, width=40)
        e_nombre.grid(row=0, column=1, columnspan=3, sticky="ew", padx=5, pady=10)
        self.entries["Nombre Completo"] = e_nombre

        # --- Fila 1: DNI y Teléfono (dos columnas) ---
        ttk.Label(form_frame, text="DNI:").grid(row=1, column=0, sticky="w", padx=5, pady=10)
        e_dni = ttk.Entry(form_frame)
        e_dni.grid(row=1, column=1, sticky="ew", padx=5, pady=10)
        self.entries["DNI"] = e_dni

        ttk.Label(form_frame, text="Teléfono:").grid(row=1, column=2, sticky="w", padx=(15, 5), pady=10)
        e_tel = ttk.Entry(form_frame)
        e_tel.grid(row=1, column=3, sticky="ew", padx=5, pady=10)
        self.entries["Teléfono"] = e_tel

        # --- Fila 2: Correo Electrónico (ocupa las 4 columnas) ---
        ttk.Label(form_frame, text="Correo Electrónico:").grid(row=2, column=0, sticky="w", padx=5, pady=10)
        e_correo = ttk.Entry(form_frame)
        e_correo.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=10)
        self.entries["Correo Electrónico"] = e_correo
        
        # --- Fila 3: Dirección (ocupa las 4 columnas) ---
        ttk.Label(form_frame, text="Dirección:").grid(row=3, column=0, sticky="w", padx=5, pady=10)
        e_dir = ttk.Entry(form_frame)
        e_dir.grid(row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=10)
        self.entries["Dirección"] = e_dir

        # --- Fila 4: Género (ocupa 2 columnas) ---
        ttk.Label(form_frame, text="Género:").grid(row=4, column=0, sticky="w", padx=5, pady=10)
        self.cmb_genero = ttk.Combobox(form_frame, state="readonly", values=["Masculino", "Femenino", "Otro"])
        self.cmb_genero.grid(row=4, column=1, sticky="ew", padx=5, pady=10)
        
        # --- Frame para los botones (pie de página) ---
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(side="bottom", fill="x", pady=(20, 0))

        ttk.Separator(footer_frame).pack(fill="x", pady=(0, 10))

        btn_container = ttk.Frame(footer_frame)
        btn_container.pack(side="right")

        ttk.Button(btn_container, text="Guardar", command=self._on_guardar, bootstyle="success").pack(side="right", padx=(10, 0))
        ttk.Button(btn_container, text="Cancelar", command=self.destroy, bootstyle="light-outline").pack(side="right")

        # --- Lógica final ---
        if self.paciente_existente:
            self._rellenar_formulario()
        else:
            self.cmb_genero.set("Masculino")

        self._centrar_ventana(parent)

   
    def _centrar_ventana(self, parent):
        self.update_idletasks() 

        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        my_width = self.winfo_width()
        my_height = self.winfo_height()

        x = parent_x + (parent_width // 2) - (my_width // 2)
        y = parent_y + (parent_height // 2) - (my_height // 2)

        self.geometry(f"+{x}+{y}")

    def _rellenar_formulario(self):
        self.entries["Nombre Completo"].insert(0, self.paciente_existente.get("nombre") or "")
        self.entries["DNI"].insert(0, self.paciente_existente.get("dni") or "")
        self.entries["Teléfono"].insert(0, self.paciente_existente.get("telefono") or "")
        self.entries["Correo Electrónico"].insert(0, self.paciente_existente.get("correo") or "")
        self.entries["Dirección"].insert(0, self.paciente_existente.get("direccion") or "")
        self.cmb_genero.set(self.paciente_existente.get("genero") or "Otro")

    def _on_guardar(self):
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
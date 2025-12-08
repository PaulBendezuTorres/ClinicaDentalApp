import ttkbootstrap as ttk
from tkinter import messagebox
from logic.sistema import sistema  
from ttkbootstrap.scrolled import ScrolledFrame
from gui.ventana_formulario_paciente import VentanaFormularioPaciente
from gui.ventana_historial_paciente import VentanaHistorialPaciente

class PacienteCard(ttk.Frame):
    def __init__(self, parent, paciente_data, edit_callback, delete_callback):
        super().__init__(parent, padding=15, bootstyle="secondary")
        self.paciente_data = paciente_data
        
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=0)

        # Icono
        genero_iconos = {"Masculino": "👨", "Femenino": "👩", "Otro": "👤"}
        icono_char = genero_iconos.get(paciente_data.get("genero", "Otro"), "👤")
        icono = ttk.Label(self, text=icono_char, font=("Segoe UI", 36), bootstyle="light")
        icono.grid(row=0, column=0, rowspan=2, padx=(0, 20), sticky="ns")

        # Info
        info_frame = ttk.Frame(self, bootstyle="secondary")
        info_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        info_frame.columnconfigure(0, weight=1)

        nombre = ttk.Label(info_frame, text=paciente_data["nombre"], font=("Segoe UI", 16, "bold"), bootstyle="light", anchor="w")
        nombre.pack(fill="x", pady=(0, 5))
        
        dni_texto = f"DNI: {paciente_data.get('dni', 'N/A')}"
        dni = ttk.Label(info_frame, text=dni_texto, font=("Segoe UI", 10), bootstyle="info", anchor="w")
        dni.pack(fill="x")
        
        # Botones
        botones_frame = ttk.Frame(self, bootstyle="secondary")
        botones_frame.grid(row=0, column=2, rowspan=2, sticky="e", padx=(20, 0))
        
        ttk.Button(botones_frame, text="Historial", command=self._ver_historial, bootstyle="light-outline").pack(pady=2, fill="x")
        ttk.Button(botones_frame, text="Editar", command=lambda: edit_callback(paciente_data), bootstyle="info-outline").pack(pady=2, fill="x")
        
        if delete_callback:
            ttk.Button(botones_frame, text="Eliminar", command=lambda: delete_callback(paciente_data), bootstyle="danger-outline").pack(pady=2, fill="x")

    def _ver_historial(self):
        VentanaHistorialPaciente(self, self.paciente_data)


class PaginaPacientes(ttk.Frame):
    def __init__(self, parent, usuario_data=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self._build()

    def _build(self):
        main_frame = ttk.Frame(self, padding=(20, 10))
        main_frame.pack(fill="both", expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(header_frame, text="Gestión de Pacientes", font=("Segoe UI", 18, "bold"), bootstyle="light").pack(side="left")
        
        right_header = ttk.Frame(header_frame)
        right_header.pack(side="right")

        self.ent_buscar = ttk.Entry(right_header, width=30)
        self.ent_buscar.pack(side="left", padx=(0, 5))
        self.ent_buscar.bind("<Return>", lambda event: self._cargar_pacientes()) 
        self.ent_buscar.bind("<KeyRelease>", lambda event: self._cargar_pacientes())

        btn_buscar = ttk.Button(right_header, text="🔍", command=self._cargar_pacientes, bootstyle="secondary-outline")
        btn_buscar.pack(side="left", padx=(0, 15))

        ttk.Button(right_header, text="✚ Nuevo Paciente", command=self._abrir_formulario_creacion, bootstyle="success").pack(side="left")
        
        self.canvas_pacientes = ScrolledFrame(main_frame, autohide=True, bootstyle="dark")
        self.canvas_pacientes.pack(fill="both", expand=True)
        
        self.cards_container = ttk.Frame(self.canvas_pacientes, bootstyle="dark")
        self.cards_container.pack(fill="x", expand=True, padx=30, pady=10)
        self.cards_container.columnconfigure((0, 1), weight=1)

        self._cargar_pacientes()

    def _abrir_formulario_creacion(self):
        def on_form_close(data):
            if data:
                try:
                    # SERVICIO PACIENTE
                    sistema.paciente.crear(data["nombre"], data["telefono"], data["dni"], data["direccion"], data["correo"], data["genero"])
                    self._cargar_pacientes()
                except Exception as e: messagebox.showerror("Error al guardar", str(e), parent=self)
        VentanaFormularioPaciente(self, on_form_close)

    def _abrir_formulario_edicion(self, paciente_a_editar):
        def on_form_close(data):
            if data:
                try:
                    # SERVICIO PACIENTE
                    sistema.paciente.actualizar(data["id"], data["nombre"], data["telefono"], data["dni"], data["direccion"], data["correo"], data["genero"])
                    self._cargar_pacientes()
                except Exception as e: messagebox.showerror("Error al actualizar", str(e), parent=self)
        VentanaFormularioPaciente(self, on_form_close, paciente_existente=paciente_a_editar)

    def _eliminar_paciente(self, paciente_data):
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas eliminar a {paciente_data['nombre']}?",
            parent=self
        )
        if confirmacion:
            try:
                # SERVICIO PACIENTE
                sistema.paciente.eliminar(paciente_data['id'])
                messagebox.showinfo("Éxito", "Paciente eliminado correctamente.", parent=self)
                self._cargar_pacientes() 
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}", parent=self)

    def _cargar_pacientes(self):
        for widget in self.cards_container.winfo_children(): widget.destroy()

        filtro = self.ent_buscar.get().strip()
        # SERVICIO PACIENTE
        lista_pacientes = sistema.paciente.obtener_todos(filtro)
        
        if not lista_pacientes:
            msg = "No se encontraron pacientes." if filtro else "No hay pacientes registrados."
            ttk.Label(self.cards_container, text=msg, font=("Segoe UI", 12), bootstyle="light").pack(pady=50)
        else:
            COLS = 2
            es_admin = self.usuario_data and self.usuario_data.get('rol') == 'admin'
            callback_eliminar = self._eliminar_paciente if es_admin else None

            for i, p in enumerate(lista_pacientes):
                fila = i // COLS
                col = i % COLS
                card = PacienteCard(self.cards_container, p, self._abrir_formulario_edicion, callback_eliminar)
                card.grid(row=fila, column=col, padx=10, pady=10, sticky="nsew")
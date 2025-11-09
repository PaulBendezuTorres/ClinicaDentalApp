import ttkbootstrap as ttk
from tkinter import messagebox
from logic import controlador
from ttkbootstrap.scrolled import ScrolledFrame
from gui.ventana_formulario_paciente import VentanaFormularioPaciente 
from gui.ventana_historial_paciente import VentanaHistorialPaciente 

class PacienteCard(ttk.Frame):
    def __init__(self, parent, paciente_data, edit_callback):
        super().__init__(parent, padding=15, bootstyle="secondary") # Cambiado a secondary para un fondo más oscuro
        self.paciente_data = paciente_data
        
        # Configuramos 3 columnas: Icono, Info, Botones
        self.columnconfigure(0, weight=0) # Icono (no se expande)
        self.columnconfigure(1, weight=1) # Info (se expande para tomar el espacio)
        self.columnconfigure(2, weight=0) # Botones (no se expande)

        # --- Icono ---
        genero_iconos = {"Masculino": "👨", "Femenino": "👩", "Otro": "👤"}
        icono_char = genero_iconos.get(paciente_data.get("genero", "Otro"), "👤")
        icono = ttk.Label(self, text=icono_char, font=("Segoe UI", 36), bootstyle="light") # Icono más grande
        icono.grid(row=0, column=0, rowspan=2, padx=(0, 20), sticky="ns") # Mayor padding a la derecha

        # --- Información del Paciente (Nombre y DNI) ---
        info_frame = ttk.Frame(self, bootstyle="secondary") # Un frame para contener nombre y DNI
        info_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        info_frame.columnconfigure(0, weight=1) # Para que el contenido del info_frame se expanda

        nombre = ttk.Label(info_frame, text=paciente_data["nombre"], font=("Segoe UI", 16, "bold"), bootstyle="light", anchor="w") # Nombre más grande
        nombre.pack(fill="x", pady=(0, 5)) # Un poco de padding debajo del nombre
        
        dni = ttk.Label(info_frame, text=f"DNI: {paciente_data.get('dni', 'N/A')}", font=("Segoe UI", 10), bootstyle="info", anchor="w") # DNI con estilo info
        dni.pack(fill="x")
        
        # --- Botones ---
        botones_frame = ttk.Frame(self, bootstyle="secondary")
        botones_frame.grid(row=0, column=2, rowspan=2, sticky="e", padx=(20, 0)) # Sticky "e" para alinear a la derecha
        ttk.Button(botones_frame, text="Editar", command=lambda: edit_callback(paciente_data), bootstyle="info-outline").pack(pady=5, fill="x") # Botones con outline
        ttk.Button(botones_frame, text="Historial", command=self._ver_historial, bootstyle="light-outline").pack(pady=5, fill="x")

    def _ver_historial(self):
        VentanaHistorialPaciente(self, self.paciente_data)


class PaginaPacientes(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()
        
    def _build(self):
        main_frame = ttk.Frame(self, padding=(20, 10))
        main_frame.pack(fill="both", expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        ttk.Label(header_frame, text="Gestión de Pacientes", font=("Segoe UI", 18, "bold"), bootstyle="light").pack(side="left") # Título con bootstyle light
        ttk.Button(header_frame, text="✚ Agregar Nuevo Paciente", command=self._abrir_formulario_creacion, bootstyle="success-outline").pack(side="right") # Botón outline success
        
        self.canvas_pacientes = ScrolledFrame(main_frame, autohide=True, bootstyle="dark") # ScrolledFrame con estilo dark
        self.canvas_pacientes.pack(fill="both", expand=True)
        
        self.canvas_pacientes.rowconfigure(0, weight=1)
        self.canvas_pacientes.columnconfigure(0, weight=1)

        self.cards_container = ttk.Frame(self.canvas_pacientes, bootstyle="dark") # Contenedor de tarjetas con estilo dark
        self.cards_container.grid(row=0, column=0, padx=30, pady=30, sticky="nsew") # Sticky "nsew" para que se estire
        
        # Es importante que el cards_container tenga sus columnas configuradas
        self.cards_container.columnconfigure(0, weight=1)
        self.cards_container.columnconfigure(1, weight=1)

        self._cargar_pacientes()

    def _abrir_formulario_creacion(self):
        def on_form_close(data):
            if data:
                try:
                    controlador.crear_paciente(data["nombre"], data["telefono"], data["dni"], data["direccion"], data["correo"], data["genero"])
                    self._cargar_pacientes()
                except Exception as e: messagebox.showerror("Error al guardar", str(e), parent=self)
        VentanaFormularioPaciente(self, on_form_close)

    def _abrir_formulario_edicion(self, paciente_a_editar):
        def on_form_close(data):
            if data:
                try:
                    controlador.actualizar_paciente(data["id"], data["nombre"], data["telefono"], data["dni"], data["direccion"], data["correo"], data["genero"])
                    self._cargar_pacientes()
                except Exception as e: messagebox.showerror("Error al actualizar", str(e), parent=self)
        VentanaFormularioPaciente(self, on_form_close, paciente_existente=paciente_a_editar)

    def _cargar_pacientes(self):
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        lista_pacientes = controlador.obtener_lista_pacientes()
        if not lista_pacientes:
            ttk.Label(self.cards_container, text="No hay pacientes registrados.", font=("Segoe UI", 12), bootstyle="light").pack(pady=50, padx=50) # Etiqueta más visible
        else:
            COLS = 2
            for i, p in enumerate(lista_pacientes):
                fila = i // COLS
                col = i % COLS
                card = PacienteCard(self.cards_container, p, edit_callback=self._abrir_formulario_edicion)
                card.grid(row=fila, column=col, padx=15, pady=15, sticky="nsew") # sticky="nsew" para que la tarjeta se estire
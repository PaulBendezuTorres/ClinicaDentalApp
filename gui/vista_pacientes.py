import ttkbootstrap as ttk
from tkinter import messagebox
from logic import controlador
from ttkbootstrap.scrolled import ScrolledFrame
from gui.ventana_formulario_paciente import VentanaFormularioPaciente

class PacienteCard(ttk.Frame):
    def __init__(self, parent, paciente_data, edit_callback):
        super().__init__(parent, padding=15, bootstyle="light")
        self.paciente_data = paciente_data
        
        # Le decimos a la columna del medio (la que contiene el texto) que debe expandirse.
        self.columnconfigure(1, weight=1)

        # Icono (sin cambios)
        genero_iconos = {"Masculino": "👨", "Femenino": "👩", "Otro": "👤"}
        icono_char = genero_iconos.get(paciente_data.get("genero", "Otro"), "👤")
        icono = ttk.Label(self, text=icono_char, font=("Segoe UI", 24))
        icono.grid(row=0, column=0, rowspan=2, padx=(0, 15), sticky="ns")

        # Label para el Nombre (simplificado)
        nombre = ttk.Label(self, text=paciente_data["nombre"], font=("Segoe UI", 12, "bold"), anchor="w")
        # 'sticky="ew"' le dice que se estire horizontalmente para llenar la columna.
        nombre.grid(row=0, column=1, sticky="ew")
        
        # Label para el DNI (sin cambios, ya era correcto)
        dni = ttk.Label(self, text=f"DNI: {paciente_data.get('dni', 'N/A')}", bootstyle="secondary", anchor="w")
        dni.grid(row=1, column=1, sticky="ew")

        botones_frame = ttk.Frame(self, bootstyle="light")
        botones_frame.grid(row=0, column=2, rowspan=2, sticky="ns")
        ttk.Button(botones_frame, text="Editar", command=lambda: edit_callback(paciente_data), bootstyle="outline-secondary").pack(pady=2, fill="x")
        ttk.Button(botones_frame, text="Historial", command=self._ver_historial, bootstyle="outline-info").pack(pady=2, fill="x")

    def _ver_historial(self):
        messagebox.showinfo("Próximamente", f"Aquí se mostrará el historial del paciente {self.paciente_data['nombre']}.")


class PaginaPacientes(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._build()

    def _build(self):
        main_frame = ttk.Frame(self, padding=(20, 10))
        main_frame.pack(fill="both", expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        ttk.Label(header_frame, text="Gestión de Pacientes", font=("Segoe UI", 18, "bold")).pack(side="left")
        ttk.Button(header_frame, text="✚ Agregar Nuevo Paciente", command=self._abrir_formulario_creacion, bootstyle="success").pack(side="right")
        
        self.canvas_pacientes = ScrolledFrame(main_frame, autohide=True)
        self.canvas_pacientes.pack(fill="both", expand=True)
        self.cards_container = ttk.Frame(self.canvas_pacientes)
        self.cards_container.pack(fill="both", expand=True)
        self.cards_container.columnconfigure((0, 1, 2), weight=1) # Columnas para la cuadrícula

        self._cargar_pacientes()

    def _abrir_formulario_creacion(self):
        def on_form_close(data):
            if data:
                try:
                    controlador.crear_paciente(data["nombre"], data["telefono"], data["dni"], data["direccion"], data["correo"], data["genero"])
                    self._cargar_pacientes()
                except Exception as e:
                    messagebox.showerror("Error al guardar", str(e), parent=self)
        VentanaFormularioPaciente(self, on_form_close)

    def _abrir_formulario_edicion(self, paciente_a_editar):
        def on_form_close(data):
            if data:
                try:
                    controlador.actualizar_paciente(data["id"], data["nombre"], data["telefono"], data["dni"], data["direccion"], data["correo"], data["genero"])
                    self._cargar_pacientes()
                except Exception as e:
                    messagebox.showerror("Error al actualizar", str(e), parent=self)
        VentanaFormularioPaciente(self, on_form_close, paciente_existente=paciente_a_editar)

    def _cargar_pacientes(self):
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        lista_pacientes = controlador.obtener_lista_pacientes()
        if not lista_pacientes:
            ttk.Label(self.cards_container, text="No hay pacientes registrados.").pack(pady=20)
        else:
            COLS = 3 # Número de tarjetas por fila
            for i, p in enumerate(lista_pacientes):
                fila = i // COLS
                col = i % COLS
                card = PacienteCard(self.cards_container, p, edit_callback=self._abrir_formulario_edicion)
                card.grid(row=fila, column=col, padx=10, pady=10, sticky="ew")
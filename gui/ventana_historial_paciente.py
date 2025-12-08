import ttkbootstrap as ttk
from logic import controlador
from ttkbootstrap.scrolled import ScrolledFrame

class CitaHistorialCard(ttk.Frame):
    def __init__(self, parent, cita_data, dia_semana):
        super().__init__(parent, padding=15, bootstyle="light")
        self.columnconfigure(1, weight=1) # Columna de info se expande

        # --- Columna Izquierda: Fecha y Día ---
        fecha_frame = ttk.Frame(self, bootstyle="light")
        fecha_frame.grid(row=0, column=0, padx=(0, 20), sticky="n")

        fecha_str = cita_data['fecha'].strftime('%d/%m/%Y')
        ttk.Label(fecha_frame, text=fecha_str, font=("Segoe UI", 12, "bold")).pack()
        ttk.Label(fecha_frame, text=dia_semana.capitalize(), font=("Segoe UI", 10), bootstyle="secondary").pack()

        # --- Columna Derecha: Detalles de la Cita ---
        detalles_frame = ttk.Frame(self, bootstyle="light")
        detalles_frame.grid(row=0, column=1, sticky="ew")

        tratamiento_texto = f"Tratamiento: {cita_data['tratamiento_nombre']}"
        ttk.Label(detalles_frame, text=tratamiento_texto, font=("Segoe UI", 11, "bold"), anchor="w").pack(fill="x")

        dentista_texto = f"Atendido por: {cita_data['dentista_nombre']}"
        ttk.Label(detalles_frame, text=dentista_texto, bootstyle="secondary", anchor="w").pack(fill="x", pady=(2, 8))

        # Separador
        ttk.Separator(detalles_frame).pack(fill="x", pady=5)
        
        hora_texto = f"Hora: {str(cita_data['hora_inicio'])[:5]}"
        costo_texto = f"Costo: S/ {cita_data['costo']:.2f}"
        
        info_footer = ttk.Frame(detalles_frame, bootstyle="light")
        info_footer.pack(fill="x")
        ttk.Label(info_footer, text=hora_texto, bootstyle="info").pack(side="left")
        ttk.Label(info_footer, text=costo_texto, bootstyle="success").pack(side="right")


class VentanaHistorialPaciente(ttk.Toplevel):
    def __init__(self, parent, paciente_data):
        super().__init__(title=f"Historial de {paciente_data['nombre']}")
        self.transient(parent)
        self.grab_set()

        self.paciente_id = paciente_data['id']
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill="both")

        scrolled_frame = ScrolledFrame(main_frame, autohide=True)
        scrolled_frame.pack(fill="both", expand=True)
        self.cards_container = ttk.Frame(scrolled_frame)
        self.cards_container.pack(fill="x", expand=True)

        self._cargar_historial()

        ttk.Button(main_frame, text="Cerrar", command=self.destroy, bootstyle="secondary-outline").pack(side="right", pady=(15, 0))

        # --- INICIO DE LA LÓGICA DE CENTRADO EN PANTALLA ---
        self.update_idletasks() # Asegura que las dimensiones iniciales son correctas

        # Dimensiones deseadas para la ventana
        my_width = 800
        my_height = 500

        # Obtenemos las dimensiones de la pantalla del monitor
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculamos las coordenadas x, y para centrar la ventana
        x = (screen_width // 2) - (my_width // 2)
        y = (screen_height // 2) - (my_height // 2)

        self.geometry(f"{my_width}x{my_height}+{x}+{y}")
        # --- FIN DE LA LÓGICA DE CENTRADO EN PANTALLA ---

    def _cargar_historial(self):
        historial = controlador.obtener_historial_paciente(self.paciente_id)
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        if not historial:
            ttk.Label(self.cards_container, text="Este paciente no tiene citas registradas.", font=("Segoe UI", 12)).pack(pady=30)
            return

        for cita in historial:
            fecha_obj = cita['fecha']
            dia_semana_str = dias[fecha_obj.weekday()]
            
            card = CitaHistorialCard(self.cards_container, cita, dia_semana_str)
            card.pack(fill="x", padx=10, pady=5)
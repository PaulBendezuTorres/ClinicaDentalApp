import ttkbootstrap as ttk
from tkinter import messagebox
from logic.sistema import sistema  # <-- NUEVO IMPORT
from ttkbootstrap.scrolled import ScrolledFrame

# --- CONFIGURACIÓN DE COLORES POR ESTADO ---
ESTILOS_ESTADO = {
    'Pendiente': {'color': 'warning', 'icono': '🕒'},
    'Confirmada': {'color': 'info', 'icono': '👍'},
    'Realizada': {'color': 'success', 'icono': '✅'},
    'Cancelada': {'color': 'danger', 'icono': '🚫'}
}

class CitaCard(ttk.Labelframe):
    def __init__(self, parent, cita, rol_usuario, callback_estado):
        estilo = ESTILOS_ESTADO.get(cita['estado'], {'color': 'light'})
        color_boot = estilo['color']
        
        super().__init__(parent, padding=15, bootstyle=color_boot)
        
        self.cita = cita
        self.rol = rol_usuario
        self.callback = callback_estado
        self.columnconfigure(1, weight=1) 

        # COLUMNA 1
        left_frame = ttk.Frame(self)
        left_frame.grid(row=0, column=0, padx=(0, 20), sticky="n")
        hora_str = str(cita['hora_inicio'])[:5]
        ttk.Label(left_frame, text=hora_str, font=("Segoe UI", 22, "bold"), bootstyle=color_boot).pack()
        ttk.Label(left_frame, text=f"{estilo['icono']} {cita['estado']}", font=("Segoe UI", 10), bootstyle=color_boot).pack(pady=5)

        # COLUMNA 2
        center_frame = ttk.Frame(self)
        center_frame.grid(row=0, column=1, sticky="ew")
        ttk.Label(center_frame, text=cita['paciente'], font=("Segoe UI", 14, "bold"), bootstyle="light").pack(anchor="w")
        ttk.Label(center_frame, text=f"Tratamiento: {cita['tratamiento']}", font=("Segoe UI", 11), bootstyle="info").pack(anchor="w", pady=(2,5))
        info_doc = f"Dr(a): {cita['dentista']}  |  {cita['consultorio']}"
        ttk.Label(center_frame, text=info_doc, font=("Segoe UI", 10), bootstyle="light").pack(anchor="w")
        if cita['fecha']: 
             ttk.Label(center_frame, text=f"Fecha: {cita['fecha']}", font=("Segoe UI", 10), bootstyle="warning").pack(anchor="w")

        # COLUMNA 3
        right_frame = ttk.Frame(self)
        right_frame.grid(row=0, column=2, padx=(10, 0), sticky="e")

        if cita['estado'] == 'Pendiente':
            ttk.Button(right_frame, text="Confirmar", bootstyle="info-outline", command=lambda: self.accion("Confirmada")).pack(fill="x", pady=2)
            if self.rol == 'admin':
                ttk.Button(right_frame, text="Cancelar", bootstyle="danger-outline", command=lambda: self.accion("Cancelada")).pack(fill="x", pady=2)
        elif cita['estado'] == 'Confirmada':
            ttk.Button(right_frame, text="Finalizar", bootstyle="success", command=lambda: self.accion("Realizada")).pack(fill="x", pady=2)
            if self.rol == 'admin':
                ttk.Button(right_frame, text="Cancelar", bootstyle="danger-outline", command=lambda: self.accion("Cancelada")).pack(fill="x", pady=2)
        elif cita['estado'] == 'Cancelada':
             ttk.Label(right_frame, text="Cancelada", bootstyle="danger").pack()
        elif cita['estado'] == 'Realizada':
             ttk.Label(right_frame, text="Completada", bootstyle="success").pack()

    def accion(self, nuevo_estado):
        if nuevo_estado == "Cancelada":
            if not messagebox.askyesno("Confirmar", "¿Seguro que desea cancelar esta cita?"): return
        self.callback(self.cita['id'], nuevo_estado)


class PaginaDashboard(ttk.Frame):
    def __init__(self, parent, usuario_data=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self._build()

    def _build(self):
        header_frame = ttk.Frame(self, padding=20)
        header_frame.pack(fill="x")
        saludo = f"Hola, {self.usuario_data['nombre_usuario']}" if self.usuario_data else "Agenda"
        ttk.Label(header_frame, text=f"{saludo}", font=("Segoe UI", 22, "bold"), bootstyle="light").pack(side="left")

        tool_frame = ttk.Frame(self, padding=(20, 0, 20, 10))
        tool_frame.pack(fill="x")
        
        ttk.Label(tool_frame, text="Mostrar:", bootstyle="light").pack(side="left", padx=(0,5))
        self.cmb_filtro = ttk.Combobox(tool_frame, values=["Hoy", "Futuras", "Todas"], state="readonly", width=10)
        self.cmb_filtro.set("Hoy")
        self.cmb_filtro.pack(side="left")
        self.cmb_filtro.bind("<<ComboboxSelected>>", lambda e: self._cargar_citas())

        ttk.Label(tool_frame, text="Buscar Paciente:", bootstyle="light").pack(side="left", padx=(20, 5))
        self.ent_buscar = ttk.Entry(tool_frame, width=30)
        self.ent_buscar.pack(side="left")
        self.ent_buscar.bind("<Return>", lambda e: self._cargar_citas())
        self.ent_buscar.bind("<KeyRelease>", lambda e: self._cargar_citas())

        ttk.Button(tool_frame, text="🔄", command=self._cargar_citas, bootstyle="secondary-outline").pack(side="right")

        self.canvas_scroll = ScrolledFrame(self, autohide=True, bootstyle="dark")
        self.canvas_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.cards_container = ttk.Frame(self.canvas_scroll, bootstyle="dark")
        self.cards_container.pack(fill="x", expand=True)
        self.cards_container.columnconfigure(0, weight=1)
        self.cards_container.columnconfigure(1, weight=1)

        self._cargar_citas()

    def _cargar_citas(self):
        for widget in self.cards_container.winfo_children(): widget.destroy()
        
        filtro_tiempo = self.cmb_filtro.get().lower()
        texto_buscar = self.ent_buscar.get().strip()
        
        # USAMOS EL SERVICIO DE CITAS
        citas = sistema.cita.listar_dashboard(filtro_tiempo, texto_buscar)
        
        if not citas:
            msg = "No se encontraron citas."
            if texto_buscar: msg = f"No hay citas para '{texto_buscar}'."
            ttk.Label(self.cards_container, text=msg, font=("Segoe UI", 14), bootstyle="inverse-dark").pack(pady=50)
            return

        resumen = f"Mostrando {len(citas)} citas"
        ttk.Label(self.cards_container, text=resumen, bootstyle="light").grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        COLS = 2
        for i, cita in enumerate(citas):
            fila = (i // COLS) + 1
            col = i % COLS
            card = CitaCard(self.cards_container, cita, self.usuario_data['rol'], self._cambiar_estado)
            card.grid(row=fila, column=col, sticky="nsew", padx=10, pady=10)

    def _cambiar_estado(self, cita_id, nuevo_estado):
        try:
            # USAMOS EL SERVICIO DE CITAS
            sistema.cita.cambiar_estado(cita_id, nuevo_estado)
            self._cargar_citas() 
        except Exception as e:
            messagebox.showerror("Error", str(e))
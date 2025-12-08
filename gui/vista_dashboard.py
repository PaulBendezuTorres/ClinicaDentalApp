import ttkbootstrap as ttk
from tkinter import messagebox
from logic import controlador
from ttkbootstrap.scrolled import ScrolledFrame

class PaginaDashboard(ttk.Frame):
    def __init__(self, parent, usuario_data=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self._build()

    def _build(self):
        # Header
        header_frame = ttk.Frame(self, padding=20)
        header_frame.pack(fill="x")
        
        saludo = f"Hola, {self.usuario_data['nombre_usuario']}" if self.usuario_data else "Bienvenido"
        ttk.Label(header_frame, text=f"{saludo} | Gestión de Citas", font=("Segoe UI", 20, "bold")).pack(side="left")

        # Filtros
        filter_frame = ttk.Frame(self, padding=(20, 0, 20, 10))
        filter_frame.pack(fill="x")
        
        ttk.Label(filter_frame, text="Filtrar por:").pack(side="left", padx=5)
        self.cmb_filtro = ttk.Combobox(filter_frame, values=["Hoy", "Futuras", "Todas"], state="readonly", width=15)
        self.cmb_filtro.set("Hoy")
        self.cmb_filtro.pack(side="left")
        self.cmb_filtro.bind("<<ComboboxSelected>>", lambda e: self._cargar_citas())

        ttk.Button(filter_frame, text="🔄 Refrescar", command=self._cargar_citas, bootstyle="light-outline").pack(side="left", padx=10)

        # Tabla de Citas
        table_frame = ttk.Frame(self, padding=20)
        table_frame.pack(fill="both", expand=True)

        cols = ("ID", "Fecha", "Hora", "Paciente", "Dentista", "Tratamiento", "Estado")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Hora", text="Hora")
        self.tree.heading("Paciente", text="Paciente")
        self.tree.heading("Dentista", text="Dentista")
        self.tree.heading("Tratamiento", text="Tratamiento")
        self.tree.heading("Estado", text="Estado")

        self.tree.column("ID", width=40, anchor="center")
        self.tree.column("Fecha", width=80, anchor="center")
        self.tree.column("Hora", width=60, anchor="center")
        self.tree.column("Paciente", width=150)
        self.tree.column("Dentista", width=150)
        self.tree.column("Tratamiento", width=150)
        self.tree.column("Estado", width=100, anchor="center")

        # Scrollbar
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # Botones de Acción (Pie de página)
        action_frame = ttk.Frame(self, padding=20)
        action_frame.pack(fill="x")

        ttk.Button(action_frame, text="✅ Marcar como Realizada", bootstyle="success", command=lambda: self._cambiar_estado("Realizada")).pack(side="left", padx=5)
        ttk.Button(action_frame, text="👍 Confirmar Asistencia", bootstyle="info", command=lambda: self._cambiar_estado("Confirmada")).pack(side="left", padx=5)
        
        # Lógica de Permisos: Botón Cancelar
        # Solo ADMIN puede cancelar
        if self.usuario_data and self.usuario_data.get('rol') == 'admin':
            ttk.Button(action_frame, text="🚫 Cancelar Cita", bootstyle="danger", command=lambda: self._cambiar_estado("Cancelada")).pack(side="right", padx=5)
        else:
            # Opción visual para recepcionistas (deshabilitado o mensaje)
            btn_cancel = ttk.Button(action_frame, text="🚫 Cancelar Cita", state="disabled")
            btn_cancel.pack(side="right", padx=5)
            # Tooltip o ayuda visual podría ir aquí

        self._cargar_citas()

    def _cargar_citas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filtro_txt = self.cmb_filtro.get().lower()
        citas = controlador.listar_citas(filtro_txt)
        
        for c in citas:
            # Formateo visual
            hora = str(c['hora_inicio'])[:5]
            fecha = str(c['fecha'])
            
            # Estilo de fila según estado (opcional, requiere configurar tags)
            self.tree.insert("", "end", values=(
                c['id'], fecha, hora, c['paciente'], c['dentista'], c['tratamiento'], c['estado']
            ))

    def _cambiar_estado(self, nuevo_estado):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione una cita de la tabla.")
            return
        
        cita_id = self.tree.item(sel[0])['values'][0]
        paciente = self.tree.item(sel[0])['values'][3]
        
        if messagebox.askyesno("Confirmar", f"¿Cambiar estado de la cita de {paciente} a '{nuevo_estado}'?"):
            controlador.cambiar_estado_cita(cita_id, nuevo_estado)
            self._cargar_citas()
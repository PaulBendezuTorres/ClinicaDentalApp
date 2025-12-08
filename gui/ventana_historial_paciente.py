import ttkbootstrap as ttk
import tkinter as tk
from tkinter import messagebox
from logic.sistema import sistema  # <-- NUEVO IMPORT
from ttkbootstrap.scrolled import ScrolledFrame

COLORES_ESTADO = {'Pendiente': 'warning', 'Confirmada': 'info', 'Realizada': 'success', 'Cancelada': 'danger'}

class CitaHistorialCard(ttk.Frame):
    def __init__(self, parent, cita_data, dia_semana, callback_refresh):
        super().__init__(parent, padding=10, bootstyle="secondary")
        self.cita_data = cita_data
        self.callback_refresh = callback_refresh
        self.columnconfigure(1, weight=1)

        fecha_frame = ttk.Frame(self, bootstyle="secondary")
        fecha_frame.grid(row=0, column=0, padx=(0, 15), sticky="ns")
        dia_num = cita_data['fecha'].strftime('%d')
        mes_anio = cita_data['fecha'].strftime('%b %Y')
        lbl_dia = ttk.Label(fecha_frame, text=dia_num, font=("Segoe UI", 24, "bold"), bootstyle="inverse-secondary")
        lbl_dia.pack(anchor="center")
        ttk.Label(fecha_frame, text=f"{dia_semana[:3].upper()} - {mes_anio}", font=("Segoe UI", 9), bootstyle="inverse-secondary").pack(anchor="center")

        detalles_frame = ttk.Frame(self, bootstyle="secondary")
        detalles_frame.grid(row=0, column=1, sticky="ew", pady=5)
        ttk.Label(detalles_frame, text=cita_data['tratamiento_nombre'], font=("Segoe UI", 14, "bold"), bootstyle="inverse-secondary").pack(anchor="w")
        info_sub = f"Dr(a). {cita_data['dentista_nombre']}  •  Hora: {str(cita_data['hora_inicio'])[:5]}"
        ttk.Label(detalles_frame, text=info_sub, font=("Segoe UI", 10), bootstyle="inverse-secondary").pack(anchor="w", pady=(2, 0))

        info_right_frame = ttk.Frame(self, bootstyle="secondary")
        info_right_frame.grid(row=0, column=2, padx=(10, 0), sticky="e")
        estado = cita_data.get('estado', 'Pendiente')
        color_estado = COLORES_ESTADO.get(estado, 'light')
        ttk.Label(info_right_frame, text=f" {estado.upper()} ", font=("Segoe UI", 9, "bold"), bootstyle=f"{color_estado}-inverse").pack(anchor="e", pady=(0, 5))
        ttk.Label(info_right_frame, text=f"S/ {cita_data['costo']:.2f}", font=("Segoe UI", 12, "bold"), bootstyle="success").pack(anchor="e")

        self.mb = ttk.Menubutton(info_right_frame, text="Opciones", bootstyle="secondary-outline")
        self.mb.pack(anchor="e", pady=(5, 0))
        self.menu = tk.Menu(self.mb, tearoff=0)
        self.mb['menu'] = self.menu
        for est in ['Pendiente', 'Confirmada', 'Realizada', 'Cancelada']:
            if est != estado: self.menu.add_command(label=f"Marcar {est}", command=lambda e=est: self._cambiar_estado(e))

    def _cambiar_estado(self, nuevo_estado):
        if nuevo_estado == "Cancelada" and not messagebox.askyesno("Confirmar", "¿Cancelar cita histórica?"): return
        try:
            # SERVICIO CITAS
            sistema.cita.cambiar_estado(self.cita_data['id'], nuevo_estado)
            self.callback_refresh()
        except Exception as e: messagebox.showerror("Error", str(e))

class VentanaHistorialPaciente(ttk.Toplevel):
    def __init__(self, parent, paciente_data):
        super().__init__(title=f"Historial Médico: {paciente_data['nombre']}")
        self.transient(parent)
        self.grab_set()
        self.paciente_id = paciente_data['id']
        
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill="both")
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 15))
        ttk.Label(header_frame, text="Historial de Citas", font=("Segoe UI", 18, "bold")).pack(side="left")
        ttk.Button(header_frame, text="✕ Cerrar", command=self.destroy, bootstyle="danger-outline").pack(side="right")

        scrolled_frame = ScrolledFrame(main_frame, autohide=True)
        scrolled_frame.pack(fill="both", expand=True)
        self.cards_container = ttk.Frame(scrolled_frame)
        self.cards_container.pack(fill="x", expand=True)

        self._cargar_historial()
        
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (600 // 2)
        self.geometry(f"900x600+{x}+{y}")

    def _cargar_historial(self):
        for widget in self.cards_container.winfo_children(): widget.destroy()
        # SERVICIO CITAS
        historial = sistema.cita.obtener_historial(self.paciente_id)
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        if not historial:
            ttk.Label(self.cards_container, text="No hay historial.", font=("Segoe UI", 14), bootstyle="secondary").pack(pady=50)
            return

        for cita in historial:
            dia_sem = dias[cita['fecha'].weekday()]
            card = CitaHistorialCard(self.cards_container, cita, dia_sem, self._cargar_historial)
            card.pack(fill="x", pady=5, padx=5)
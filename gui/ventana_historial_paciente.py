import ttkbootstrap as ttk
import tkinter as tk
from tkinter import messagebox
from logic import controlador
from ttkbootstrap.scrolled import ScrolledFrame

# Mapa de colores para los estados
COLORES_ESTADO = {
    'Pendiente': 'warning',
    'Confirmada': 'info',
    'Realizada': 'success',
    'Cancelada': 'danger'
}

class CitaHistorialCard(ttk.Frame):
    def __init__(self, parent, cita_data, dia_semana, callback_refresh):
        # Usamos un estilo 'secondary' para un fondo gris oscuro sutil, o 'default' para transparente
        super().__init__(parent, padding=10, bootstyle="secondary")
        self.cita_data = cita_data
        self.callback_refresh = callback_refresh
        
        # Configuración de Grid: 3 columnas principales
        self.columnconfigure(1, weight=1) # El centro se expande

        # --- COLUMNA 1: FECHA (Estilo Calendario) ---
        # Un cuadro visual para la fecha
        fecha_frame = ttk.Frame(self, bootstyle="secondary")
        fecha_frame.grid(row=0, column=0, padx=(0, 15), sticky="ns")
        
        dia_num = cita_data['fecha'].strftime('%d')
        mes_anio = cita_data['fecha'].strftime('%b %Y') # Ej: Nov 2025
        
        # Día numérico grande
        lbl_dia = ttk.Label(fecha_frame, text=dia_num, font=("Segoe UI", 24, "bold"), bootstyle="inverse-secondary")
        lbl_dia.pack(anchor="center")
        
        # Mes y día semana
        texto_fecha_baja = f"{dia_semana[:3].upper()} - {mes_anio}"
        ttk.Label(fecha_frame, text=texto_fecha_baja, font=("Segoe UI", 9), bootstyle="inverse-secondary").pack(anchor="center")

        # --- COLUMNA 2: DETALLES PRINCIPALES ---
        detalles_frame = ttk.Frame(self, bootstyle="secondary")
        detalles_frame.grid(row=0, column=1, sticky="ew", pady=5)

        # Título: Tratamiento
        tratamiento = cita_data['tratamiento_nombre']
        ttk.Label(detalles_frame, text=tratamiento, font=("Segoe UI", 14, "bold"), bootstyle="inverse-secondary").pack(anchor="w")

        # Subtítulo: Dentista y Hora
        hora_str = str(cita_data['hora_inicio'])[:5]
        info_sub = f"Dr(a). {cita_data['dentista_nombre']}  •  Hora: {hora_str}"
        ttk.Label(detalles_frame, text=info_sub, font=("Segoe UI", 10), bootstyle="inverse-secondary").pack(anchor="w", pady=(2, 0))

        # --- COLUMNA 3: ESTADO, COSTO Y ACCIÓN ---
        info_right_frame = ttk.Frame(self, bootstyle="secondary")
        info_right_frame.grid(row=0, column=2, padx=(10, 0), sticky="e")

        # Estado (Badge de color)
        estado = cita_data.get('estado', 'Pendiente')
        color_estado = COLORES_ESTADO.get(estado, 'light')
        
        # Usamos un Label con estilo inverso para que parezca una etiqueta rellena
        lbl_estado = ttk.Label(
            info_right_frame, 
            text=f" {estado.upper()} ", 
            font=("Segoe UI", 9, "bold"), 
            bootstyle=f"{color_estado}-inverse"
        )
        lbl_estado.pack(anchor="e", pady=(0, 5))

        # Costo
        costo = f"S/ {cita_data['costo']:.2f}"
        ttk.Label(info_right_frame, text=costo, font=("Segoe UI", 12, "bold"), bootstyle="success").pack(anchor="e")

        # Botón Menú (Más discreto)
        self.mb = ttk.Menubutton(info_right_frame, text="Opciones", bootstyle="secondary-outline")
        self.mb.pack(anchor="e", pady=(5, 0))
        
        # Menú
        self.menu = tk.Menu(self.mb, tearoff=0)
        self.mb['menu'] = self.menu
        
        estados = ['Pendiente', 'Confirmada', 'Realizada', 'Cancelada']
        for est in estados:
            if est != estado:
                self.menu.add_command(label=f"Marcar como {est}", command=lambda e=est: self._cambiar_estado(e))

    def _cambiar_estado(self, nuevo_estado):
        if nuevo_estado == "Cancelada":
            if not messagebox.askyesno("Confirmar", "¿Seguro que desea marcar esta cita histórica como Cancelada?"):
                return
        try:
            controlador.cambiar_estado_cita(self.cita_data['id'], nuevo_estado)
            self.callback_refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))


class VentanaHistorialPaciente(ttk.Toplevel):
    def __init__(self, parent, paciente_data):
        super().__init__(title=f"Historial Médico: {paciente_data['nombre']}")
        self.transient(parent)
        self.grab_set()

        self.paciente_id = paciente_data['id']
        
        # Fondo principal oscuro
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill="both")

        # Título
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 15))
        ttk.Label(header_frame, text="Historial de Citas", font=("Segoe UI", 18, "bold")).pack(side="left")
        ttk.Button(header_frame, text="✕ Cerrar", command=self.destroy, bootstyle="danger-outline").pack(side="right")

        # --- Contenedor con Scroll ---
        # Usamos bootstyle='round' o similar si queremos bordes, o default
        scrolled_frame = ScrolledFrame(main_frame, autohide=True) 
        scrolled_frame.pack(fill="both", expand=True)
        
        self.cards_container = ttk.Frame(scrolled_frame)
        self.cards_container.pack(fill="x", expand=True)

        self._cargar_historial()

        # Centrado
        self.update_idletasks()
        my_width = 900
        my_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (my_width // 2)
        y = (screen_height // 2) - (my_height // 2)
        self.geometry(f"{my_width}x{my_height}+{x}+{y}")

    def _cargar_historial(self):
        for widget in self.cards_container.winfo_children(): widget.destroy()

        historial = controlador.obtener_historial_paciente(self.paciente_id)
        dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        
        if not historial:
            ttk.Label(self.cards_container, text="No hay historial registrado.", font=("Segoe UI", 14), bootstyle="secondary").pack(pady=50)
            return

        for cita in historial:
            fecha_obj = cita['fecha']
            dia_semana_str = dias[fecha_obj.weekday()]
            
            # Añadimos un separador visual entre tarjetas (padding externo)
            card = CitaHistorialCard(self.cards_container, cita, dia_semana_str, self._cargar_historial)
            card.pack(fill="x", pady=5, padx=5) # Espacio entre tarjetas
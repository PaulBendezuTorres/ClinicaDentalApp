# gui/ventana_historial_paciente.py

import ttkbootstrap as ttk
from logic import controlador

class VentanaHistorialPaciente(ttk.Toplevel):
    def __init__(self, parent, paciente_data):
        super().__init__(title=f"Historial de {paciente_data['nombre']}")
        self.transient(parent)
        self.grab_set()

        self.paciente_id = paciente_data['id']
        
        self.geometry("900x500")

        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True, fill="both")
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        ttk.Label(
            main_frame, 
            text=f"Historial de Citas: {paciente_data['nombre']}",
            font=("Segoe UI", 16, "bold"),
            bootstyle="light"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        self.tree = ttk.Treeview(
            main_frame,
            columns=("fecha", "hora", "dentista", "tratamiento", "costo"),
            show="headings",
            bootstyle="info" 
        )
        self.tree.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("hora", text="Hora")
        self.tree.heading("dentista", text="Dentista")
        self.tree.heading("tratamiento", text="Tratamiento")
        self.tree.heading("costo", text="Costo")

        self.tree.column("fecha", width=100, anchor="center")
        self.tree.column("hora", width=80, anchor="center")
        self.tree.column("dentista", width=220)
        self.tree.column("tratamiento", width=220)
        self.tree.column("costo", width=100, anchor="e")

        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(15, 0))
        footer_frame.columnconfigure(0, weight=1)

        ttk.Separator(footer_frame, bootstyle="secondary").grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        self.total_label = ttk.Label(footer_frame, font=("Segoe UI", 12, "bold"), bootstyle="success")
        self.total_label.grid(row=1, column=0, sticky="e", padx=10)
        
        ttk.Button(footer_frame, text="Cerrar", command=self.destroy, bootstyle="light-outline").grid(row=1, column=1, sticky="e")

        self._cargar_historial()
        self._centrar_ventana() # Ya no necesita 'parent' como argumento

    def _cargar_historial(self):
        historial = controlador.obtener_historial_paciente(self.paciente_id)
        total_costo = 0.0
        
        for cita in historial:
            fecha_cita = cita.get('fecha')
            hora_cita = cita.get('hora_inicio')
            costo_cita = cita.get('costo', 0.0)
            
            fecha_str = fecha_cita.strftime('%Y-%m-%d') if fecha_cita else 'N/A'
            hora_str = str(hora_cita)[:5] if hora_cita else 'N/A'
            
            costo_float = float(costo_cita)
            costo_str = f"S/ {costo_float:.2f}"
            total_costo += costo_float
            
            self.tree.insert("", "end", values=(
                fecha_str, hora_str, cita.get('dentista_nombre', 'N/A'),
                cita.get('tratamiento_nombre', 'N/A'), costo_str
            ))
        
        self.total_label.config(text=f"Costo Total Histórico: S/ {total_costo:.2f}")

    # --- INICIO DE LA CORRECCIÓN ---
    def _centrar_ventana(self):
        self.update_idletasks() # Asegura que winfo_width/height tengan el valor correcto
        
        # Obtenemos el tamaño de la ventana (el Toplevel)
        my_width = self.winfo_width()
        my_height = self.winfo_height()
        
        # Obtenemos el tamaño de la pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Calculamos la posición x, y para centrarla
        x = (screen_width // 2) - (my_width // 2)
        y = (screen_height // 2) - (my_height // 2)
        
        self.geometry(f"+{x}+{y}")
    # --- FIN DE LA CORRECCIÓN ---
import ttkbootstrap as ttk
from tkinter import messagebox
from logic import controlador

class VentanaGestionHorario(ttk.Toplevel):
    def __init__(self, parent, dentista_data):
        super().__init__(title=f"Gestionar Horario - {dentista_data['nombre']}")
        self.transient(parent)
        self.grab_set()
        
        self.dentista_id = dentista_data['id']
        self.dentista_nombre = dentista_data['nombre']
        
        self._build()
        self._centrar(parent)
        self._cargar_horarios()

    def _build(self):
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # --- Título ---
        ttk.Label(main_frame, text=f"Horarios de {self.dentista_nombre}", font=("Segoe UI", 14, "bold")).pack(pady=(0, 15))

        # --- Tabla de Horarios Actuales ---
        self.tree = ttk.Treeview(main_frame, columns=("id", "dia", "inicio", "fin"), show="headings", height=8)
        self.tree.heading("id", text="ID")
        self.tree.heading("dia", text="Día")
        self.tree.heading("inicio", text="Inicio")
        self.tree.heading("fin", text="Fin")
        
        self.tree.column("id", width=0, stretch=False) # Oculto
        self.tree.column("dia", width=100)
        self.tree.column("inicio", width=80, anchor="center")
        self.tree.column("fin", width=80, anchor="center")
        
        self.tree.pack(fill="both", expand=True)

        # Botón para borrar seleccionado
        ttk.Button(main_frame, text="Eliminar Horario Seleccionado", bootstyle="danger-outline", command=self._eliminar_horario).pack(pady=5, anchor="e")

        ttk.Separator(main_frame).pack(fill="x", pady=15)

        # --- Formulario para Agregar Nuevo Horario ---
        ttk.Label(main_frame, text="Agregar Nuevo Turno:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0,5))
        
        form_frame = ttk.Frame(main_frame)
        form_frame.pack(fill="x")

        # Combobox Día
        self.dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
        self.cmb_dia = ttk.Combobox(form_frame, values=[d.capitalize() for d in self.dias], state="readonly", width=12)
        self.cmb_dia.pack(side="left", padx=5)
        self.cmb_dia.set("Lunes")

        # Generador de horas (de 07:00 a 22:00 cada 30 min)
        horas = []
        for h in range(7, 23):
            horas.append(f"{h:02d}:00")
            horas.append(f"{h:02d}:30")
        
        # Combobox Inicio
        ttk.Label(form_frame, text="De:").pack(side="left")
        self.cmb_inicio = ttk.Combobox(form_frame, values=horas, state="readonly", width=8)
        self.cmb_inicio.pack(side="left", padx=5)
        self.cmb_inicio.set("09:00")

        # Combobox Fin
        ttk.Label(form_frame, text="A:").pack(side="left")
        self.cmb_fin = ttk.Combobox(form_frame, values=horas, state="readonly", width=8)
        self.cmb_fin.pack(side="left", padx=5)
        self.cmb_fin.set("17:00")

        ttk.Button(form_frame, text="Agregar", bootstyle="success", command=self._agregar_horario).pack(side="left", padx=15)

    def _cargar_horarios(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        
        horarios = controlador.obtener_horarios_dentista(self.dentista_id)
        for h in horarios:
            # Formateamos las horas para quitar los segundos si vienen de BD
            inicio = str(h['hora_inicio'])[:5]
            fin = str(h['hora_fin'])[:5]
            dia = h['dia_semana'].capitalize()
            self.tree.insert("", "end", values=(h['id'], dia, inicio, fin))

    def _agregar_horario(self):
        dia = self.cmb_dia.get().lower() # Guardamos en minúsculas para la BD
        inicio = self.cmb_inicio.get()
        fin = self.cmb_fin.get()

        if inicio >= fin:
            messagebox.showwarning("Error", "La hora de inicio debe ser menor a la hora de fin.", parent=self)
            return

        try:
            controlador.crear_horario_dentista(self.dentista_id, dia, inicio, fin)
            self._cargar_horarios()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar: {e}", parent=self)

    def _eliminar_horario(self):
        sel = self.tree.selection()
        if not sel: return
        
        horario_id = self.tree.item(sel[0])['values'][0]
        dia = self.tree.item(sel[0])['values'][1]
        
        if messagebox.askyesno("Confirmar", f"¿Eliminar el turno del {dia}?", parent=self):
            controlador.borrar_horario_dentista(horario_id)
            self._cargar_horarios()

    def _centrar(self, parent):
        self.update_idletasks()
        w, h = 550, 450
        x = parent.winfo_rootx() + (parent.winfo_width()//2) - (w//2)
        y = parent.winfo_rooty() + (parent.winfo_height()//2) - (h//2)
        self.geometry(f"{w}x{h}+{x}+{y}")
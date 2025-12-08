import ttkbootstrap as ttk
from tkinter import messagebox
from logic.sistema import sistema  # <-- NUEVO IMPORT

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
        ttk.Label(main_frame, text=f"Horarios de {self.dentista_nombre}", font=("Segoe UI", 14, "bold")).pack(pady=(0, 15))

        self.tree = ttk.Treeview(main_frame, columns=("id", "dia", "inicio", "fin"), show="headings", height=8)
        self.tree.heading("id", text="ID"); self.tree.column("id", width=0, stretch=False)
        self.tree.heading("dia", text="Día"); self.tree.column("dia", width=100)
        self.tree.heading("inicio", text="Inicio"); self.tree.column("inicio", width=80)
        self.tree.heading("fin", text="Fin"); self.tree.column("fin", width=80)
        self.tree.pack(fill="both", expand=True)

        ttk.Button(main_frame, text="Eliminar Seleccionado", bootstyle="danger-outline", command=self._eliminar_horario).pack(pady=5, anchor="e")
        ttk.Separator(main_frame).pack(fill="x", pady=15)

        ttk.Label(main_frame, text="Agregar Nuevo Turno:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0,5))
        form_frame = ttk.Frame(main_frame); form_frame.pack(fill="x")

        self.cmb_dia = ttk.Combobox(form_frame, values=["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"], state="readonly", width=12)
        self.cmb_dia.pack(side="left", padx=5); self.cmb_dia.set("Lunes")

        horas = [f"{h:02d}:{m:02d}" for h in range(7, 23) for m in (0, 30)]
        ttk.Label(form_frame, text="De:").pack(side="left")
        self.cmb_inicio = ttk.Combobox(form_frame, values=horas, state="readonly", width=8); self.cmb_inicio.pack(side="left", padx=5); self.cmb_inicio.set("09:00")
        ttk.Label(form_frame, text="A:").pack(side="left")
        self.cmb_fin = ttk.Combobox(form_frame, values=horas, state="readonly", width=8); self.cmb_fin.pack(side="left", padx=5); self.cmb_fin.set("17:00")

        ttk.Button(form_frame, text="Agregar", bootstyle="success", command=self._agregar_horario).pack(side="left", padx=15)

    def _cargar_horarios(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        # SERVICIO HORARIO
        horarios = sistema.horario.obtener_por_dentista(self.dentista_id)
        for h in horarios:
            self.tree.insert("", "end", values=(h['id'], h['dia_semana'].capitalize(), str(h['hora_inicio'])[:5], str(h['hora_fin'])[:5]))

    def _agregar_horario(self):
        dia = self.cmb_dia.get().lower()
        inicio = self.cmb_inicio.get()
        fin = self.cmb_fin.get()
        if inicio >= fin:
            messagebox.showwarning("Error", "Inicio debe ser menor a Fin", parent=self)
            return
        try:
            sistema.horario.crear(self.dentista_id, dia, inicio, fin)
            self._cargar_horarios()
        except Exception as e: messagebox.showerror("Error", str(e), parent=self)

    def _eliminar_horario(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Confirmar", "¿Eliminar turno?"):
            sistema.horario.eliminar(self.tree.item(sel[0])['values'][0])
            self._cargar_horarios()

    def _centrar(self, parent):
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width()//2) - (550//2)
        y = parent.winfo_rooty() + (parent.winfo_height()//2) - (450//2)
        self.geometry(f"550x450+{x}+{y}")
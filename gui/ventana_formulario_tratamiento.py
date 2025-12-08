import ttkbootstrap as ttk
from tkinter import messagebox

class VentanaFormularioTratamiento(ttk.Toplevel):
    def __init__(self, parent, callback, existente=None):
        super().__init__(title="Gestión de Tratamiento")
        self.transient(parent)
        self.grab_set()
        
        self.callback = callback
        self.existente = existente
        
        self._build()
        self._centrar_ventana(parent)

    def _build(self):
        # Frame principal
        frm = ttk.Frame(self, padding=20)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Nombre Tratamiento:").pack(anchor="w")
        self.ent_nombre = ttk.Entry(frm)
        self.ent_nombre.pack(fill="x", pady=5)

        ttk.Label(frm, text="Duración (minutos):").pack(anchor="w")
        self.ent_duracion = ttk.Entry(frm)
        self.ent_duracion.pack(fill="x", pady=5)

        ttk.Label(frm, text="Costo (S/.):").pack(anchor="w")
        self.ent_costo = ttk.Entry(frm)
        self.ent_costo.pack(fill="x", pady=5)

        self.var_equipo = ttk.BooleanVar()
        ttk.Checkbutton(frm, text="Requiere Equipo Especial (Rayos X, etc.)", variable=self.var_equipo, bootstyle="round-toggle").pack(anchor="w", pady=15)

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill="x", pady=20, side="bottom") 

        ttk.Button(btn_frame, text="Guardar", bootstyle="success", command=self._guardar).pack(side="right")
        ttk.Button(btn_frame, text="Cancelar", bootstyle="secondary", command=self.destroy).pack(side="right", padx=5)

        if self.existente:
            self.ent_nombre.insert(0, self.existente['nombre'])
            self.ent_duracion.insert(0, self.existente['duracion_minutos'])
            self.ent_costo.insert(0, self.existente['costo'])
            self.var_equipo.set(bool(self.existente['requiere_equipo_especial']))

    def _guardar(self):
        try:
            nombre = self.ent_nombre.get().strip()
            duracion = int(self.ent_duracion.get())
            costo = float(self.ent_costo.get())
            equipo = 1 if self.var_equipo.get() else 0
            
            if not nombre: raise ValueError("Nombre vacío")

            data = {"nombre": nombre, "duracion": duracion, "costo": costo, "equipo": equipo}
            if self.existente: data["id"] = self.existente["id"]
            
            self.destroy()
            self.callback(data)
        except ValueError:
            messagebox.showwarning("Error", "Revise los campos numéricos (Duración y Costo).", parent=self)

    def _centrar_ventana(self, parent):
        self.update_idletasks()
        w, h = 400, 400 
        
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        
        self.geometry(f"{w}x{h}+{x}+{y}")
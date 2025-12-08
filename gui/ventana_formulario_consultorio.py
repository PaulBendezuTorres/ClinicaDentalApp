import ttkbootstrap as ttk
from tkinter import messagebox

class VentanaFormularioConsultorio(ttk.Toplevel):
    def __init__(self, parent, callback, existente=None):
        super().__init__(title="Gestión de Consultorio")
        self.transient(parent)
        self.grab_set()
        
        self.callback = callback
        self.existente = existente
        
        self._build()
        self._centrar_ventana(parent)

    def _build(self):
        frm = ttk.Frame(self, padding=20)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Nombre/Número de Sala:").pack(anchor="w")
        self.ent_nombre = ttk.Entry(frm)
        self.ent_nombre.pack(fill="x", pady=5)

        self.var_equipo = ttk.BooleanVar()
        ttk.Checkbutton(frm, text="Tiene Equipo Especial", variable=self.var_equipo, bootstyle="round-toggle").pack(anchor="w", pady=10)

        # Frame para los botones para asegurar que se queden abajo
        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill="x", pady=20)

        ttk.Button(btn_frame, text="Guardar", bootstyle="success", command=self._guardar).pack(side="right")
        ttk.Button(btn_frame, text="Cancelar", bootstyle="secondary", command=self.destroy).pack(side="right", padx=5)

        if self.existente:
            self.ent_nombre.insert(0, self.existente['nombre_sala'])
            self.var_equipo.set(bool(self.existente['equipo_especial']))

    def _guardar(self):
        nombre = self.ent_nombre.get().strip()
        if not nombre: 
            messagebox.showwarning("Error", "El nombre es obligatorio", parent=self)
            return
            
        data = {"nombre": nombre, "equipo": 1 if self.var_equipo.get() else 0}
        if self.existente: data["id"] = self.existente["id"]
        self.destroy()
        self.callback(data)

    def _centrar_ventana(self, parent):
        self.update_idletasks()
        w, h = 400 , 220 
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (w // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (h // 2)
        
        self.geometry(f"{w}x{h}+{x}+{y}")
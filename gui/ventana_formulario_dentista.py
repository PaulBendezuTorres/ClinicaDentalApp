import ttkbootstrap as ttk
from tkinter import messagebox

class VentanaFormularioDentista(ttk.Toplevel):
    def __init__(self, parent, callback, dentista_existente=None):
        title = "Editar Dentista" if dentista_existente else "Nuevo Dentista"
        super().__init__(title=title)
        self.transient(parent)
        self.grab_set()
        
        self.callback = callback
        self.dentista_existente = dentista_existente
        
        self._build()
        self._centrar(parent)

    def _build(self):
        frm = ttk.Frame(self, padding=20)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Nombre Completo:").pack(anchor="w")
        self.ent_nombre = ttk.Entry(frm, width=40)
        self.ent_nombre.pack(fill="x", pady=5)

        ttk.Label(frm, text="Especialidad:").pack(anchor="w", pady=(10,0))
        self.ent_esp = ttk.Entry(frm, width=40)
        self.ent_esp.pack(fill="x", pady=5)

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill="x", pady=20)
        ttk.Button(btn_frame, text="Guardar", bootstyle="success", command=self._guardar).pack(side="right")
        ttk.Button(btn_frame, text="Cancelar", bootstyle="secondary", command=self.destroy).pack(side="right", padx=5)

        if self.dentista_existente:
            self.ent_nombre.insert(0, self.dentista_existente['nombre'])
            self.ent_esp.insert(0, self.dentista_existente['especialidad'])

    def _guardar(self):
        nombre = self.ent_nombre.get().strip()
        esp = self.ent_esp.get().strip()

        if not nombre or not esp:
            messagebox.showwarning("Error", "Todos los campos son obligatorios", parent=self)
            return
        
        data = {"nombre": nombre, "especialidad": esp}
        if self.dentista_existente:
            data["id"] = self.dentista_existente["id"]
        
        self.destroy()
        self.callback(data)

    def _centrar(self, parent):
        self.update_idletasks()
        w, h = 400, 250
        x = parent.winfo_rootx() + (parent.winfo_width()//2) - (w//2)
        y = parent.winfo_rooty() + (parent.winfo_height()//2) - (h//2)
        self.geometry(f"{w}x{h}+{x}+{y}")
        
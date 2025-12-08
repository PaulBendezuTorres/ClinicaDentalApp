import ttkbootstrap as ttk
from tkinter import messagebox

class VentanaFormularioUsuario(ttk.Toplevel):
    def __init__(self, parent, callback, usuario_existente=None):
        title = "Editar Usuario" if usuario_existente else "Nuevo Usuario"
        super().__init__(title=title)
        self.transient(parent)
        self.grab_set()
        
        self.callback = callback
        self.usuario_existente = usuario_existente
        
        self._build()
        self._centrar(parent)

    def _build(self):
        frm = ttk.Frame(self, padding=20)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Nombre de Usuario:").pack(anchor="w")
        self.ent_nombre = ttk.Entry(frm)
        self.ent_nombre.pack(fill="x", pady=5)

        ttk.Label(frm, text="Rol:").pack(anchor="w", pady=(10,0))
        self.cmb_rol = ttk.Combobox(frm, values=["recepcionista", "admin"], state="readonly")
        self.cmb_rol.pack(fill="x", pady=5)
        self.cmb_rol.set("recepcionista")

        lbl_pass = "Contraseña (dejar vacía para no cambiar):" if self.usuario_existente else "Contraseña:"
        ttk.Label(frm, text=lbl_pass).pack(anchor="w", pady=(10,0))
        self.ent_pass = ttk.Entry(frm, show="*")
        self.ent_pass.pack(fill="x", pady=5)

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill="x", pady=20)
        ttk.Button(btn_frame, text="Guardar", bootstyle="success", command=self._guardar).pack(side="right")
        ttk.Button(btn_frame, text="Cancelar", bootstyle="secondary", command=self.destroy).pack(side="right", padx=5)

        if self.usuario_existente:
            self.ent_nombre.insert(0, self.usuario_existente['nombre_usuario'])
            self.cmb_rol.set(self.usuario_existente['rol'])

    def _guardar(self):
        nombre = self.ent_nombre.get().strip()
        rol = self.cmb_rol.get()
        pw = self.ent_pass.get().strip()

        if not nombre or not rol:
            messagebox.showwarning("Error", "Nombre y Rol son obligatorios", parent=self)
            return
        
        if not self.usuario_existente and not pw:
            messagebox.showwarning("Error", "La contraseña es obligatoria para nuevos usuarios", parent=self)
            return

        data = {"nombre": nombre, "rol": rol, "password": pw if pw else None}
        if self.usuario_existente:
            data["id"] = self.usuario_existente["id"]
        
        self.destroy()
        self.callback(data)

    def _centrar(self, parent):
        self.update_idletasks()
        w, h = 350, 350
        x = parent.winfo_rootx() + (parent.winfo_width()//2) - (w//2)
        y = parent.winfo_rooty() + (parent.winfo_height()//2) - (h//2)
        self.geometry(f"{w}x{h}+{x}+{y}")
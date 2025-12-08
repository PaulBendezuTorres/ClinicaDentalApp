import ttkbootstrap as ttk
from tkinter import messagebox
from logic import controlador
from gui.ventana_formulario_usuario import VentanaFormularioUsuario

class PaginaAdministracion(ttk.Frame):
    def __init__(self, parent, usuario_data=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self._build()

    def _build(self):
        ttk.Label(self, text="Panel de Administración", font=("Segoe UI", 20, "bold")).pack(pady=20)

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Pestaña 1: Usuarios ---
        self.tab_usuarios = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_usuarios, text="Usuarios")
        self._construir_tab_usuarios()

        # --- Pestaña 2: Dentistas ---
        self.tab_dentistas = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_dentistas, text="Dentistas")
        ttk.Label(self.tab_dentistas, text="Próximamente: Gestión de Dentistas").pack()

    def _construir_tab_usuarios(self):
        # Toolbar
        tool_frame = ttk.Frame(self.tab_usuarios)
        tool_frame.pack(fill="x", pady=5)
        ttk.Button(tool_frame, text="+ Nuevo Usuario", bootstyle="success", command=self._nuevo_usuario).pack(side="left")
        ttk.Button(tool_frame, text="Refrescar", bootstyle="info-outline", command=self._cargar_usuarios).pack(side="left", padx=5)

        # Tabla
        cols = ("ID", "Usuario", "Rol")
        self.tree_users = ttk.Treeview(self.tab_usuarios, columns=cols, show="headings", height=10)
        self.tree_users.heading("ID", text="ID")
        self.tree_users.heading("Usuario", text="Usuario")
        self.tree_users.heading("Rol", text="Rol")
        
        self.tree_users.column("ID", width=50, anchor="center")
        self.tree_users.column("Usuario", width=200)
        self.tree_users.column("Rol", width=150)
        self.tree_users.pack(fill="both", expand=True, pady=5)

        # Botones de acción
        action_frame = ttk.Frame(self.tab_usuarios)
        action_frame.pack(fill="x", pady=5)
        ttk.Button(action_frame, text="Editar Seleccionado", bootstyle="warning-outline", command=self._editar_usuario).pack(side="left")
        ttk.Button(action_frame, text="Eliminar Seleccionado", bootstyle="danger-outline", command=self._eliminar_usuario).pack(side="left", padx=5)

        self._cargar_usuarios()

    def _cargar_usuarios(self):
        for item in self.tree_users.get_children():
            self.tree_users.delete(item)
        
        usuarios = controlador.obtener_lista_usuarios()
        for u in usuarios:
            self.tree_users.insert("", "end", values=(u['id'], u['nombre_usuario'], u['rol']))

    def _nuevo_usuario(self):
        def callback(data):
            try:
                controlador.registrar_usuario(data['nombre'], data['password'], data['rol'])
                messagebox.showinfo("Éxito", "Usuario creado correctamente")
                self._cargar_usuarios()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        VentanaFormularioUsuario(self, callback)

    def _editar_usuario(self):
        sel = self.tree_users.selection()
        if not sel:
            return
        
        item = self.tree_users.item(sel[0])
        # Reconstruimos el diccionario simple desde el treeview
        user_data = {
            "id": item['values'][0],
            "nombre_usuario": item['values'][1],
            "rol": item['values'][2]
        }

        def callback(data):
            try:
                controlador.modificar_usuario(data['id'], data['nombre'], data['rol'], data['password'])
                messagebox.showinfo("Éxito", "Usuario actualizado")
                self._cargar_usuarios()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        VentanaFormularioUsuario(self, callback, usuario_existente=user_data)

    def _eliminar_usuario(self):
        sel = self.tree_users.selection()
        if not sel: return
        
        user_id = self.tree_users.item(sel[0])['values'][0]
        nombre = self.tree_users.item(sel[0])['values'][1]

        # Evitar auto-eliminación
        if nombre == self.usuario_data['nombre_usuario']:
            messagebox.showwarning("Acción no permitida", "No puedes eliminar tu propio usuario.")
            return

        if messagebox.askyesno("Confirmar", f"¿Eliminar al usuario {nombre}?"):
            controlador.borrar_usuario(user_id)
            self._cargar_usuarios()
import ttkbootstrap as ttk
from tkinter import messagebox
from logic import controlador
from gui.ventana_formulario_usuario import VentanaFormularioUsuario
from gui.ventana_formulario_dentista import VentanaFormularioDentista 

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
        self._construir_tab_dentistas() # <-- AHORA CONSTRUIMOS ESTO
        
        # --- Pestaña 3: Configuración ---
        self.tab_config = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_config, text="Configuración")
        ttk.Label(self.tab_config, text="Configuraciones del sistema").pack()


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
        for item in self.tree_users.get_children(): self.tree_users.delete(item)
        usuarios = controlador.obtener_lista_usuarios()
        for u in usuarios: self.tree_users.insert("", "end", values=(u['id'], u['nombre_usuario'], u['rol']))

    def _nuevo_usuario(self):
        def callback(data):
            try:
                controlador.registrar_usuario(data['nombre'], data['password'], data['rol'])
                messagebox.showinfo("Éxito", "Usuario creado correctamente")
                self._cargar_usuarios()
            except Exception as e: messagebox.showerror("Error", str(e))
        VentanaFormularioUsuario(self, callback)

    def _editar_usuario(self):
        sel = self.tree_users.selection()
        if not sel: return
        item = self.tree_users.item(sel[0])
        user_data = {"id": item['values'][0], "nombre_usuario": item['values'][1], "rol": item['values'][2]}
        def callback(data):
            try:
                controlador.modificar_usuario(data['id'], data['nombre'], data['rol'], data['password'])
                messagebox.showinfo("Éxito", "Usuario actualizado")
                self._cargar_usuarios()
            except Exception as e: messagebox.showerror("Error", str(e))
        VentanaFormularioUsuario(self, callback, usuario_existente=user_data)

    def _eliminar_usuario(self):
        sel = self.tree_users.selection()
        if not sel: return
        user_id = self.tree_users.item(sel[0])['values'][0]
        nombre = self.tree_users.item(sel[0])['values'][1]
        if nombre == self.usuario_data['nombre_usuario']:
            messagebox.showwarning("Acción no permitida", "No puedes eliminar tu propio usuario.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar al usuario {nombre}?"):
            controlador.borrar_usuario(user_id)
            self._cargar_usuarios()

    # --- NUEVOS MÉTODOS PARA DENTISTAS ---

    def _construir_tab_dentistas(self):
        # Toolbar
        tool_frame = ttk.Frame(self.tab_dentistas)
        tool_frame.pack(fill="x", pady=5)
        ttk.Button(tool_frame, text="+ Nuevo Dentista", bootstyle="success", command=self._nuevo_dentista).pack(side="left")
        ttk.Button(tool_frame, text="Refrescar", bootstyle="info-outline", command=self._cargar_dentistas).pack(side="left", padx=5)

        # Tabla
        cols = ("ID", "Nombre", "Especialidad")
        self.tree_dentistas = ttk.Treeview(self.tab_dentistas, columns=cols, show="headings", height=10)
        self.tree_dentistas.heading("ID", text="ID")
        self.tree_dentistas.heading("Nombre", text="Nombre")
        self.tree_dentistas.heading("Especialidad", text="Especialidad")
        
        self.tree_dentistas.column("ID", width=50, anchor="center")
        self.tree_dentistas.column("Nombre", width=250)
        self.tree_dentistas.column("Especialidad", width=200)
        self.tree_dentistas.pack(fill="both", expand=True, pady=5)

        # Botones de acción
        action_frame = ttk.Frame(self.tab_dentistas)
        action_frame.pack(fill="x", pady=5)
        ttk.Button(action_frame, text="Editar Seleccionado", bootstyle="warning-outline", command=self._editar_dentista).pack(side="left")
        ttk.Button(action_frame, text="Eliminar Seleccionado", bootstyle="danger-outline", command=self._eliminar_dentista).pack(side="left", padx=5)
        
        # Botón para Gestionar Horarios (lo implementaremos después)
        ttk.Button(action_frame, text="🕒 Gestionar Horario", bootstyle="primary-outline", command=self._gestionar_horario).pack(side="right")

        self._cargar_dentistas()

    def _cargar_dentistas(self):
        for item in self.tree_dentistas.get_children():
            self.tree_dentistas.delete(item)
        
        # Usamos el controlador existente
        dentistas = controlador.obtener_lista_dentistas()
        for d in dentistas:
            self.tree_dentistas.insert("", "end", values=(d['id'], d['nombre'], d['especialidad']))

    def _nuevo_dentista(self):
        def callback(data):
            try:
                controlador.registrar_dentista(data['nombre'], data['especialidad'])
                messagebox.showinfo("Éxito", "Dentista creado correctamente")
                self._cargar_dentistas()
            except Exception as e: messagebox.showerror("Error", str(e))
        VentanaFormularioDentista(self, callback)

    def _editar_dentista(self):
        sel = self.tree_dentistas.selection()
        if not sel: return
        item = self.tree_dentistas.item(sel[0])
        dentista_data = {"id": item['values'][0], "nombre": item['values'][1], "especialidad": item['values'][2]}
        
        def callback(data):
            try:
                controlador.modificar_dentista(data['id'], data['nombre'], data['especialidad'])
                messagebox.showinfo("Éxito", "Dentista actualizado")
                self._cargar_dentistas()
            except Exception as e: messagebox.showerror("Error", str(e))
        VentanaFormularioDentista(self, callback, dentista_existente=dentista_data)

    def _eliminar_dentista(self):
        sel = self.tree_dentistas.selection()
        if not sel: return
        
        d_id = self.tree_dentistas.item(sel[0])['values'][0]
        nombre = self.tree_dentistas.item(sel[0])['values'][1]

        if messagebox.askyesno("Confirmar", f"¿Eliminar al dentista {nombre}?\n(Se mantendrá su historial de citas)"):
            controlador.borrar_dentista(d_id)
            self._cargar_dentistas()

    def _gestionar_horario(self):
        # Este método lo dejaremos listo para la próxima iteración
        sel = self.tree_dentistas.selection()
        if not sel: 
            messagebox.showwarning("Atención", "Seleccione un dentista primero.")
            return
        nombre = self.tree_dentistas.item(sel[0])['values'][1]
        messagebox.showinfo("Próximamente", f"Aquí se abrirá el gestor de horarios para {nombre}")
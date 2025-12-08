import ttkbootstrap as ttk
from tkinter import messagebox
from logic import controlador

# Importamos todas las ventanas modales
from gui.ventana_formulario_usuario import VentanaFormularioUsuario
from gui.ventana_formulario_dentista import VentanaFormularioDentista
from gui.ventana_gestion_horario import VentanaGestionHorario
from gui.ventana_formulario_tratamiento import VentanaFormularioTratamiento
from gui.ventana_formulario_consultorio import VentanaFormularioConsultorio

class PaginaAdministracion(ttk.Frame):
    def __init__(self, parent, usuario_data=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self._build()

    def _build(self):
        ttk.Label(self, text="Panel de Administración", font=("Segoe UI", 20, "bold")).pack(pady=20)

        # Contenedor de Pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Pestaña 1: Usuarios ---
        self.tab_usuarios = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_usuarios, text="Usuarios")
        self._construir_tab_usuarios()

        # --- Pestaña 2: Dentistas ---
        self.tab_dentistas = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_dentistas, text="Dentistas")
        self._construir_tab_dentistas()

        # --- Pestaña 3: Tratamientos ---
        self.tab_tratamientos = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_tratamientos, text="Tratamientos")
        self._construir_tab_tratamientos()

        # --- Pestaña 4: Consultorios ---
        self.tab_consultorios = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_consultorios, text="Consultorios")
        self._construir_tab_consultorios()
        
        # --- NUEVA PESTAÑA: PAPELERA ---
        self.tab_papelera = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_papelera, text="Papelera ♻")
        self._construir_tab_papelera()


    # GESTIÓN DE USUARIOS

    def _construir_tab_usuarios(self):
        tool_frame = ttk.Frame(self.tab_usuarios)
        tool_frame.pack(fill="x", pady=5)
        ttk.Button(tool_frame, text="+ Nuevo Usuario", bootstyle="success", command=self._nuevo_usuario).pack(side="left")
        ttk.Button(tool_frame, text="Refrescar", bootstyle="info-outline", command=self._cargar_usuarios).pack(side="left", padx=5)

        cols = ("ID", "Usuario", "Rol")
        self.tree_users = ttk.Treeview(self.tab_usuarios, columns=cols, show="headings", height=8)
        self.tree_users.heading("ID", text="ID"); self.tree_users.column("ID", width=50, anchor="center")
        self.tree_users.heading("Usuario", text="Usuario"); self.tree_users.column("Usuario", width=200)
        self.tree_users.heading("Rol", text="Rol"); self.tree_users.column("Rol", width=150)
        self.tree_users.pack(fill="both", expand=True, pady=5)

        action_frame = ttk.Frame(self.tab_usuarios)
        action_frame.pack(fill="x", pady=5)
        ttk.Button(action_frame, text="Editar Seleccionado", bootstyle="warning-outline", command=self._editar_usuario).pack(side="left")
        ttk.Button(action_frame, text="Eliminar Seleccionado", bootstyle="danger-outline", command=self._eliminar_usuario).pack(side="left", padx=5)

        self._cargar_usuarios()

    def _cargar_usuarios(self):
        for item in self.tree_users.get_children(): self.tree_users.delete(item)
        for u in controlador.obtener_lista_usuarios():
            self.tree_users.insert("", "end", values=(u['id'], u['nombre_usuario'], u['rol']))

    def _nuevo_usuario(self):
        def cb(d):
            try:
                controlador.registrar_usuario(d['nombre'], d['password'], d['rol'])
                self._cargar_usuarios()
            except Exception as e: messagebox.showerror("Error", str(e))
        VentanaFormularioUsuario(self, cb)

    def _editar_usuario(self):
        sel = self.tree_users.selection()
        if not sel: return
        item = self.tree_users.item(sel[0])
        user_data = {"id": item['values'][0], "nombre_usuario": item['values'][1], "rol": item['values'][2]}
        def cb(d):
            try:
                controlador.modificar_usuario(d['id'], d['nombre'], d['rol'], d['password'])
                self._cargar_usuarios()
            except Exception as e: messagebox.showerror("Error", str(e))
        VentanaFormularioUsuario(self, cb, usuario_existente=user_data)

    def _eliminar_usuario(self):
        sel = self.tree_users.selection()
        if not sel: return
        u_id = self.tree_users.item(sel[0])['values'][0]
        nombre = self.tree_users.item(sel[0])['values'][1]
        if nombre == self.usuario_data['nombre_usuario']:
            messagebox.showwarning("Error", "No puedes eliminar tu propio usuario.")
            return
        if messagebox.askyesno("Confirmar", f"¿Eliminar usuario {nombre}?"):
            controlador.borrar_usuario(u_id)
            self._cargar_usuarios()


    # GESTIÓN DE DENTISTAS

    def _construir_tab_dentistas(self):
        tool_frame = ttk.Frame(self.tab_dentistas)
        tool_frame.pack(fill="x", pady=5)
        ttk.Button(tool_frame, text="+ Nuevo Dentista", bootstyle="success", command=self._nuevo_dentista).pack(side="left")
        ttk.Button(tool_frame, text="Refrescar", bootstyle="info-outline", command=self._cargar_dentistas).pack(side="left", padx=5)

        cols = ("ID", "Nombre", "Especialidad")
        self.tree_dentistas = ttk.Treeview(self.tab_dentistas, columns=cols, show="headings", height=8)
        self.tree_dentistas.heading("ID", text="ID"); self.tree_dentistas.column("ID", width=50, anchor="center")
        self.tree_dentistas.heading("Nombre", text="Nombre"); self.tree_dentistas.column("Nombre", width=250)
        self.tree_dentistas.heading("Especialidad", text="Especialidad"); self.tree_dentistas.column("Especialidad", width=200)
        self.tree_dentistas.pack(fill="both", expand=True, pady=5)

        action_frame = ttk.Frame(self.tab_dentistas)
        action_frame.pack(fill="x", pady=5)
        ttk.Button(action_frame, text="Editar", bootstyle="warning-outline", command=self._editar_dentista).pack(side="left")
        ttk.Button(action_frame, text="Eliminar", bootstyle="danger-outline", command=self._eliminar_dentista).pack(side="left", padx=5)
        ttk.Button(action_frame, text="🕒 Gestionar Horario", bootstyle="primary-outline", command=self._gestionar_horario).pack(side="right")

        self._cargar_dentistas()

    def _cargar_dentistas(self):
        for item in self.tree_dentistas.get_children(): self.tree_dentistas.delete(item)
        for d in controlador.obtener_lista_dentistas():
            self.tree_dentistas.insert("", "end", values=(d['id'], d['nombre'], d['especialidad']))

    def _nuevo_dentista(self):
        def cb(d):
            try:
                controlador.registrar_dentista(d['nombre'], d['especialidad'])
                self._cargar_dentistas()
            except Exception as e: messagebox.showerror("Error", str(e))
        VentanaFormularioDentista(self, cb)

    def _editar_dentista(self):
        sel = self.tree_dentistas.selection()
        if not sel: return
        item = self.tree_dentistas.item(sel[0])
        data = {"id": item['values'][0], "nombre": item['values'][1], "especialidad": item['values'][2]}
        def cb(d):
            try:
                controlador.modificar_dentista(d['id'], d['nombre'], d['especialidad'])
                self._cargar_dentistas()
            except Exception as e: messagebox.showerror("Error", str(e))
        VentanaFormularioDentista(self, cb, dentista_existente=data)

    def _eliminar_dentista(self):
        sel = self.tree_dentistas.selection()
        if not sel: return
        d_id = self.tree_dentistas.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar dentista? (Se mantiene historial)"):
            controlador.borrar_dentista(d_id)
            self._cargar_dentistas()

    def _gestionar_horario(self):
        sel = self.tree_dentistas.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un dentista primero.")
            return
        item = self.tree_dentistas.item(sel[0])
        data = {"id": item['values'][0], "nombre": item['values'][1]}
        VentanaGestionHorario(self, data)


    # GESTIÓN DE TRATAMIENTOS

    def _construir_tab_tratamientos(self):
        tool_frame = ttk.Frame(self.tab_tratamientos); tool_frame.pack(fill="x", pady=5)
        ttk.Button(tool_frame, text="+ Nuevo Tratamiento", bootstyle="success", command=self._nuevo_tratamiento).pack(side="left")
        ttk.Button(tool_frame, text="Refrescar", bootstyle="info-outline", command=self._cargar_tratamientos).pack(side="left", padx=5)

        cols = ("ID", "Nombre", "Duración", "Costo", "Equipo Esp.")
        self.tree_trat = ttk.Treeview(self.tab_tratamientos, columns=cols, show="headings", height=8)
        self.tree_trat.heading("ID", text="ID"); self.tree_trat.column("ID", width=40)
        self.tree_trat.heading("Nombre", text="Nombre"); self.tree_trat.column("Nombre", width=200)
        self.tree_trat.heading("Duración", text="Min"); self.tree_trat.column("Duración", width=60)
        self.tree_trat.heading("Costo", text="Costo (S/.)"); self.tree_trat.column("Costo", width=80)
        self.tree_trat.heading("Equipo Esp.", text="Equipo"); self.tree_trat.column("Equipo Esp.", width=80)
        self.tree_trat.pack(fill="both", expand=True, pady=5)

        action_frame = ttk.Frame(self.tab_tratamientos); action_frame.pack(fill="x", pady=5)
        ttk.Button(action_frame, text="Editar", bootstyle="warning-outline", command=self._editar_tratamiento).pack(side="left")
        ttk.Button(action_frame, text="Eliminar", bootstyle="danger-outline", command=self._eliminar_tratamiento).pack(side="left", padx=5)
        self._cargar_tratamientos()

    def _cargar_tratamientos(self):
        for i in self.tree_trat.get_children(): self.tree_trat.delete(i)
        for t in controlador.obtener_lista_tratamientos():
            eq = "Sí" if t['requiere_equipo_especial'] else "No"
            self.tree_trat.insert("", "end", values=(t['id'], t['nombre'], t['duracion_minutos'], t['costo'], eq))

    def _nuevo_tratamiento(self):
        def cb(d):
            try:
                controlador.registrar_tratamiento(d['nombre'], d['duracion'], d['costo'], d['equipo'])
                self._cargar_tratamientos()
            except Exception as e: messagebox.showerror("Error", str(e))
        VentanaFormularioTratamiento(self, cb)

    def _editar_tratamiento(self):
        sel = self.tree_trat.selection()
        if not sel: return
        vals = self.tree_trat.item(sel[0])['values']
        data = {"id": vals[0], "nombre": vals[1], "duracion_minutos": vals[2], "costo": vals[3], "requiere_equipo_especial": 1 if vals[4]=="Sí" else 0}
        def cb(d):
            try:
                controlador.modificar_tratamiento(d['id'], d['nombre'], d['duracion'], d['costo'], d['equipo'])
                self._cargar_tratamientos()
            except Exception as e: messagebox.showerror("Error", str(e))
        VentanaFormularioTratamiento(self, cb, existente=data)

    def _eliminar_tratamiento(self):
        sel = self.tree_trat.selection()
        if not sel: return
        t_id = self.tree_trat.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar tratamiento?"):
            controlador.borrar_tratamiento(t_id)
            self._cargar_tratamientos()


    # GESTIÓN DE CONSULTORIOS

    def _construir_tab_consultorios(self):
        tool_frame = ttk.Frame(self.tab_consultorios); tool_frame.pack(fill="x", pady=5)
        ttk.Button(tool_frame, text="+ Nuevo Consultorio", bootstyle="success", command=self._nuevo_consultorio).pack(side="left")
        ttk.Button(tool_frame, text="Refrescar", bootstyle="info-outline", command=self._cargar_consultorios).pack(side="left", padx=5)

        cols = ("ID", "Nombre", "Equipo Especial")
        self.tree_cons = ttk.Treeview(self.tab_consultorios, columns=cols, show="headings", height=8)
        self.tree_cons.heading("ID", text="ID"); self.tree_cons.column("ID", width=40)
        self.tree_cons.heading("Nombre", text="Nombre Sala"); self.tree_cons.column("Nombre", width=200)
        self.tree_cons.heading("Equipo Especial", text="Equipo Esp."); self.tree_cons.column("Equipo Especial", width=100)
        self.tree_cons.pack(fill="both", expand=True, pady=5)

        action_frame = ttk.Frame(self.tab_consultorios); action_frame.pack(fill="x", pady=5)
        ttk.Button(action_frame, text="Editar", bootstyle="warning-outline", command=self._editar_consultorio).pack(side="left")
        ttk.Button(action_frame, text="Eliminar", bootstyle="danger-outline", command=self._eliminar_consultorio).pack(side="left", padx=5)
        self._cargar_consultorios()

    def _cargar_consultorios(self):
        for i in self.tree_cons.get_children(): self.tree_cons.delete(i)
        for c in controlador.obtener_lista_consultorios():
            eq = "Sí" if c['equipo_especial'] else "No"
            self.tree_cons.insert("", "end", values=(c['id'], c['nombre_sala'], eq))

    def _nuevo_consultorio(self):
        def cb(d):
            try:
                controlador.registrar_consultorio(d['nombre'], d['equipo'])
                self._cargar_consultorios()
            except Exception as e: messagebox.showerror("Error", str(e))
        VentanaFormularioConsultorio(self, cb)

    def _editar_consultorio(self):
        sel = self.tree_cons.selection()
        if not sel: return
        vals = self.tree_cons.item(sel[0])['values']
        data = {"id": vals[0], "nombre_sala": vals[1], "equipo_especial": 1 if vals[2]=="Sí" else 0}
        def cb(d):
            try:
                controlador.modificar_consultorio(d['id'], d['nombre'], d['equipo'])
                self._cargar_consultorios()
            except Exception as e: messagebox.showerror("Error", str(e))
        VentanaFormularioConsultorio(self, cb, existente=data)

    def _eliminar_consultorio(self):
        sel = self.tree_cons.selection()
        if not sel: return
        c_id = self.tree_cons.item(sel[0])['values'][0]
        if messagebox.askyesno("Confirmar", "¿Eliminar consultorio?"):
            controlador.borrar_consultorio(c_id)
            self._cargar_consultorios()

    # =========================================================================
    # SECCIÓN PAPELERA DE RECICLAJE
    # =========================================================================
    def _construir_tab_papelera(self):
        # Selector de Tipo
        top_frame = ttk.Frame(self.tab_papelera)
        top_frame.pack(fill="x", pady=10)
        
        ttk.Label(top_frame, text="Ver eliminados de:").pack(side="left")
        
        self.cmb_tipo_papelera = ttk.Combobox(
            top_frame, 
            values=["Pacientes", "Dentistas", "Usuarios", "Tratamientos", "Consultorios"], 
            state="readonly",
            width=20
        )
        self.cmb_tipo_papelera.pack(side="left", padx=10)
        self.cmb_tipo_papelera.set("Pacientes") # Default
        self.cmb_tipo_papelera.bind("<<ComboboxSelected>>", lambda e: self._cargar_papelera())

        ttk.Button(top_frame, text="Refrescar", command=self._cargar_papelera, bootstyle="info-outline").pack(side="left")

        # Tabla Genérica
        self.tree_papelera = ttk.Treeview(self.tab_papelera, columns=("ID", "Nombre", "Extra"), show="headings", height=10)
        self.tree_papelera.heading("ID", text="ID")
        self.tree_papelera.heading("Nombre", text="Nombre / Descripción")
        self.tree_papelera.heading("Extra", text="Info Adicional")
        
        self.tree_papelera.column("ID", width=50, anchor="center")
        self.tree_papelera.column("Nombre", width=300)
        self.tree_papelera.column("Extra", width=200)
        
        self.tree_papelera.pack(fill="both", expand=True, pady=5)

        # Botón Restaurar
        btn_frame = ttk.Frame(self.tab_papelera)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="♻ Restaurar Seleccionado", bootstyle="success", command=self._restaurar_item).pack(side="right")

        self._cargar_papelera()

    def _cargar_papelera(self):
        # Limpiar
        for item in self.tree_papelera.get_children(): self.tree_papelera.delete(item)
        
        tipo = self.cmb_tipo_papelera.get()
        items = controlador.obtener_eliminados(tipo)
        
        if not items:
            return

        for item in items:
            # Adaptamos los datos para que encajen en las 3 columnas genéricas
            col_id = item['id']
            # Intentamos buscar claves comunes, si no existen, ponemos string vacío
            col_nombre = item.get('nombre') or item.get('nombre_usuario') or item.get('nombre_sala')
            
            col_extra = ""
            if tipo == "Usuarios": col_extra = f"Rol: {item['rol']}"
            elif tipo == "Dentistas": col_extra = item['especialidad']
            elif tipo == "Pacientes": col_extra = f"DNI: {item.get('dni', '-')}"
            elif tipo == "Tratamientos": col_extra = f"S/. {item['costo']}"
            
            self.tree_papelera.insert("", "end", values=(col_id, col_nombre, col_extra))

    def _restaurar_item(self):
        sel = self.tree_papelera.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccione un elemento para restaurar.")
            return
        
        item_id = self.tree_papelera.item(sel[0])['values'][0]
        nombre = self.tree_papelera.item(sel[0])['values'][1]
        tipo = self.cmb_tipo_papelera.get()

        if messagebox.askyesno("Confirmar", f"¿Restaurar '{nombre}' en {tipo}?"):
            try:
                controlador.restaurar_elemento(tipo, item_id)
                messagebox.showinfo("Éxito", "Elemento restaurado y activo nuevamente.")
                self._cargar_papelera()
                
                # Actualizar las otras pestañas si es necesario
                if tipo == "Usuarios": self._cargar_usuarios()
                elif tipo == "Dentistas": self._cargar_dentistas()
                elif tipo == "Tratamientos": self._cargar_tratamientos()
                elif tipo == "Consultorios": self._cargar_consultorios()
                
            except Exception as e:
                messagebox.showerror("Error", str(e))
import ttkbootstrap as ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from gui.vista_pacientes import PaginaPacientes
from gui.vista_cita import PaginaAgendarCita
from gui.vista_admin import PaginaAdministracion

class PaginaDashboard(ttk.Frame):
    # --- CORRECCIÓN AQUÍ: Se añade usuario_data=None ---
    def __init__(self, parent, usuario_data=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        ttk.Label(self, text="Dashboard - Citas de Hoy", font=("Segoe UI", 18, "bold")).pack(pady=20, padx=20)
        # Aquí implementaremos la tabla de citas del día más adelante

class App(ttk.Toplevel):
    def __init__(self, parent, usuario_data):
        super().__init__(parent)
        
        self.usuario_data = usuario_data 
        
        # Mostramos quién está logueado en el título
        self.title(f"Clínica Dental - (Usuario: {self.usuario_data['nombre_usuario']} | Rol: {self.usuario_data['rol']})")
        
        self._centrar_ventana(1280, 720) 

        self.protocol("WM_DELETE_WINDOW", self.accion_no_permitida)
        self.crear_widgets()

    def _centrar_ventana(self, width, height):
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def accion_no_permitida(self):
        messagebox.showwarning("Acción no permitida", "Usa el botón 'Salir' para cerrar la aplicación.")

    def crear_widgets(self):
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        
        # --- Sidebar ---
        sidebar = ttk.Frame(container, width=200, bootstyle="secondary")
        sidebar.grid(row=0, column=0, sticky="ns")
        
        try:
            logo_img = Image.open("assets/logo.png").resize((150, 150), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_img)
            ttk.Label(sidebar, image=self.logo, bootstyle="secondary").pack(pady=20)
        except FileNotFoundError:
            ttk.Label(sidebar, text="Logo Aquí", bootstyle="secondary", font=("Segoe UI", 16)).pack(pady=20)
            
        # --- Botones de Navegación ---
        nav_frame = ttk.Frame(sidebar, bootstyle="secondary")
        nav_frame.pack(fill="x", padx=10, pady=10)
        
        self.nav_buttons = {}
        
        # 1. Definimos los botones básicos disponibles para todos
        buttons_info = [
            ("Dashboard", "Dashboard"),
            ("Agendar Cita", "AgendarCita"),
            ("Pacientes", "Pacientes")
        ]
        
        # 2. Si el usuario es ADMIN, agregamos el botón de Administración
        if self.usuario_data['rol'] == 'admin':
            buttons_info.append(("Administración", "Administracion"))
        
        for text, page_name in buttons_info:
            btn = ttk.Button(
                nav_frame, 
                text=text, 
                command=lambda p=page_name: self.mostrar_pagina(p), 
                bootstyle="light-outline"
            )
            btn.pack(fill="x", pady=4)
            self.nav_buttons[page_name] = btn
        
        # --- Botones de Salida ---
        footer_frame = ttk.Frame(sidebar, bootstyle="secondary")
        footer_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        # Cerrar Sesión: Cierra esta ventana (App) y vuelve al Login
        ttk.Button(footer_frame, text="Cerrar Sesión", command=self.destroy, bootstyle="warning-outline").pack(fill="x", pady=4)
        
        # Salir: Cierra la ventana maestra (Login) y termina el programa
        ttk.Button(footer_frame, text="Salir", command=self.master.destroy, bootstyle="danger").pack(fill="x", pady=4)
        
        # --- Contenedor de Páginas ---
        self.paginas_container = ttk.Frame(container)
        self.paginas_container.grid(row=0, column=1, sticky="nsew")
        self.paginas_container.grid_rowconfigure(0, weight=1)
        self.paginas_container.grid_columnconfigure(0, weight=1)
        
        self.paginas = {}
        
        # Mapeo de nombres a Clases
        clases_map = {
            "Dashboard": PaginaDashboard,
            "AgendarCita": PaginaAgendarCita,
            "Pacientes": PaginaPacientes,
            "Administracion": PaginaAdministracion
        }
        
        for page_name, Clase in clases_map.items():
            # Seguridad extra: No crear la página de admin si no es admin
            if page_name == "Administracion" and self.usuario_data['rol'] != 'admin':
                continue

            # Instanciamos la página pasando el usuario_data
            frame = Clase(self.paginas_container, usuario_data=self.usuario_data)
            self.paginas[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.mostrar_pagina("Dashboard") 

    def mostrar_pagina(self, page_name):
        # Actualizar estilos de botones
        for name, button in self.nav_buttons.items():
            if name == page_name:
                button.config(bootstyle="light") 
            else:
                button.config(bootstyle="light-outline")
        
        # Levantar la página seleccionada
        frame = self.paginas[page_name]
        frame.tkraise()
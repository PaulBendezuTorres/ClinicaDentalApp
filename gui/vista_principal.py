import ttkbootstrap as ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from gui.vista_pacientes import PaginaPacientes
from gui.vista_cita import PaginaAgendarCita 

class PaginaDashboard(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Dashboard - Citas de Hoy", font=("Segoe UI", 18, "bold")).pack(pady=20, padx=20)
        
# --- CAMBIOS AQUÍ ---
class App(ttk.Toplevel): # 1. Cambiado de ttk.Window a ttk.Toplevel
    
    # 2. El __init__ ahora acepta 'parent' y 'usuario_data'
    def __init__(self, parent, usuario_data):
        super().__init__(parent) # 3. Se llama al super() de Toplevel
        
        self.usuario_data = usuario_data 
        
        self.title(f"Clínica Dental - (Usuario: {self.usuario_data['nombre_usuario']})")
        
        self._centrar_ventana(1280, 720) 

        self.protocol("WM_DELETE_WINDOW", self.accion_no_permitida)
        self.crear_widgets()
    # --- FIN DE CAMBIOS ---

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
        
        sidebar = ttk.Frame(container, width=200, bootstyle="secondary")
        sidebar.grid(row=0, column=0, sticky="ns")
        
        try:
            logo_img = Image.open("assets/logo.png").resize((150, 150), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_img)
            # Esta línea ahora funcionará
            ttk.Label(sidebar, image=self.logo, bootstyle="secondary").pack(pady=20)
        except FileNotFoundError:
            ttk.Label(sidebar, text="Logo Aquí", bootstyle="secondary", font=("Segoe UI", 16)).pack(pady=20)
            
        # --- Frame para botones de navegación ---
        nav_frame = ttk.Frame(sidebar, bootstyle="secondary")
        nav_frame.pack(fill="x", padx=10, pady=10)
        
        self.nav_buttons = {}
        buttons_info = [
            ("Dashboard", "Dashboard"),
            ("Agendar Cita", "AgendarCita"),
            ("Pacientes", "Pacientes")
        ]
        
        for text, page_name in buttons_info:
            btn = ttk.Button(
                nav_frame, 
                text=text, 
                command=lambda p=page_name: self.mostrar_pagina(p), 
                bootstyle="light-outline"
            )
            btn.pack(fill="x", pady=4)
            self.nav_buttons[page_name] = btn
        
        # --- Frame para botones de salida (al fondo) ---
        footer_frame = ttk.Frame(sidebar, bootstyle="secondary")
        footer_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        # Este botón ahora destruye SÓLO esta ventana (App), permitiendo volver al login.
        ttk.Button(footer_frame, text="Cerrar Sesión", command=self.destroy, bootstyle="warning-outline").pack(fill="x", pady=4)
        
        # Este botón destruye la ventana MAESTRA (el login), cerrando toda la aplicación.
        ttk.Button(footer_frame, text="Salir", command=self.master.destroy, bootstyle="danger").pack(fill="x", pady=4)
        # --- Contenedor de páginas ---
        
        self.paginas_container = ttk.Frame(container)
        self.paginas_container.grid(row=0, column=1, sticky="nsew")
        
        self.paginas_container.grid_rowconfigure(0, weight=1)
        self.paginas_container.grid_columnconfigure(0, weight=1)
        
        self.paginas = {}
        
        for F in (PaginaDashboard, PaginaAgendarCita, PaginaPacientes):
            page_name = F.__name__.replace("Pagina", "")
            frame = F(self.paginas_container)
            self.paginas[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.mostrar_pagina("Dashboard") 
        

    def mostrar_pagina(self, page_name):
        for name, button in self.nav_buttons.items():
            if name == page_name:
                button.config(bootstyle="light") 
            else:
                button.config(bootstyle="light-outline")
        
        frame = self.paginas[page_name]
        frame.tkraise()
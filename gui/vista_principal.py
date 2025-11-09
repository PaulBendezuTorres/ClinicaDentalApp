import ttkbootstrap as ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from gui.vista_pacientes import PaginaPacientes

class PaginaDashboard(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Dashboard - Citas de Hoy", font=("Segoe UI", 18, "bold")).pack(pady=20, padx=20)

class PaginaAgendarCita(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        ttk.Label(self, text="Agendar Nueva Cita", font=("Segoe UI", 18, "bold")).pack(pady=20, padx=20)

class App(ttk.Window):
    def __init__(self):
        super().__init__(themename="superhero")
        self.title("Clínica Dental")
        
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
        
        sidebar = ttk.Frame(container, width=200, bootstyle="secondary")
        sidebar.grid(row=0, column=0, sticky="ns")
        
        try:
            logo_img = Image.open("assets/logo.png").resize((150, 150), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo_img)
            ttk.Label(sidebar, image=self.logo).pack(pady=20)
        except FileNotFoundError:
            ttk.Label(sidebar, text="Logo Aquí").pack(pady=20)
            
        ttk.Button(sidebar, text="Dashboard", command=lambda: self.mostrar_pagina("Dashboard"), bootstyle="info").pack(fill="x", padx=10, pady=5)
        ttk.Button(sidebar, text="Agendar Cita", command=lambda: self.mostrar_pagina("AgendarCita"), bootstyle="info").pack(fill="x", padx=10, pady=5)
        ttk.Button(sidebar, text="Pacientes", command=lambda: self.mostrar_pagina("Pacientes"), bootstyle="info").pack(fill="x", padx=10, pady=5)
        
        ttk.Button(sidebar, text="Salir", command=self.destroy, bootstyle="danger").pack(side="bottom", fill="x", padx=10, pady=10)
        ttk.Button(sidebar, text="Cerrar Sesión", command=lambda: print("TODO: Implementar Login"), bootstyle="warning").pack(side="bottom", fill="x", padx=10, pady=5)
        
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
        frame = self.paginas[page_name]
        frame.tkraise()
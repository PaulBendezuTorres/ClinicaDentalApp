import ttkbootstrap as ttk
from tkinter import messagebox

class VistaLogin(ttk.Window):
    def __init__(self, on_login_success):
        super().__init__(themename="superhero", title="Clínica Dental - Inicio de Sesión")
        self.on_login_success = on_login_success

        self.update_idletasks()
        width = 400
        height = 450
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)

        self._build()

    def _build(self):
        main_frame = ttk.Frame(self, padding=40)
        main_frame.pack(expand=True, fill="both")

        ttk.Label(main_frame, text="Clínica Dental", font=("Segoe UI", 24, "bold"), bootstyle="primary").pack(pady=(0, 30))

        ttk.Label(main_frame, text="Nombre de Usuario:").pack(anchor="w")
        self.ent_usuario = ttk.Entry(main_frame)
        self.ent_usuario.pack(fill="x", pady=5)
        self.ent_usuario.focus_set()

        ttk.Label(main_frame, text="Contraseña:").pack(anchor="w", pady=(10, 0))
        self.ent_contrasena = ttk.Entry(main_frame, show="*")
        self.ent_contrasena.pack(fill="x", pady=5)
        
        self.lbl_error = ttk.Label(main_frame, text="", bootstyle="danger")
        self.lbl_error.pack(pady=10)

        btn_ingresar = ttk.Button(main_frame, text="Ingresar", command=self._on_ingresar, bootstyle="success")
        btn_ingresar.pack(fill="x", pady=20)

        self.ent_contrasena.bind("<Return>", self._on_ingresar)
        self.ent_usuario.bind("<Return>", lambda e: self.ent_contrasena.focus_set())

    def _on_ingresar(self, event=None):
        from logic import controlador 
        
        usuario = self.ent_usuario.get().strip()
        contrasena = self.ent_contrasena.get()
        
        self.lbl_error.config(text="") 

        if not usuario or not contrasena:
            self.lbl_error.config(text="Por favor, ingrese usuario y contraseña.")
            return

        usuario_data = controlador.verificar_credenciales(usuario, contrasena)

        if usuario_data:
            self.withdraw() 
            
            self.on_login_success(self, usuario_data) 

            self.destroy()
        else:
            self.lbl_error.config(text="Credenciales incorrectas.")
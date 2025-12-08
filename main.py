import tkinter as tk
from tkinter import messagebox
import ctypes 
import atexit
from gui.vista_principal import App
from gui.vista_login import VistaLogin
from database.conexion import get_db_connection
from logic import controlador

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass 

def _test_db_connection():
    try:
        cn = get_db_connection()
        cn.close()
        return True
    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{e}")
        return False

def iniciar_app_principal(parent_window, usuario_data):
    """
    Se ejecuta cuando el login es exitoso.
    parent_window: Es la instancia de VistaLogin (que está oculta/withdraw)
    """
    print(f"Login exitoso. Bienvenido {usuario_data['nombre_usuario']} (Rol: {usuario_data['rol']})")
    
    app = App(parent=parent_window, usuario_data=usuario_data)
    
    app.grab_set()
    
    app.wait_window()

if __name__ == "__main__":

    atexit.register(controlador.cerrar_prolog)

    if _test_db_connection():

        login_window = VistaLogin(on_login_success=iniciar_app_principal)
        login_window.mainloop()
    else:
        print("La aplicación no se puede iniciar debido a un error de conexión con la base de datos.")

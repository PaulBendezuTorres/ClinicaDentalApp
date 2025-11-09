import tkinter as tk
from tkinter import messagebox
from gui.vista_principal import App
from gui.vista_login import VistaLogin 
from database.conexion import get_db_connection
import atexit
from logic import controlador

def _test_db_connection():
    try:
        cn = get_db_connection()
        cn.close()
        return True
    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{e}")
        return False


def iniciar_app_principal(usuario_data):
    print(f"Login exitoso. Bienvenido {usuario_data['nombre_usuario']} (Rol: {usuario_data['rol']})")
    app = App(usuario_data) 
    app.mainloop()

if __name__ == "__main__":
    atexit.register(controlador.cerrar_prolog)

    if _test_db_connection():

        login_window = VistaLogin(on_login_success=iniciar_app_principal)
        login_window.mainloop()
    else:
        print("La aplicación no se puede iniciar debido a un error de conexión con la base de datos.")

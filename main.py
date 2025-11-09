import tkinter as tk
from tkinter import messagebox
from gui.vista_principal import App  
from database.conexion import get_db_connection

def _test_db_connection():
    try:
        cn = get_db_connection()
        cn.close()
        return True
    except Exception as e:
        messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{e}")
        return False

if __name__ == "__main__":
    if _test_db_connection():
        app = App()  # <-- CAMBIO 2: Creamos una instancia de 'App'
        app.mainloop()
    else:
        # Si la conexión falla, es buena idea no abrir la app.
        # Podemos simplemente imprimir un mensaje y salir.
        print("La aplicación no se puede iniciar debido a un error de conexión con la base de datos.")
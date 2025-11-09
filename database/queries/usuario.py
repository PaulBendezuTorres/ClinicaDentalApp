from typing import Dict, Optional
from database.conexion import get_db_connection

def obtener_usuario_por_nombre(nombre_usuario: str) -> Optional[Dict]:
    """Busca un usuario por su nombre de usuario y devuelve sus datos."""
    cn = get_db_connection()
    cur = cn.cursor(dictionary=True) # dictionary=True es muy útil aquí
    cur.execute(
        "SELECT id, nombre_usuario, contrasena_hash, rol FROM usuarios WHERE nombre_usuario = %s",
        (nombre_usuario,)
    )
    usuario = cur.fetchone()
    cur.close(); cn.close()
    return usuario
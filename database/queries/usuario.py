from typing import List, Dict, Optional
from database.conexion import get_db_connection
from database.db_utils import fetch_all_dict

def obtener_usuario_por_nombre(nombre_usuario: str) -> Optional[Dict]:
    cn = get_db_connection()
    cur = cn.cursor(dictionary=True)
    cur.execute("SELECT id, nombre_usuario, contrasena_hash, rol, activo FROM usuarios WHERE nombre_usuario = %s AND activo = 1", (nombre_usuario,))
    usuario = cur.fetchone()
    cur.close(); cn.close()
    return usuario

def obtener_todos_usuarios() -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    # Solo traemos usuarios activos
    cur.execute("SELECT id, nombre_usuario, rol FROM usuarios WHERE activo = 1 ORDER BY nombre_usuario")
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def crear_usuario_db(nombre: str, hash_pw: str, rol: str):
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute(
        "INSERT INTO usuarios (nombre_usuario, contrasena_hash, rol) VALUES (%s, %s, %s)",
        (nombre, hash_pw, rol)
    )
    cur.close(); cn.close()

def actualizar_usuario_db(user_id: int, nombre: str, rol: str, hash_pw: str = None):
    cn = get_db_connection()
    cur = cn.cursor()
    if hash_pw:
        # Si hay nueva contraseña, actualizamos todo
        cur.execute(
            "UPDATE usuarios SET nombre_usuario=%s, rol=%s, contrasena_hash=%s WHERE id=%s",
            (nombre, rol, hash_pw, user_id)
        )
    else:
        # Si no, solo actualizamos nombre y rol
        cur.execute(
            "UPDATE usuarios SET nombre_usuario=%s, rol=%s WHERE id=%s",
            (nombre, rol, user_id)
        )
    cur.close(); cn.close()

def eliminar_usuario_db(user_id: int):
    """Borrado lógico"""
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("UPDATE usuarios SET activo = 0 WHERE id = %s", (user_id,))
    cur.close(); cn.close()
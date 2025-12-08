from typing import List, Dict
from database.conexion import get_db_connection
from database.db_utils import fetch_all_dict

def obtener_consultorios() -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("SELECT id, nombre_sala, equipo_especial FROM consultorios WHERE activo = 1 ORDER BY id")
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def crear_consultorio_db(nombre: str, equipo_especial: int):
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("INSERT INTO consultorios (nombre_sala, equipo_especial) VALUES (%s, %s)", (nombre, equipo_especial))
    cur.close(); cn.close()

def actualizar_consultorio_db(c_id: int, nombre: str, equipo_especial: int):
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("UPDATE consultorios SET nombre_sala=%s, equipo_especial=%s WHERE id=%s", (nombre, equipo_especial, c_id))
    cur.close(); cn.close()

def eliminar_consultorio_db(c_id: int):
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("UPDATE consultorios SET activo = 0 WHERE id = %s", (c_id,))
    cur.close(); cn.close()

def obtener_consultorios_eliminados() -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("SELECT id, nombre_sala AS nombre FROM consultorios WHERE activo = 0")
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def reactivar_consultorio_db(id: int):
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("UPDATE consultorios SET activo = 1 WHERE id = %s", (id,))
    cur.close(); cn.close()
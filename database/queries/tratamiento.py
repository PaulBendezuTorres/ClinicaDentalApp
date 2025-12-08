from typing import List, Dict, Optional
from database.conexion import get_db_connection
from database.db_utils import fetch_all_dict

def obtener_tratamientos() -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("SELECT id, nombre, duracion_minutos, costo, requiere_equipo_especial FROM tratamientos WHERE activo = 1 ORDER BY nombre")
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def obtener_tratamiento_por_id(tratamiento_id: int) -> Optional[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("SELECT * FROM tratamientos WHERE id=%s", (tratamiento_id,))
    row = cur.fetchone()
    cur.close(); cn.close()
    if not row: return None
    return {"id": row[0], "nombre": row[1], "duracion_minutos": row[2], "costo": float(row[3]), "requiere_equipo_especial": int(row[4])}

def crear_tratamiento_db(nombre: str, duracion: int, costo: float, requiere_equipo: int):
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute(
        "INSERT INTO tratamientos (nombre, duracion_minutos, costo, requiere_equipo_especial) VALUES (%s, %s, %s, %s)",
        (nombre, duracion, costo, requiere_equipo)
    )
    cur.close(); cn.close()

def actualizar_tratamiento_db(t_id: int, nombre: str, duracion: int, costo: float, requiere_equipo: int):
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute(
        "UPDATE tratamientos SET nombre=%s, duracion_minutos=%s, costo=%s, requiere_equipo_especial=%s WHERE id=%s",
        (nombre, duracion, costo, requiere_equipo, t_id)
    )
    cur.close(); cn.close()

def eliminar_tratamiento_db(t_id: int):
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("UPDATE tratamientos SET activo = 0 WHERE id = %s", (t_id,))
    cur.close(); cn.close()

def obtener_tratamientos_eliminados() -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("SELECT id, nombre, costo FROM tratamientos WHERE activo = 0")
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def reactivar_tratamiento_db(id: int):
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("UPDATE tratamientos SET activo = 1 WHERE id = %s", (id,))
    cur.close(); cn.close()
    
from typing import List, Dict, Optional
from database.conexion import get_db_connection
from database.db_utils import fetch_all_dict

def obtener_dentistas() -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    # Solo traemos dentistas activos
    cur.execute("SELECT id, nombre, especialidad FROM dentistas WHERE activo = 1 ORDER BY nombre")
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def obtener_dentista_por_id(dentista_id: int) -> Optional[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("SELECT id, nombre, especialidad FROM dentistas WHERE id=%s", (dentista_id,))
    row = cur.fetchone()
    cur.close(); cn.close()
    if not row: return None
    return {"id": row[0], "nombre": row[1], "especialidad": row[2]}

def crear_dentista_db(nombre: str, especialidad: str):
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute(
        "INSERT INTO dentistas (nombre, especialidad) VALUES (%s, %s)",
        (nombre, especialidad)
    )
    cur.close(); cn.close()

def actualizar_dentista_db(dentista_id: int, nombre: str, especialidad: str):
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute(
        "UPDATE dentistas SET nombre=%s, especialidad=%s WHERE id=%s",
        (nombre, especialidad, dentista_id)
    )
    cur.close(); cn.close()

def eliminar_dentista_db(dentista_id: int):
    """Borrado lógico"""
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("UPDATE dentistas SET activo = 0 WHERE id = %s", (dentista_id,))
    cur.close(); cn.close()
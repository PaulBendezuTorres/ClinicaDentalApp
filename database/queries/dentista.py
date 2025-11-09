from typing import List, Dict, Optional
from database.conexion import get_db_connection
from database.db_utils import fetch_all_dict

def obtener_dentistas() -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("SELECT id, nombre, especialidad FROM dentistas ORDER BY nombre")
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
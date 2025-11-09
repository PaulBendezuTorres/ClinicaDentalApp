from typing import List, Dict, Optional
from database.conexion import get_db_connection
from database.db_utils import fetch_all_dict

def obtener_tratamientos() -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("""SELECT id, nombre, duracion_minutos, costo, requiere_equipo_especial 
                   FROM tratamientos ORDER BY nombre""")
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def obtener_tratamiento_por_id(tratamiento_id: int) -> Optional[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("""SELECT id, nombre, duracion_minutos, costo, requiere_equipo_especial 
                   FROM tratamientos WHERE id=%s""", (tratamiento_id,))
    row = cur.fetchone(); cur.close(); cn.close()
    if not row: return None
    return {
        "id": row[0], "nombre": row[1], "duracion_minutos": row[2],
        "costo": float(row[3]), "requiere_equipo_especial": int(row[4])
    }
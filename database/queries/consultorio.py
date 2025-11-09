from typing import List, Dict
from database.conexion import get_db_connection
from database.db_utils import fetch_all_dict

def obtener_consultorios() -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("SELECT id, nombre_sala, equipo_especial FROM consultorios ORDER BY id")
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data
from typing import List, Dict
from database.conexion import get_db_connection
from database.db_utils import fetch_all_dict

def obtener_reglas_horarios_dentistas() -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("""
        SELECT h.id, h.dentista_id, d.nombre AS dentista_nombre,
               h.dia_semana, h.hora_inicio, h.hora_fin
        FROM horarios_dentistas h
        JOIN dentistas d ON d.id = h.dentista_id
        ORDER BY d.nombre, FIELD(h.dia_semana,'lunes','martes','miercoles','jueves','viernes','sabado','domingo'), h.hora_inicio
    """)
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data
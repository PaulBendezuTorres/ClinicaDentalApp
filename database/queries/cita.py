from typing import List, Dict
from database.conexion import get_db_connection
from database.db_utils import fetch_all_dict

def obtener_citas_por_paciente(paciente_id: int) -> List[Dict]:
    """Obtiene todas las citas de un paciente, con nombres de dentista y tratamiento."""
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("""
        SELECT 
            c.fecha, 
            c.hora_inicio, 
            d.nombre AS dentista_nombre, 
            t.nombre AS tratamiento_nombre,
            t.costo
        FROM citas c
        JOIN dentistas d ON d.id = c.dentista_id
        JOIN tratamientos t ON t.id = c.tratamiento_id
        WHERE c.paciente_id = %s
        ORDER BY c.fecha DESC, c.hora_inicio DESC
    """, (paciente_id,))
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def guardar_nueva_cita(paciente_id: int, dentista_id: int, consultorio_id: int,
                       tratamiento_id: int, fecha: str, hora_inicio: str) -> int:
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("""
        INSERT INTO citas(paciente_id, dentista_id, consultorio_id, 
                          tratamiento_id, fecha, hora_inicio)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (paciente_id, dentista_id, consultorio_id, tratamiento_id, fecha, hora_inicio))
    new_id = cur.lastrowid
    cur.close(); cn.close()
    return new_id
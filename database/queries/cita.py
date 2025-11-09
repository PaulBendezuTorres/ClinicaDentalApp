from typing import List, Dict
from database.conexion import get_db_connection
from database.db_utils import fetch_all_dict

def obtener_citas_por_fecha(fecha: str) -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    # (El resto de la función es idéntico)
    cur.execute("""
        SELECT 
            c.id, c.paciente_id, p.nombre AS paciente_nombre,
            c.dentista_id, d.nombre AS dentista_nombre,
            c.consultorio_id, s.nombre_sala AS consultorio_nombre,
            c.tratamiento_id, t.nombre AS tratamiento_nombre,
            t.duracion_minutos, t.requiere_equipo_especial,
            c.fecha, c.hora_inicio
        FROM citas c
        JOIN pacientes p ON p.id = c.paciente_id
        JOIN dentistas d ON d.id = c.dentista_id
        JOIN consultorios s ON s.id = c.consultorio_id
        JOIN tratamientos t ON t.id = c.tratamiento_id
        WHERE c.fecha = %s
        ORDER BY c.hora_inicio
    """, (fecha,))
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
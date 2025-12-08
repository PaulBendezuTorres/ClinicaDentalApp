
from typing import List, Dict
from database.conexion import get_db_connection
from database.db_utils import fetch_all_dict

def obtener_citas_por_fecha(fecha: str) -> List[Dict]:
    """Obtiene todas las citas para una fecha específica."""
    cn = get_db_connection()
    cur = cn.cursor()
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
    """Inserta una nueva cita en la base de datos."""
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

def obtener_citas_por_paciente(paciente_id: int) -> List[Dict]:
    """Obtiene todas las citas de un paciente, con nombres de dentista y tratamiento."""
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("""
        SELECT 
            c.fecha, c.hora_inicio, d.nombre AS dentista_nombre, 
            t.nombre AS tratamiento_nombre, t.costo
        FROM citas c
        JOIN dentistas d ON d.id = c.dentista_id
        JOIN tratamientos t ON t.id = c.tratamiento_id
        WHERE c.paciente_id = %s
        ORDER BY c.fecha DESC, c.hora_inicio DESC
    """, (paciente_id,))
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def obtener_todas_citas(filtro_fecha: str = None, busqueda: str = "") -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    
    sql = """
        SELECT 
            c.id, c.fecha, c.hora_inicio, c.estado,
            p.nombre AS paciente,
            d.nombre AS dentista,
            t.nombre AS tratamiento,
            s.nombre_sala AS consultorio
        FROM citas c
        JOIN pacientes p ON c.paciente_id = p.id
        JOIN dentistas d ON c.dentista_id = d.id
        JOIN tratamientos t ON c.tratamiento_id = t.id
        JOIN consultorios s ON c.consultorio_id = s.id
        WHERE 1=1
    """
    
    params = []
    
    # 1. Filtro de Fecha
    if filtro_fecha == 'hoy':
        sql += " AND c.fecha = CURDATE()"
    elif filtro_fecha == 'futuras':
        sql += " AND c.fecha >= CURDATE()"
    # Si es 'todas', no agregamos restricción de fecha
    
    # 2. Filtro de Búsqueda (Nombre del paciente)
    if busqueda:
        sql += " AND p.nombre LIKE %s"
        params.append(f"%{busqueda}%")
    
    sql += " ORDER BY c.fecha, c.hora_inicio"
    
    cur.execute(sql, tuple(params))
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def actualizar_estado_cita_db(cita_id: int, nuevo_estado: str):
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("UPDATE citas SET estado = %s WHERE id = %s", (nuevo_estado, cita_id))
    cur.close(); cn.close()
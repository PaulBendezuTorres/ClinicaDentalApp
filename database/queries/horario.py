from typing import List, Dict
from database.conexion import get_db_connection
from database.db_utils import fetch_all_dict

def obtener_reglas_horarios_dentistas() -> List[Dict]:
    """Usado por el motor de búsqueda (Prolog). Trae todo."""
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("""
        SELECT h.id, h.dentista_id, d.nombre AS dentista_nombre,
               h.dia_semana, h.hora_inicio, h.hora_fin
        FROM horarios_dentistas h
        JOIN dentistas d ON d.id = h.dentista_id
        WHERE d.activo = 1 
        ORDER BY d.nombre, FIELD(h.dia_semana,'lunes','martes','miercoles','jueves','viernes','sabado','domingo'), h.hora_inicio
    """)
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def obtener_horarios_por_dentista(dentista_id: int) -> List[Dict]:
    """Usado por la vista de administración. Trae horarios de UN dentista."""
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("""
        SELECT id, dia_semana, hora_inicio, hora_fin
        FROM horarios_dentistas
        WHERE dentista_id = %s
        ORDER BY FIELD(dia_semana,'lunes','martes','miercoles','jueves','viernes','sabado','domingo'), hora_inicio
    """, (dentista_id,))
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def agregar_horario(dentista_id: int, dia: str, inicio: str, fin: str):
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("""
        INSERT INTO horarios_dentistas (dentista_id, dia_semana, hora_inicio, hora_fin)
        VALUES (%s, %s, %s, %s)
    """, (dentista_id, dia, inicio, fin))
    cur.close(); cn.close()

def eliminar_horario(horario_id: int):
    """Aquí usamos borrado físico, ya que es configuración y no historial crítico."""
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("DELETE FROM horarios_dentistas WHERE id = %s", (horario_id,))
    cur.close(); cn.close()
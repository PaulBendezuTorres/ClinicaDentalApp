from typing import List, Dict
from database.conexion import get_db_connection
from database.db_utils import fetch_all_dict

def obtener_pacientes() -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    # Pedimos todos los nuevos campos
    cur.execute("SELECT id, nombre, telefono, dni, direccion, correo, genero FROM pacientes ORDER BY nombre")
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def crear_paciente(nombre: str, telefono: str, dni: str, direccion: str, correo: str, genero: str) -> int:
    cn = get_db_connection()
    cur = cn.cursor()
    # Pasamos todos los argumentos al procedimiento
    args = (nombre, telefono, dni, direccion, correo, genero, 0)
    result_args = cur.callproc('sp_crear_paciente', args)
    new_id = result_args[2]
    cur.close(); cn.close()
    return new_id

def actualizar_paciente(id: int, nombre: str, telefono: str, dni: str, direccion: str, correo: str, genero: str):
    cn = get_db_connection()
    cur = cn.cursor()
    args = (id, nombre, telefono, dni, direccion, correo, genero)
    cur.callproc('sp_actualizar_paciente', args)
    cur.close(); cn.close()

def obtener_preferencias_paciente(paciente_id: int) -> List[Dict]:
    """Obtiene los días y turnos no disponibles para un paciente."""
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("""
        SELECT dia_semana, turno 
        FROM preferencias_pacientes 
        WHERE paciente_id = %s
    """, (paciente_id,))
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data
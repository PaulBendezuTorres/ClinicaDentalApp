from typing import List, Dict, Optional
from database.conexion import get_db_connection
from database.db_utils import fetch_all_dict

def obtener_pacientes(filtro_nombre: str = "") -> List[Dict]:
    """
    Obtiene pacientes activos. Si hay filtro, busca por nombre o DNI.
    """
    cn = get_db_connection()
    cur = cn.cursor()
    
    query = "SELECT id, nombre, telefono, dni, direccion, correo, genero FROM pacientes WHERE activo = 1"
    params = []

    if filtro_nombre:
        # Buscamos coincidencias en nombre O en DNI
        query += " AND (nombre LIKE %s OR dni LIKE %s)"
        filtro_like = f"%{filtro_nombre}%"
        params.extend([filtro_like, filtro_like])
    
    query += " ORDER BY nombre"
    
    cur.execute(query, tuple(params))
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def crear_paciente(nombre: str, telefono: str, dni: str, direccion: str, correo: str, genero: str) -> int:
    cn = get_db_connection()
    cur = cn.cursor()
    args = (nombre, telefono, dni, direccion, correo, genero, 0)
    result_args = cur.callproc('sp_crear_paciente', args)
    new_id = result_args[6] # El índice del parámetro OUT depende de tu SP, asumiendo que es el último
    cur.close(); cn.close()
    return new_id

def actualizar_paciente(id: int, nombre: str, telefono: str, dni: str, direccion: str, correo: str, genero: str):
    cn = get_db_connection()
    cur = cn.cursor()
    args = (id, nombre, telefono, dni, direccion, correo, genero)
    cur.callproc('sp_actualizar_paciente', args)
    cur.close(); cn.close()

def obtener_preferencias_paciente(paciente_id: int) -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("SELECT dia_semana, turno FROM preferencias_pacientes WHERE paciente_id = %s", (paciente_id,))
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def desactivar_paciente(paciente_id: int):
    """Realiza un borrado lógico (soft delete)."""
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("UPDATE pacientes SET activo = 0 WHERE id = %s", (paciente_id,))
    cur.close(); cn.close()

def obtener_pacientes_eliminados() -> List[Dict]:
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("SELECT id, nombre, dni FROM pacientes WHERE activo = 0")
    data = fetch_all_dict(cur)
    cur.close(); cn.close()
    return data

def reactivar_paciente_db(id: int):
    cn = get_db_connection()
    cur = cn.cursor()
    cur.execute("UPDATE pacientes SET activo = 1 WHERE id = %s", (id,))
    cur.close(); cn.close()
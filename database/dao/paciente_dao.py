# database/dao/paciente_dao.py
from typing import List, Dict
from database.conexion import get_db_connection
from clases.paciente import Paciente

class PacienteDAO:
    def __init__(self):
        pass

    def _map_row_to_paciente(self, row) -> Paciente:
        """Método auxiliar para convertir un diccionario de BD a objeto Paciente"""
        return Paciente(
            id=row['id'],
            nombre=row['nombre'],
            telefono=row['telefono'],
            dni=row['dni'],
            direccion=row.get('direccion', ''), # .get por si acaso la columna no viene en algunas consultas
            correo=row.get('correo', ''),
            genero=row.get('genero', ''),
            activo=row.get('activo', 1)
        )

    def obtener_todos(self, filtro_nombre: str = "") -> List[Paciente]:
        """Obtiene una lista de OBJETOS Paciente activos."""
        cn = get_db_connection()
        # Usamos dictionary=True para facilitar el mapeo
        cur = cn.cursor(dictionary=True)
        
        query = "SELECT * FROM pacientes WHERE activo = 1"
        params = []

        if filtro_nombre:
            query += " AND (nombre LIKE %s OR dni LIKE %s)"
            filtro_like = f"%{filtro_nombre}%"
            params.extend([filtro_like, filtro_like])
        
        query += " ORDER BY nombre"
        
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close(); cn.close()
        
        # Convertimos los diccionarios a Objetos Paciente
        return [self._map_row_to_paciente(row) for row in rows]

    def crear(self, paciente: Paciente) -> int:
        """Recibe un OBJETO Paciente y lo guarda."""
        cn = get_db_connection()
        cur = cn.cursor()
        args = (paciente.nombre, paciente.telefono, paciente.dni, 
                paciente.direccion, paciente.correo, paciente.genero, 0)
        
        result_args = cur.callproc('sp_crear_paciente', args)
        cn.commit() # Importante en POO
        new_id = result_args[6] 
        cur.close(); cn.close()
        return new_id

    def actualizar(self, paciente: Paciente):
        """Recibe un OBJETO Paciente con los datos nuevos."""
        cn = get_db_connection()
        cur = cn.cursor()
        args = (paciente.id, paciente.nombre, paciente.telefono, paciente.dni, 
                paciente.direccion, paciente.correo, paciente.genero)
        cur.callproc('sp_actualizar_paciente', args)
        cn.commit()
        cur.close(); cn.close()

    def eliminar(self, paciente_id: int):
        """Soft delete."""
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute("UPDATE pacientes SET activo = 0 WHERE id = %s", (paciente_id,))
        cn.commit()
        cur.close(); cn.close()

    def obtener_preferencias(self, paciente_id: int) -> List[Dict]:
        """
        Las preferencias podrían tener su propia clase, pero por ahora 
        retornar diccionarios está bien para Prolog.
        """
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("SELECT dia_semana, turno FROM preferencias_pacientes WHERE paciente_id = %s", (paciente_id,))
        data = cur.fetchall()
        cur.close(); cn.close()
        return data

    # --- PAPELERA ---
    def obtener_eliminados(self) -> List[Paciente]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("SELECT * FROM pacientes WHERE activo = 0")
        rows = cur.fetchall()
        cur.close(); cn.close()
        return [self._map_row_to_paciente(row) for row in rows]

    def reactivar(self, paciente_id: int):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute("UPDATE pacientes SET activo = 1 WHERE id = %s", (paciente_id,))
        cn.commit()
        cur.close(); cn.close()
        
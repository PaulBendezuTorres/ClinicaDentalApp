from typing import List, Optional
from database.conexion import get_db_connection
from clases.tratamiento import Tratamiento

class TratamientoDAO:
    def _map_row(self, row) -> Tratamiento:
        return Tratamiento(
            id=row['id'],
            nombre=row['nombre'],
            duracion_minutos=row['duracion_minutos'],
            costo=float(row['costo']),
            requiere_equipo_especial=row['requiere_equipo_especial'],
            activo=row['activo']
        )

    def obtener_todos(self) -> List[Tratamiento]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("SELECT * FROM tratamientos WHERE activo = 1 ORDER BY nombre")
        rows = cur.fetchall()
        cur.close(); cn.close()
        return [self._map_row(r) for r in rows]

    def obtener_por_id(self, id: int) -> Optional[Tratamiento]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("SELECT * FROM tratamientos WHERE id=%s", (id,))
        row = cur.fetchone()
        cur.close(); cn.close()
        return self._map_row(row) if row else None

    def crear(self, t: Tratamiento):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute(
            "INSERT INTO tratamientos (nombre, duracion_minutos, costo, requiere_equipo_especial) VALUES (%s, %s, %s, %s)",
            (t.nombre, t.duracion_minutos, t.costo, t.requiere_equipo_especial)
        )
        cn.commit()
        cur.close(); cn.close()

    def actualizar(self, t: Tratamiento):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute(
            "UPDATE tratamientos SET nombre=%s, duracion_minutos=%s, costo=%s, requiere_equipo_especial=%s WHERE id=%s",
            (t.nombre, t.duracion_minutos, t.costo, t.requiere_equipo_especial, t.id)
        )
        cn.commit()
        cur.close(); cn.close()

    def eliminar(self, id: int):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute("UPDATE tratamientos SET activo = 0 WHERE id = %s", (id,))
        cn.commit()
        cur.close(); cn.close()

    # Papelera
    def obtener_eliminados(self) -> List[Tratamiento]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("SELECT * FROM tratamientos WHERE activo = 0")
        rows = cur.fetchall()
        cur.close(); cn.close()
        return [self._map_row(r) for r in rows]

    def reactivar(self, id: int):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute("UPDATE tratamientos SET activo = 1 WHERE id = %s", (id,))
        cn.commit()
        cur.close(); cn.close()
from typing import List, Optional
from database.conexion import get_db_connection
from clases.consultorio import Consultorio

class ConsultorioDAO:
    def _map_row(self, row) -> Consultorio:
        return Consultorio(
            id=row['id'],
            nombre_sala=row['nombre_sala'],
            equipo_especial=row['equipo_especial'],
            activo=row['activo']
        )

    def obtener_todos(self) -> List[Consultorio]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("SELECT * FROM consultorios WHERE activo = 1 ORDER BY id")
        rows = cur.fetchall()
        cur.close(); cn.close()
        return [self._map_row(r) for r in rows]

    def crear(self, c: Consultorio):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute(
            "INSERT INTO consultorios (nombre_sala, equipo_especial) VALUES (%s, %s)",
            (c.nombre_sala, c.equipo_especial)
        )
        cn.commit()
        cur.close(); cn.close()

    def actualizar(self, c: Consultorio):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute(
            "UPDATE consultorios SET nombre_sala=%s, equipo_especial=%s WHERE id=%s",
            (c.nombre_sala, c.equipo_especial, c.id)
        )
        cn.commit()
        cur.close(); cn.close()

    def eliminar(self, id: int):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute("UPDATE consultorios SET activo = 0 WHERE id = %s", (id,))
        cn.commit()
        cur.close(); cn.close()

    # Papelera
    def obtener_eliminados(self) -> List[Consultorio]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("SELECT * FROM consultorios WHERE activo = 0")
        rows = cur.fetchall()
        cur.close(); cn.close()
        return [self._map_row(r) for r in rows]

    def reactivar(self, id: int):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute("UPDATE consultorios SET activo = 1 WHERE id = %s", (id,))
        cn.commit()
        cur.close(); cn.close()
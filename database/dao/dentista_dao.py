from typing import List, Optional
from database.conexion import get_db_connection
from clases.dentista import Dentista

class DentistaDAO:
    def _map_row(self, row) -> Dentista:
        return Dentista(
            id=row['id'],
            nombre=row['nombre'],
            especialidad=row['especialidad'],
            activo=row['activo']
        )

    def obtener_todos(self) -> List[Dentista]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("SELECT * FROM dentistas WHERE activo = 1 ORDER BY nombre")
        rows = cur.fetchall()
        cur.close(); cn.close()
        return [self._map_row(r) for r in rows]

    def obtener_por_id(self, id: int) -> Optional[Dentista]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("SELECT * FROM dentistas WHERE id=%s", (id,))
        row = cur.fetchone()
        cur.close(); cn.close()
        return self._map_row(row) if row else None

    def crear(self, dentista: Dentista):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute(
            "INSERT INTO dentistas (nombre, especialidad) VALUES (%s, %s)",
            (dentista.nombre, dentista.especialidad)
        )
        cn.commit()
        cur.close(); cn.close()

    def actualizar(self, dentista: Dentista):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute(
            "UPDATE dentistas SET nombre=%s, especialidad=%s WHERE id=%s",
            (dentista.nombre, dentista.especialidad, dentista.id)
        )
        cn.commit()
        cur.close(); cn.close()

    def eliminar(self, id: int):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute("UPDATE dentistas SET activo = 0 WHERE id = %s", (id,))
        cn.commit()
        cur.close(); cn.close()

    # Papelera
    def obtener_eliminados(self) -> List[Dentista]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("SELECT * FROM dentistas WHERE activo = 0")
        rows = cur.fetchall()
        cur.close(); cn.close()
        return [self._map_row(r) for r in rows]

    def reactivar(self, id: int):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute("UPDATE dentistas SET activo = 1 WHERE id = %s", (id,))
        cn.commit()
        cur.close(); cn.close()
from typing import List
from database.conexion import get_db_connection
from clases.horario import HorarioDentista

class HorarioDAO:
    def _map_row(self, row) -> HorarioDentista:
        return HorarioDentista(
            id=row['id'],
            dentista_id=row.get('dentista_id', 0),
            dia_semana=row['dia_semana'],
            hora_inicio=row['hora_inicio'],
            hora_fin=row['hora_fin'],
            dentista_nombre=row.get('dentista_nombre', '') 
        )

    def obtener_todos_para_reglas(self) -> List[HorarioDentista]:
        """Obtiene horarios de dentistas activos para Prolog."""
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("""
            SELECT h.*, d.nombre AS dentista_nombre
            FROM horarios_dentistas h
            JOIN dentistas d ON d.id = h.dentista_id
            WHERE d.activo = 1 
            ORDER BY d.nombre
        """)
        rows = cur.fetchall()
        cur.close(); cn.close()
        return [self._map_row(r) for r in rows]

    def obtener_por_dentista(self, dentista_id: int) -> List[HorarioDentista]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("""
            SELECT * FROM horarios_dentistas
            WHERE dentista_id = %s
            ORDER BY FIELD(dia_semana,'lunes','martes','miercoles','jueves','viernes','sabado','domingo'), hora_inicio
        """, (dentista_id,))
        rows = cur.fetchall()
        cur.close(); cn.close()
        return [self._map_row(r) for r in rows]

    def crear(self, h: HorarioDentista):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute("""
            INSERT INTO horarios_dentistas (dentista_id, dia_semana, hora_inicio, hora_fin)
            VALUES (%s, %s, %s, %s)
        """, (h.dentista_id, h.dia_semana, h.hora_inicio, h.hora_fin))
        cn.commit()
        cur.close(); cn.close()

    def eliminar(self, id: int):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute("DELETE FROM horarios_dentistas WHERE id = %s", (id,))
        cn.commit()
        cur.close(); cn.close()
        
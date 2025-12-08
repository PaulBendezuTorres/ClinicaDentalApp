from typing import List, Dict
from database.conexion import get_db_connection
from clases.cita import Cita

class CitaDAO:
    def _map_row(self, row) -> Cita:
        # Mapeo flexible: algunos campos pueden no venir en todas las consultas
        return Cita(
            id=row.get('id'),
            paciente_id=row.get('paciente_id'),
            dentista_id=row.get('dentista_id'),
            consultorio_id=row.get('consultorio_id'),
            tratamiento_id=row.get('tratamiento_id'),
            fecha=str(row.get('fecha', '')),
            hora_inicio=str(row.get('hora_inicio', '')),
            estado=row.get('estado', 'Pendiente'),
            paciente_nombre=row.get('paciente_nombre', row.get('paciente', '')),
            dentista_nombre=row.get('dentista_nombre', row.get('dentista', '')),
            tratamiento_nombre=row.get('tratamiento_nombre', row.get('tratamiento', '')),
            consultorio_nombre=row.get('consultorio_nombre', row.get('consultorio', '')),
            duracion_minutos=row.get('duracion_minutos', 0),
            requiere_equipo_especial=row.get('requiere_equipo_especial', 0),
            costo=float(row.get('costo', 0.0))
        )

    def obtener_por_fecha(self, fecha: str) -> List[Cita]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                c.*, 
                p.nombre AS paciente_nombre,
                d.nombre AS dentista_nombre,
                s.nombre_sala AS consultorio_nombre,
                t.nombre AS tratamiento_nombre,
                t.duracion_minutos, t.requiere_equipo_especial
            FROM citas c
            JOIN pacientes p ON p.id = c.paciente_id
            JOIN dentistas d ON d.id = c.dentista_id
            JOIN consultorios s ON s.id = c.consultorio_id
            JOIN tratamientos t ON t.id = c.tratamiento_id
            WHERE c.fecha = %s
            ORDER BY c.hora_inicio
        """, (fecha,))
        rows = cur.fetchall()
        cur.close(); cn.close()
        return [self._map_row(r) for r in rows]

    def crear(self, c: Cita) -> int:
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute("""
            INSERT INTO citas(paciente_id, dentista_id, consultorio_id, 
                              tratamiento_id, fecha, hora_inicio, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (c.paciente_id, c.dentista_id, c.consultorio_id, c.tratamiento_id, c.fecha, c.hora_inicio, c.estado))
        new_id = cur.lastrowid
        cn.commit()
        cur.close(); cn.close()
        return new_id

    def obtener_todas_dashboard(self, filtro_fecha: str = None, busqueda: str = "") -> List[Cita]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
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
        if filtro_fecha == 'hoy': sql += " AND c.fecha = CURDATE()"
        elif filtro_fecha == 'futuras': sql += " AND c.fecha >= CURDATE()"
        if busqueda:
            sql += " AND p.nombre LIKE %s"
            params.append(f"%{busqueda}%")
        
        sql += " ORDER BY c.fecha, c.hora_inicio"
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        cur.close(); cn.close()
        return [self._map_row(r) for r in rows]

    def actualizar_estado(self, id: int, estado: str):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute("UPDATE citas SET estado = %s WHERE id = %s", (estado, id))
        cn.commit()
        cur.close(); cn.close()

    def obtener_historial_paciente(self, paciente_id: int) -> List[Cita]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("""
            SELECT 
                c.id, c.fecha, c.hora_inicio, c.estado,
                d.nombre AS dentista_nombre, 
                t.nombre AS tratamiento_nombre, t.costo
            FROM citas c
            JOIN dentistas d ON d.id = c.dentista_id
            JOIN tratamientos t ON t.id = c.tratamiento_id
            WHERE c.paciente_id = %s
            ORDER BY c.fecha DESC, c.hora_inicio DESC
        """, (paciente_id,))
        rows = cur.fetchall()
        cur.close(); cn.close()
        return [self._map_row(r) for r in rows]
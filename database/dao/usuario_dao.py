from typing import List, Optional
from database.conexion import get_db_connection
from clases.usuario import Usuario

class UsuarioDAO:
    def _map_row(self, row) -> Usuario:
        return Usuario(
            id=row['id'],
            nombre_usuario=row['nombre_usuario'],
            contrasena_hash=row['contrasena_hash'],
            rol=row['rol'],
            activo=row['activo']
        )

    def obtener_por_nombre(self, nombre: str) -> Optional[Usuario]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s AND activo = 1", (nombre,))
        row = cur.fetchone()
        cur.close(); cn.close()
        return self._map_row(row) if row else None

    def obtener_todos(self) -> List[Usuario]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE activo = 1 ORDER BY nombre_usuario")
        rows = cur.fetchall()
        cur.close(); cn.close()
        return [self._map_row(r) for r in rows]

    def crear(self, u: Usuario):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute(
            "INSERT INTO usuarios (nombre_usuario, contrasena_hash, rol) VALUES (%s, %s, %s)",
            (u.nombre_usuario, u.contrasena_hash, u.rol)
        )
        cn.commit()
        cur.close(); cn.close()

    def actualizar(self, u: Usuario, actualizar_password=False):
        cn = get_db_connection()
        cur = cn.cursor()
        if actualizar_password:
            cur.execute(
                "UPDATE usuarios SET nombre_usuario=%s, rol=%s, contrasena_hash=%s WHERE id=%s",
                (u.nombre_usuario, u.rol, u.contrasena_hash, u.id)
            )
        else:
            cur.execute(
                "UPDATE usuarios SET nombre_usuario=%s, rol=%s WHERE id=%s",
                (u.nombre_usuario, u.rol, u.id)
            )
        cn.commit()
        cur.close(); cn.close()

    def eliminar(self, id: int):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute("UPDATE usuarios SET activo = 0 WHERE id = %s", (id,))
        cn.commit()
        cur.close(); cn.close()

    # Papelera
    def obtener_eliminados(self) -> List[Usuario]:
        cn = get_db_connection()
        cur = cn.cursor(dictionary=True)
        cur.execute("SELECT * FROM usuarios WHERE activo = 0")
        rows = cur.fetchall()
        cur.close(); cn.close()
        return [self._map_row(r) for r in rows]

    def reactivar(self, id: int):
        cn = get_db_connection()
        cur = cn.cursor()
        cur.execute("UPDATE usuarios SET activo = 1 WHERE id = %s", (id,))
        cn.commit()
        cur.close(); cn.close()
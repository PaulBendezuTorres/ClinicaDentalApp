from typing import List, Dict, Optional
from dataclasses import asdict
import bcrypt
from database.dao.usuario_dao import UsuarioDAO
from clases.usuario import Usuario

class UsuarioService:
    def __init__(self):
        self.dao = UsuarioDAO()

    def verificar_credenciales(self, nombre: str, pass_plana: str) -> Optional[Dict]:
        usuario = self.dao.obtener_por_nombre(nombre)
        if not usuario:
            return None
        
        # Verificar hash
        hash_db = usuario.contrasena_hash.encode('utf-8')
        if bcrypt.checkpw(pass_plana.encode('utf-8'), hash_db):
            return asdict(usuario)
        return None

    def obtener_todos(self) -> List[Dict]:
        return [asdict(u) for u in self.dao.obtener_todos()]

    def crear(self, nombre: str, pass_plana: str, rol: str):
        # Hashear password
        salt = bcrypt.gensalt()
        hash_pw = bcrypt.hashpw(pass_plana.encode('utf-8'), salt).decode('utf-8')
        
        nuevo = Usuario(nombre_usuario=nombre, contrasena_hash=hash_pw, rol=rol)
        self.dao.crear(nuevo)

    def actualizar(self, id: int, nombre: str, rol: str, pass_plana: str = None):
        usuario = Usuario(id=id, nombre_usuario=nombre, rol=rol)
        
        if pass_plana:
            salt = bcrypt.gensalt()
            usuario.contrasena_hash = bcrypt.hashpw(pass_plana.encode('utf-8'), salt).decode('utf-8')
            self.dao.actualizar(usuario, actualizar_password=True)
        else:
            self.dao.actualizar(usuario, actualizar_password=False)

    def eliminar(self, id: int):
        self.dao.eliminar(id)

    # Papelera
    def obtener_eliminados(self) -> List[Dict]:
        return [asdict(u) for u in self.dao.obtener_eliminados()]

    def restaurar(self, id: int):
        self.dao.reactivar(id)
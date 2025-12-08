from dataclasses import dataclass

@dataclass
class Usuario:
    id: int = None
    nombre_usuario: str = ""
    contrasena_hash: str = ""
    rol: str = ""
    activo: int = 1
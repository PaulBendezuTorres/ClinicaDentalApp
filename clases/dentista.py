from dataclasses import dataclass

@dataclass
class Dentista:
    id: int = None
    nombre: str = ""
    especialidad: str = ""
    activo: int = 1
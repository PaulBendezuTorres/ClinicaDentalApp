from dataclasses import dataclass

@dataclass
class Consultorio:
    id: int = None
    nombre_sala: str = ""
    equipo_especial: int = 0
    activo: int = 1
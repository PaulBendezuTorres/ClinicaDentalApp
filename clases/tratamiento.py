from dataclasses import dataclass

@dataclass
class Tratamiento:
    id: int = None
    nombre: str = ""
    duracion_minutos: int = 0
    costo: float = 0.0
    requiere_equipo_especial: int = 0
    activo: int = 1
from dataclasses import dataclass

@dataclass
class Cita:
    id: int = None
    paciente_id: int = 0
    dentista_id: int = 0
    consultorio_id: int = 0
    tratamiento_id: int = 0
    fecha: str = "" # YYYY-MM-DD
    hora_inicio: str = "" # HH:MM:SS
    estado: str = "Pendiente"
    
    # Campos extendidos para visualización (Joins)
    paciente_nombre: str = ""
    dentista_nombre: str = ""
    tratamiento_nombre: str = ""
    consultorio_nombre: str = ""
    duracion_minutos: int = 0
    requiere_equipo_especial: int = 0
    costo: float = 0.0
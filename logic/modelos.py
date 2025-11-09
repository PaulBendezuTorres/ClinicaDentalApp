from dataclasses import dataclass

@dataclass
class Paciente:
    id: int
    nombre: str
    telefono: str

@dataclass
class Dentista:
    id: int
    nombre: str
    especialidad: str

@dataclass
class Cita:
    id: int
    paciente_id: int
    dentista_id: int
    consultorio_id: int
    tratamiento_id: int
    fecha: str         # 'YYYY-MM-DD'
    hora_inicio: str   # 'HH:MM'

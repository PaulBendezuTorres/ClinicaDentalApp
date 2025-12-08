from dataclasses import dataclass
from typing import Optional

@dataclass
class Paciente:
    id: int
    nombre: str
    telefono: str
    dni: str
    direccion: str
    correo: str
    genero: str  # 'Masculino', 'Femenino', 'Otro'
    activo: bool = True

@dataclass
class Dentista:
    id: int
    nombre: str
    especialidad: str
    activo: bool = True

@dataclass
class Tratamiento:
    id: int
    nombre: str
    duracion_minutos: int
    costo: float
    requiere_equipo_especial: bool
    activo: bool = True

@dataclass
class Consultorio:
    id: int
    nombre_sala: str
    equipo_especial: bool
    activo: bool = True

@dataclass
class Cita:
    id: int
    paciente_id: int
    dentista_id: int
    consultorio_id: int
    tratamiento_id: int
    fecha: str         # 'YYYY-MM-DD'
    hora_inicio: str   # 'HH:MM'
    estado: str = "Pendiente" # 'Pendiente', 'Confirmada', 'Realizada', 'Cancelada'

@dataclass
class Usuario:
    id: int
    nombre_usuario: str
    contrasena_hash: str
    rol: str # 'admin', 'recepcionista'
    activo: bool = True

@dataclass
class HorarioDentista:
    id: int
    dentista_id: int
    dia_semana: str
    hora_inicio: str
    hora_fin: str
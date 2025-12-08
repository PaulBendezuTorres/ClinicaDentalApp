# clases/paciente.py
from dataclasses import dataclass

@dataclass
class Paciente:
    id: int = None
    nombre: str = ""
    telefono: str = ""
    dni: str = ""
    direccion: str = ""
    correo: str = ""
    genero: str = ""  # 'Masculino', 'Femenino', 'Otro'
    activo: int = 1

    @property
    def info_completa(self):
        """Propiedad para mostrar información formateada (útil para UIs)"""
        return f"{self.nombre} (DNI: {self.dni})"
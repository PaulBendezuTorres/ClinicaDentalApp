from dataclasses import dataclass

@dataclass
class HorarioDentista:
    id: int = None
    dentista_id: int = 0
    dia_semana: str = ""
    hora_inicio: str = "" # O datetime.time
    hora_fin: str = ""    # O datetime.time
    
    # Campo extra para facilitar lectura en vistas (no está en tabla horario)
    dentista_nombre: str = ""
from typing import List, Dict
from dataclasses import asdict
from database.dao.tratamiento_dao import TratamientoDAO
from clases.tratamiento import Tratamiento

class TratamientoService:
    def __init__(self):
        self.dao = TratamientoDAO()

    def obtener_todos(self) -> List[Dict]:
        return [asdict(t) for t in self.dao.obtener_todos()]

    def crear(self, nombre: str, duracion: int, costo: float, equipo: int):
        nuevo = Tratamiento(
            nombre=nombre, 
            duracion_minutos=duracion, 
            costo=costo, 
            requiere_equipo_especial=equipo
        )
        self.dao.crear(nuevo)

    def actualizar(self, id: int, nombre: str, duracion: int, costo: float, equipo: int):
        obj = Tratamiento(
            id=id,
            nombre=nombre, 
            duracion_minutos=duracion, 
            costo=costo, 
            requiere_equipo_especial=equipo
        )
        self.dao.actualizar(obj)

    def eliminar(self, id: int):
        self.dao.eliminar(id)

    # Papelera
    def obtener_eliminados(self) -> List[Dict]:
        return [asdict(t) for t in self.dao.obtener_eliminados()]

    def restaurar(self, id: int):
        self.dao.reactivar(id)
    
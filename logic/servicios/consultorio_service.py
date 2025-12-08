from typing import List, Dict
from dataclasses import asdict
from database.dao.consultorio_dao import ConsultorioDAO
from clases.consultorio import Consultorio

class ConsultorioService:
    def __init__(self):
        self.dao = ConsultorioDAO()

    def obtener_todos(self) -> List[Dict]:
        return [asdict(c) for c in self.dao.obtener_todos()]

    def crear(self, nombre: str, equipo: int):
        nuevo = Consultorio(nombre_sala=nombre, equipo_especial=equipo)
        self.dao.crear(nuevo)

    def actualizar(self, id: int, nombre: str, equipo: int):
        obj = Consultorio(id=id, nombre_sala=nombre, equipo_especial=equipo)
        self.dao.actualizar(obj)

    def eliminar(self, id: int):
        self.dao.eliminar(id)

    # Papelera
    def obtener_eliminados(self) -> List[Dict]:
        return [asdict(c) for c in self.dao.obtener_eliminados()]

    def restaurar(self, id: int):
        self.dao.reactivar(id)
        
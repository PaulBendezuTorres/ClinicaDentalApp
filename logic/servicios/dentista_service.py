from typing import List, Dict
from dataclasses import asdict
from database.dao.dentista_dao import DentistaDAO
from clases.dentista import Dentista

class DentistaService:
    def __init__(self):
        self.dao = DentistaDAO()

    def obtener_todos(self) -> List[Dict]:
        return [asdict(d) for d in self.dao.obtener_todos()]

    def crear(self, nombre: str, especialidad: str):
        nuevo = Dentista(nombre=nombre, especialidad=especialidad)
        self.dao.crear(nuevo)

    def actualizar(self, id: int, nombre: str, especialidad: str):
        obj = Dentista(id=id, nombre=nombre, especialidad=especialidad)
        self.dao.actualizar(obj)

    def eliminar(self, id: int):
        self.dao.eliminar(id)

    # Papelera
    def obtener_eliminados(self) -> List[Dict]:
        return [asdict(d) for d in self.dao.obtener_eliminados()]

    def restaurar(self, id: int):
        self.dao.reactivar(id)
from typing import List, Dict
from dataclasses import asdict
from database.dao.horario_dao import HorarioDAO
from clases.horario import HorarioDentista

class HorarioService:
    def __init__(self):
        self.dao = HorarioDAO()

    def obtener_por_dentista(self, dentista_id: int) -> List[Dict]:
        return [asdict(h) for h in self.dao.obtener_por_dentista(dentista_id)]

    def crear(self, dentista_id: int, dia: str, inicio: str, fin: str):
        nuevo = HorarioDentista(
            dentista_id=dentista_id,
            dia_semana=dia,
            hora_inicio=inicio,
            hora_fin=fin
        )
        self.dao.crear(nuevo)

    def eliminar(self, id: int):
        self.dao.eliminar(id)
        
    def obtener_todos_reglas(self) -> List[Dict]:
        # Para el motor de prolog
        return [asdict(h) for h in self.dao.obtener_todos_para_reglas()]
    
# logic/servicios/paciente_service.py
from typing import List, Dict
from dataclasses import asdict
from clases.paciente import Paciente
from database.dao.paciente_dao import PacienteDAO

class PacienteService:
    def __init__(self):
        self.dao = PacienteDAO()

    def obtener_todos(self, filtro: str = "") -> List[Dict]:
        """
        Obtiene los pacientes y los convierte a diccionarios para que 
        la vista (Tkinter) los pueda leer fácilmente sin cambios drásticos.
        """
        pacientes_obj = self.dao.obtener_todos(filtro)
        # Convertimos la lista de Objetos a lista de Diccionarios
        return [asdict(p) for p in pacientes_obj]

    def crear(self, nombre: str, telefono: str, dni: str, direccion: str, correo: str, genero: str) -> int:
        # Aquí creamos la instancia del objeto
        nuevo_paciente = Paciente(
            nombre=nombre,
            telefono=telefono,
            dni=dni,
            direccion=direccion,
            correo=correo,
            genero=genero
        )
        return self.dao.crear(nuevo_paciente)

    def actualizar(self, id: int, nombre: str, telefono: str, dni: str, direccion: str, correo: str, genero: str):
        paciente = Paciente(
            id=id,
            nombre=nombre,
            telefono=telefono,
            dni=dni,
            direccion=direccion,
            correo=correo,
            genero=genero
        )
        self.dao.actualizar(paciente)

    def eliminar(self, id: int):
        self.dao.eliminar(id)

    def obtener_preferencias(self, id: int) -> List[Dict]:
        return self.dao.obtener_preferencias(id)

    # --- Papelera ---
    def obtener_eliminados(self) -> List[Dict]:
        pacientes_obj = self.dao.obtener_eliminados()
        return [asdict(p) for p in pacientes_obj]

    def restaurar(self, id: int):
        self.dao.reactivar(id)
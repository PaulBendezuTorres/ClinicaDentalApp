from logic.servicios.usuario_service import UsuarioService
from logic.servicios.paciente_service import PacienteService
from logic.servicios.dentista_service import DentistaService
from logic.servicios.tratamiento_service import TratamientoService
from logic.servicios.consultorio_service import ConsultorioService
from logic.servicios.horario_service import HorarioService
from logic.servicios.cita_service import CitaService

class SistemaDental:
    def __init__(self):
        # Inicializamos todos los servicios
        self.usuario = UsuarioService()
        self.paciente = PacienteService()
        self.dentista = DentistaService()
        self.tratamiento = TratamientoService()
        self.consultorio = ConsultorioService()
        self.horario = HorarioService()
        self.cita = CitaService()

# Instancia única (Singleton)
sistema = SistemaDental()
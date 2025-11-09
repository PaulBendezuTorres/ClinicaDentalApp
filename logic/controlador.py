from datetime import datetime, timedelta
from typing import List, Dict
from pyswip import Prolog
import os
from database.queries import paciente as paciente_queries
from database.queries import dentista as dentista_queries
from database.queries import tratamiento as tratamiento_queries
from database.queries import cita as cita_queries
from database.queries import horario as horario_queries
from database.queries import consultorio as consultorio_queries

from logic import procesador

def obtener_historial_paciente(paciente_id: int) -> List[Dict]:
    return cita_queries.obtener_citas_por_paciente(paciente_id)

def _dia_semana_es(d: datetime) -> str:
    dias = ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]
    return dias[d.weekday()]

def _generar_slots(inicio: str, fin: str, paso_min=30) -> List[str]:
    h0 = datetime.strptime(inicio, "%H:%M")
    h1 = datetime.strptime(fin, "%H:%M")
    t = h0
    slots = []
    while t <= h1:
        slots.append(t.strftime("%H:%M"))
        t += timedelta(minutes=paso_min)
    return slots

def _ExisteEquipoEspecial() -> bool:
    # Cambiamos la llamada
    consultorios = consultorio_queries.obtener_consultorios()
    return any(int(c["equipo_especial"]) == 1 for c in consultorios)

def obtener_lista_pacientes() -> List[Dict]:
    # Cambiamos la llamada
    return paciente_queries.obtener_pacientes()

def crear_paciente(nombre: str, telefono: str, dni: str, direccion: str, correo: str, genero: str) -> int:
    return paciente_queries.crear_paciente(nombre, telefono, dni, direccion, correo, genero)

def actualizar_paciente(id: int, nombre: str, telefono: str, dni: str, direccion: str, correo: str, genero: str):
    return paciente_queries.actualizar_paciente(id, nombre, telefono, dni, direccion, correo, genero)

def obtener_lista_dentistas() -> List[Dict]:
    # Cambiamos la llamada
    return dentista_queries.obtener_dentistas()

def obtener_lista_tratamientos() -> List[Dict]:
    # Cambiamos la llamada
    return tratamiento_queries.obtener_tratamientos()

def obtener_lista_consultorios() -> List[Dict]:
    # ¡Añadimos esta nueva función para que la vista no llame a la DB directamente!
    return consultorio_queries.obtener_consultorios()

def buscar_horarios_disponibles(fecha: str, dentista_id: int, tratamiento_id: int, paciente_id: int) -> List[str]: # <-- 1. Añadimos paciente_id
    # ... (obtener citas, horarios, dentista, tratamiento no cambia) ...
    citas = cita_queries.obtener_citas_por_fecha(fecha)
    horarios = horario_queries.obtener_reglas_horarios_dentistas()
    dentista = dentista_queries.obtener_dentista_por_id(dentista_id)
    tratamiento = tratamiento_queries.obtener_tratamiento_por_id(tratamiento_id)
    
    # --- INICIO DE LA NUEVA LÓGICA ---
    # 2. Obtenemos las preferencias del paciente
    preferencias = paciente_queries.obtener_preferencias_paciente(paciente_id)
    # --- FIN DE LA NUEVA LÓGICA ---

    if not dentista or not tratamiento:
        return []

    # ... (generar hechos de citas, horarios y tratamiento no cambia) ...
    hechos_citas = procesador.generar_hechos_prolog_citas(citas)
    hechos_horarios = procesador.generar_hechos_prolog_horarios(
        [h for h in horarios if int(h["dentista_id"]) == dentista_id]
    )
    hechos_trat = procesador.generar_hechos_prolog_tratamiento_unico(tratamiento)

    prolog = Prolog()
    reglas_path = os.path.join(os.path.dirname(__file__), "..", "prolog", "motor_reglas.pl")
    prolog.consult(os.path.normpath(reglas_path))

    for linea in (hechos_citas + "\n" + hechos_horarios + "\n" + hechos_trat).splitlines():
        if linea.strip():
            prolog.assertz(linea.strip()[:-1])
            
    # --- INICIO DE LA NUEVA LÓGICA ---
    # 3. "Enseñamos" a Prolog las preferencias del paciente
    for pref in preferencias:
        dia = pref['dia_semana']
        turno = pref['turno']
        # Creamos un hecho dinámico como: paciente_no_disponible('lunes', 'mañana').
        prolog.assertz(f"paciente_no_disponible('{dia}', '{turno}')")

def confirmar_cita(datos_cita: Dict) -> int:
    return cita_queries.guardar_nueva_cita(
        datos_cita["paciente_id"],
        datos_cita["dentista_id"],
        datos_cita["consultorio_id"],
        datos_cita["tratamiento_id"],
        datos_cita["fecha"],
        datos_cita["hora_inicio"]
    )

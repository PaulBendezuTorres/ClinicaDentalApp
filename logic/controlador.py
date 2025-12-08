
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
from pyswip import Prolog
import bcrypt
import os

from database.queries import paciente as paciente_queries
from database.queries import dentista as dentista_queries
from database.queries import tratamiento as tratamiento_queries
from database.queries import cita as cita_queries
from database.queries import horario as horario_queries
from database.queries import consultorio as consultorio_queries
from database.queries import usuario as usuario_queries
from logic import procesador



_prolog_engine = None 

def _inicializar_prolog():
    """Crea la instancia del motor Prolog si aún no existe."""
    global _prolog_engine
    if _prolog_engine is None:
        _prolog_engine = Prolog()
        reglas_path = os.path.join(os.path.dirname(__file__), "..", "prolog", "motor_reglas.pl")
        _prolog_engine.consult(os.path.normpath(reglas_path))

def _limpiar_hechos_dinamicos(prolog: Prolog):
    """Elimina todos los hechos temporales de la base de conocimiento de Prolog."""
    prolog.retractall("cita_ocupada(_,_,_)")
    prolog.retractall("paciente_no_disponible(_,_)")
    prolog.retractall("filtro_turno(_)")
    prolog.retractall("filtro_dia(_)")
    prolog.retractall("equipo_especial_disponible(_,_)")
    # Limpiamos también horarios y tratamientos para asegurar un estado limpio
    prolog.retractall("horario_laboral(_,_,_,_)")
    prolog.retractall("duracion_tratamiento(_,_)")
    prolog.retractall("requiere_equipo(_,_)")

def _dia_semana_es(d: datetime) -> str:
    dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    return dias[d.weekday()]

def _generar_slots(inicio: str, fin: str, paso_min=30) -> List[str]:
    h0 = datetime.strptime(inicio, "%H:%M")
    h1 = datetime.strptime(fin, "%H:%M")
    t = h0
    slots = []
    while t < h1:
        slots.append(t.strftime("%H:%M"))
        t += timedelta(minutes=paso_min)
    return slots

def _ExisteEquipoEspecial() -> bool:
    consultorios = consultorio_queries.obtener_consultorios()
    return any(int(c["equipo_especial"]) == 1 for c in consultorios)

def obtener_lista_pacientes() -> List[Dict]:
    return paciente_queries.obtener_pacientes()

def crear_paciente(nombre: str, telefono: str, dni: str, direccion: str, correo: str, genero: str) -> int:
    return paciente_queries.crear_paciente(nombre, telefono, dni, direccion, correo, genero)

def actualizar_paciente(id: int, nombre: str, telefono: str, dni: str, direccion: str, correo: str, genero: str):
    return paciente_queries.actualizar_paciente(id, nombre, telefono, dni, direccion, correo, genero)

def obtener_historial_paciente(paciente_id: int) -> List[Dict]:
    return cita_queries.obtener_citas_por_paciente(paciente_id)

def obtener_lista_dentistas() -> List[Dict]:
    return dentista_queries.obtener_dentistas()

def obtener_lista_tratamientos() -> List[Dict]:
    return tratamiento_queries.obtener_tratamientos()

def obtener_lista_consultorios() -> List[Dict]:
    return consultorio_queries.obtener_consultorios()

def obtener_lista_pacientes(filtro: str = "") -> List[Dict]:
    return paciente_queries.obtener_pacientes(filtro)

def eliminar_paciente(paciente_id: int):
    return paciente_queries.desactivar_paciente(paciente_id)

def obtener_lista_usuarios() -> List[Dict]:
    return usuario_queries.obtener_todos_usuarios()

def registrar_dentista(nombre: str, especialidad: str):
    dentista_queries.crear_dentista_db(nombre, especialidad)

def modificar_dentista(dentista_id: int, nombre: str, especialidad: str):
    dentista_queries.actualizar_dentista_db(dentista_id, nombre, especialidad)

def borrar_dentista(dentista_id: int):
    dentista_queries.eliminar_dentista_db(dentista_id)

def registrar_usuario(nombre: str, contrasena: str, rol: str):
    # Hasheamos la contraseña antes de enviarla a la BD
    salt = bcrypt.gensalt()
    hash_pw = bcrypt.hashpw(contrasena.encode('utf-8'), salt).decode('utf-8')
    usuario_queries.crear_usuario_db(nombre, hash_pw, rol)

def modificar_usuario(user_id: int, nombre: str, rol: str, nueva_contrasena: str = None):
    hash_pw = None
    if nueva_contrasena:
        salt = bcrypt.gensalt()
        hash_pw = bcrypt.hashpw(nueva_contrasena.encode('utf-8'), salt).decode('utf-8')
    
    usuario_queries.actualizar_usuario_db(user_id, nombre, rol, hash_pw)

def borrar_usuario(user_id: int):
    usuario_queries.eliminar_usuario_db(user_id)

def buscar_horarios_disponibles(fecha: str, dentista_id: int, tratamiento_id: int, paciente_id: int, 
                              filtro_turno: str = None, filtro_dias: list = None) -> List[Dict]:
    _inicializar_prolog()
    prolog = _prolog_engine
    _limpiar_hechos_dinamicos(prolog)

    citas = cita_queries.obtener_citas_por_fecha(fecha)
    horarios = horario_queries.obtener_reglas_horarios_dentistas()
    dentista = dentista_queries.obtener_dentista_por_id(dentista_id)
    tratamiento = tratamiento_queries.obtener_tratamiento_por_id(tratamiento_id)
    
    # --- LÍNEA CORREGIDA ---
    preferencias = paciente_queries.obtener_preferencias_paciente(paciente_id)

    if not dentista or not tratamiento:
        return []

    hechos_citas = procesador.generar_hechos_prolog_citas(citas)
    hechos_horarios = procesador.generar_hechos_prolog_horarios(
        [h for h in horarios if int(h["dentista_id"]) == dentista_id]
    )
    hechos_trat = procesador.generar_hechos_prolog_tratamiento_unico(tratamiento)

    for linea in (hechos_citas + "\n" + hechos_horarios + "\n" + hechos_trat).splitlines():
        if linea.strip():
            prolog.assertz(linea.strip()[:-1])
            
    for pref in preferencias:
        prolog.assertz(f"paciente_no_disponible('{pref['dia_semana']}', '{pref['turno']}')")

    if filtro_turno:
        prolog.assertz(f"filtro_turno('{filtro_turno.lower()}')")

    if filtro_dias:
        for dia in filtro_dias:
            prolog.assertz(f"filtro_dia('{dia}')")

    fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
    dia_semana = _dia_semana_es(fecha_dt)

    dname = dentista["nombre"].replace("'", "\\'")
    rangos = list(prolog.query(f"horario_laboral('{dname}','{dia_semana}', Ini, Fin)"))
    if not rangos:
        return []

    slots_candidatos = []
    for r in rangos:
        slots_candidatos += _generar_slots(r["Ini"], r["Fin"])

    if _ExisteEquipoEspecial():
        consultorios_especiales = [c["id"] for c in consultorio_queries.obtener_consultorios() if c["equipo_especial"] == 1]
        citas_dia = cita_queries.obtener_citas_por_fecha(fecha)
        for hhmm in slots_candidatos:
            citas_en_hora_especial = [c for c in citas_dia if str(c['hora_inicio'])[:5] == hhmm and c['consultorio_id'] in consultorios_especiales]
            if len(citas_en_hora_especial) < len(consultorios_especiales):
                 prolog.assertz(f"equipo_especial_disponible('{fecha}','{hhmm}')")

    tname = tratamiento["nombre"].replace("'", "\\'")
    resultados_horas = []
    for hhmm in slots_candidatos:
        if list(prolog.query(f"encontrar_hora_valida('{dname}','{tname}','{fecha}','{dia_semana}','{hhmm}')")):
            resultados_horas.append(hhmm)

    resultados_horas = sorted(list(dict.fromkeys(resultados_horas)))

    resultados_finales = []
    for hora in resultados_horas:
        resultados_finales.append({
            "fecha": fecha,
            "hora": hora,
            "dia_semana": dia_semana
        })
    return resultados_finales

def encontrar_proxima_cita(dentista_id: int, tratamiento_id: int, paciente_id: int, 
                           filtro_turno: str, filtro_dias: list) -> List[Dict]:
    fecha_inicio = date.today() + timedelta(days=1)
    limite_busqueda = fecha_inicio + timedelta(days=90)
    fecha_actual = fecha_inicio

    while fecha_actual <= limite_busqueda:
        dia_semana_actual = _dia_semana_es(fecha_actual)
        if dia_semana_actual in filtro_dias:
            fecha_str = fecha_actual.strftime('%Y-%m-%d')
            horarios_disponibles = buscar_horarios_disponibles(
                fecha_str, dentista_id, tratamiento_id, paciente_id,
                filtro_turno, [dia_semana_actual] 
            )

            if horarios_disponibles:
                return horarios_disponibles

        fecha_actual += timedelta(days=1)
    return []

def confirmar_cita(datos_cita: Dict) -> int:
    return cita_queries.guardar_nueva_cita(
        datos_cita["paciente_id"],
        datos_cita["dentista_id"],
        datos_cita["consultorio_id"],
        datos_cita["tratamiento_id"],
        datos_cita["fecha"],
        datos_cita["hora_inicio"]
    )
def cerrar_prolog():
    """Cierra la instancia del motor Prolog si fue creada."""
    global _prolog_engine
    if _prolog_engine is not None:
        try:
            # La forma más directa de pedirle a Prolog que termine es con 'halt.'
            list(_prolog_engine.query("halt."))
            print("Motor Prolog cerrado correctamente.")
        except Exception as e:
            print(f"Error al intentar cerrar el motor Prolog: {e}")
def verificar_credenciales(nombre_usuario: str, contrasena_plana: str) -> Optional[Dict]:

    usuario_db = usuario_queries.obtener_usuario_por_nombre(nombre_usuario)
    
    if not usuario_db:
        return None 

    contrasena_hash_db = usuario_db['contrasena_hash'].encode('utf-8')

    if bcrypt.checkpw(contrasena_plana.encode('utf-8'), contrasena_hash_db):
        return usuario_db 
    else:
        return None 

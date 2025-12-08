from typing import List, Dict, Callable
from datetime import timedelta

# --- PARADIGMA FUNCIONAL: FUNCIONES PURAS Y AUXILIARES ---

# Función pura: Escapa caracteres especiales para Prolog (sin efectos secundarios)
def _esc(s: str) -> str:
    return s.replace("'", "\\'")

# Función pura: Formatea objetos de tiempo (timedelta o time) a string 'HH:MM'
def _format_time(time_obj) -> str:
    if hasattr(time_obj, 'strftime'):
        return time_obj.strftime("%H:%M")
    if isinstance(time_obj, timedelta):
        total_seconds = int(time_obj.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02}:{minutes:02}"
    return str(time_obj)[:5]

# Lambda: Formatea fechas a string
format_date: Callable[[any], str] = lambda d: str(d)

# Lambda: Lógica para determinar si requiere equipo ('si'/'no')
req_logic: Callable[[int], str] = lambda r: "si" if r == 1 else "no"


# --- FUNCIONES DE TRANSFORMACIÓN DE DATOS (MAPPING) ---

def generar_hechos_prolog_citas(lista_citas_db: List[Dict]) -> str:
    """
    Transforma una lista de diccionarios de citas en hechos Prolog
    utilizando programación funcional (map y set comprehension).
    """
    # 1. Map: Transforma cada cita en un hecho 'cita_ocupada'
    # Retorna un iterador, es evaluación perezosa (lazy evaluation)
    citas_facts = map(
        lambda c: f"cita_ocupada('{_esc(c['dentista_nombre'])}','{format_date(c['fecha'])}','{_format_time(c['hora_inicio'])}').", 
        lista_citas_db
    )
    
    # 2. Set Comprehension: Extrae duraciones únicas de tratamientos para evitar duplicados
    # Esto reemplaza bucles for anidados y verificaciones de existencia
    duracion_facts = {
        f"duracion_tratamiento('{_esc(c['tratamiento_nombre'])}',{int(c['duracion_minutos'])})." 
        for c in lista_citas_db
    }
    
    # 3. Set Comprehension: Extrae requisitos de equipo únicos
    req_facts = {
        f"requiere_equipo('{_esc(c['tratamiento_nombre'])}','{req_logic(c['requiere_equipo_especial'])}')." 
        for c in lista_citas_db
    }

    # Reduce/Join: Une todos los iterables en un solo string
    return "\n".join(list(citas_facts) + list(duracion_facts) + list(req_facts))


def generar_hechos_prolog_horarios(lista_horarios_db: List[Dict]) -> str:
    """
    Usa map para transformar la lista de horarios en hechos Prolog.
    """
    # Lambda que define la estructura del hecho horario_laboral
    horario_to_fact = lambda h: (
        f"horario_laboral('{_esc(h['dentista_nombre'])}',"
        f"'{h['dia_semana']}',"
        f"'{_format_time(h['hora_inicio'])}',"
        f"'{_format_time(h['hora_fin'])}')."
    )
    
    # Aplicación del map y unión
    return "\n".join(map(horario_to_fact, lista_horarios_db))


def generar_hechos_prolog_tratamiento_unico(tratamiento: Dict) -> str:
    """
    Procesa un único tratamiento (caso simple).
    """
    tname = _esc(tratamiento["nombre"])
    dur = int(tratamiento["duracion_minutos"])
    req = req_logic(tratamiento["requiere_equipo_especial"])
    
    return f"duracion_tratamiento('{tname}',{dur}).\nrequiere_equipo('{tname}','{req}')."
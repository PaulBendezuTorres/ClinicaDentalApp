from typing import List, Dict, Callable
from datetime import timedelta, datetime

# --- FUNCIONES PURAS Y AUXILIARES ---

def _esc(s: str) -> str:
    return s.replace("'", "\\'")

def _format_time(time_obj) -> str:
    """Formatea objetos de tiempo a HH:MM de forma robusta."""
    if time_obj is None: return "00:00"
    
    if isinstance(time_obj, str):
        try:
            if len(time_obj) > 5:
                t = datetime.strptime(time_obj, "%H:%M:%S")
            else:
                t = datetime.strptime(time_obj, "%H:%M")
            return t.strftime("%H:%M")
        except ValueError:
            return time_obj[:5]

    if hasattr(time_obj, 'strftime'):
        return time_obj.strftime("%H:%M")
        
    if isinstance(time_obj, timedelta):
        total_seconds = int(time_obj.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours:02}:{minutes:02}"
        
    return str(time_obj)[:5]

def _calcular_hora_fin(hora_inicio, duracion_minutos) -> str:
    """Calcula la hora de fin sumando minutos."""
    segundos_inicio = 0
    # Normalizar hora inicio a segundos
    if isinstance(hora_inicio, timedelta):
        segundos_inicio = int(hora_inicio.total_seconds())
    elif isinstance(hora_inicio, str):
        try:
            h, m = map(int, _format_time(hora_inicio).split(':'))
            segundos_inicio = h * 3600 + m * 60
        except: return "23:59"
    elif hasattr(hora_inicio, 'hour'): # datetime o time
        segundos_inicio = hora_inicio.hour * 3600 + hora_inicio.minute * 60
    
    segundos_totales = segundos_inicio + (duracion_minutos * 60)
    
    hours = segundos_totales // 3600
    minutes = (segundos_totales % 3600) // 60
    return f"{hours:02}:{minutes:02}"

format_date: Callable[[any], str] = lambda d: str(d)
req_logic: Callable[[int], str] = lambda r: "si" if r == 1 else "no"


# --- FUNCIONES DE TRANSFORMACIÓN DE DATOS ---

def generar_hechos_prolog_citas(lista_citas_db: List[Dict]) -> str:
    """
    Genera hechos: cita_ocupada(Dentista, Fecha, HoraInicio, HoraFin).
    ¡ESTA ES LA PARTE CLAVE QUE FALTABA!
    """
    citas_facts = []
    for c in lista_citas_db:
        dname = _esc(c['dentista_nombre'])
        fecha = format_date(c['fecha'])
        ini = _format_time(c['hora_inicio'])
        
        # Obtenemos la duración de la cita agendada (o 30 por defecto)
        duracion = c.get('duracion_minutos')
        if not duracion: duracion = 30 
        
        # Calculamos cuándo termina esa cita
        fin = _calcular_hora_fin(c['hora_inicio'], int(duracion))
        
        # Generamos el hecho con 4 ARGUMENTOS
        citas_facts.append(f"cita_ocupada('{dname}','{fecha}','{ini}','{fin}').")

    duracion_facts = {
        f"duracion_tratamiento('{_esc(c['tratamiento_nombre'])}',{int(c['duracion_minutos'])})." 
        for c in lista_citas_db if 'tratamiento_nombre' in c
    }
    
    req_facts = {
        f"requiere_equipo('{_esc(c['tratamiento_nombre'])}','{req_logic(c['requiere_equipo_especial'])}')." 
        for c in lista_citas_db if 'tratamiento_nombre' in c
    }

    return "\n".join(citas_facts + list(duracion_facts) + list(req_facts))


def generar_hechos_prolog_horarios(lista_horarios_db: List[Dict]) -> str:
    horario_to_fact = lambda h: (
        f"horario_laboral('{_esc(h['dentista_nombre'])}',"
        f"'{h['dia_semana']}',"
        f"'{_format_time(h['hora_inicio'])}',"
        f"'{_format_time(h['hora_fin'])}')."
    )
    return "\n".join(map(horario_to_fact, lista_horarios_db))


def generar_hechos_prolog_tratamiento_unico(tratamiento: Dict) -> str:
    tname = _esc(tratamiento["nombre"])
    dur = int(tratamiento["duracion_minutos"])
    req = req_logic(tratamiento["requiere_equipo_especial"])
    return f"duracion_tratamiento('{tname}',{dur}).\nrequiere_equipo('{tname}','{req}')."
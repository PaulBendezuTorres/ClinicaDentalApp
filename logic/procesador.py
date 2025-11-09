from typing import List, Dict

def _esc(s: str) -> str:
    return s.replace("'", "\\'")

def generar_hechos_prolog_citas(lista_citas_db: List[Dict]) -> str:
    def cita_to_fact(c):
        dname = _esc(c["dentista_nombre"])
        fecha = str(c["fecha"])
        hora = c["hora_inicio"].strftime("%H:%M") if hasattr(c["hora_inicio"], "strftime") else str(c["hora_inicio"])[:5]
        return f"cita_ocupada('{dname}','{fecha}','{hora}')."

    def trat_to_duracion(c):
        tname = _esc(c["tratamiento_nombre"])
        dur = int(c["duracion_minutos"])
        return f"duracion_tratamiento('{tname}',{dur})."

    def trat_to_req(c):
        tname = _esc(c["tratamiento_nombre"])
        req = "si" if int(c["requiere_equipo_especial"]) == 1 else "no"
        return f"requiere_equipo('{tname}','{req}')."

    hechos_citas = map(cita_to_fact, lista_citas_db)
    hechos_duracion = map(trat_to_duracion, lista_citas_db)
    hechos_req = map(trat_to_req, lista_citas_db)

    hechos = list(hechos_citas) + list(set(hechos_duracion)) + list(set(hechos_req))
    return "\n".join(hechos)

def generar_hechos_prolog_horarios(lista_horarios_db: List[Dict]) -> str:
    def horario_to_fact(h):
        dname = _esc(h["dentista_nombre"])
        dia = h["dia_semana"]
        hi = h["hora_inicio"].strftime("%H:%M") if hasattr(h["hora_inicio"], "strftime") else str(h["hora_inicio"])[:5]
        hf = h["hora_fin"].strftime("%H:%M") if hasattr(h["hora_fin"], "strftime") else str(h["hora_fin"])[:5]
        return f"horario_laboral('{dname}','{dia}','{hi}','{hf}')."

    hechos = map(horario_to_fact, lista_horarios_db)
    return "\n".join(hechos)

def generar_hechos_prolog_tratamiento_unico(tratamiento: Dict) -> str:
    tname = _esc(tratamiento["nombre"])
    dur = int(tratamiento["duracion_minutos"])
    req = "si" if int(tratamiento["requiere_equipo_especial"]) == 1 else "no"
    return f"duracion_tratamiento('{tname}',{dur}).\nrequiere_equipo('{tname}','{req}')."

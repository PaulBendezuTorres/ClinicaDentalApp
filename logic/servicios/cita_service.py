import os
from datetime import datetime, timedelta, date
from typing import List, Dict
from dataclasses import asdict
from pyswip import Prolog

from database.dao.cita_dao import CitaDAO
from database.dao.horario_dao import HorarioDAO
from database.dao.dentista_dao import DentistaDAO
from database.dao.tratamiento_dao import TratamientoDAO
from database.dao.paciente_dao import PacienteDAO
from database.dao.consultorio_dao import ConsultorioDAO
from clases.cita import Cita
from logic import procesador

class CitaService:
    def __init__(self):
        self.cita_dao = CitaDAO()
        self.horario_dao = HorarioDAO()
        self.dentista_dao = DentistaDAO()
        self.tratamiento_dao = TratamientoDAO()
        self.paciente_dao = PacienteDAO()
        self.consultorio_dao = ConsultorioDAO()
        
        self._prolog_engine = None

    def _inicializar_prolog(self):
        if self._prolog_engine is None:
            self._prolog_engine = Prolog()
            reglas_path = os.path.join(os.path.dirname(__file__), "..", "..", "prolog", "motor_reglas.pl")
            self._prolog_engine.consult(os.path.normpath(reglas_path))

    def _limpiar_hechos(self):
        p = self._prolog_engine
        p.retractall("cita_ocupada(_,_,_,_)")
        p.retractall("paciente_no_disponible(_,_)")
        p.retractall("filtro_turno(_)")
        p.retractall("filtro_dia(_)")
        p.retractall("equipo_especial_disponible(_,_)")
        p.retractall("horario_laboral(_,_,_,_)")
        p.retractall("duracion_tratamiento(_,_)")
        p.retractall("requiere_equipo(_,_)")

    def cerrar_motor(self):
        if self._prolog_engine:
            try:
                list(self._prolog_engine.query("halt."))
                print("Motor Prolog cerrado.")
            except: pass

    def buscar_horarios(self, fecha: str, dentista_id: int, tratamiento_id: int, paciente_id: int, 
                        filtro_turno: str = None, filtro_dias: list = None) -> List[Dict]:
        
        self._inicializar_prolog()
        self._limpiar_hechos()
        prolog = self._prolog_engine

        citas_objs = self.cita_dao.obtener_por_fecha(fecha)
        citas_dicts = [asdict(c) for c in citas_objs]
        
        horarios_objs = self.horario_dao.obtener_todos_para_reglas()
        horarios_dicts = [asdict(h) for h in horarios_objs if h.dentista_id == dentista_id]
        
        tratamiento = self.tratamiento_dao.obtener_por_id(tratamiento_id)
        if not tratamiento: return []
        trat_dict = asdict(tratamiento)

        dentista = self.dentista_dao.obtener_por_id(dentista_id)
        if not dentista: return []

        preferencias = self.paciente_dao.obtener_preferencias(paciente_id) 

        hechos_citas = procesador.generar_hechos_prolog_citas(citas_dicts)
        hechos_horarios = procesador.generar_hechos_prolog_horarios(horarios_dicts)
        hechos_trat = procesador.generar_hechos_prolog_tratamiento_unico(trat_dict)

        for linea in (hechos_citas + "\n" + hechos_horarios + "\n" + hechos_trat).splitlines():
            if linea.strip(): prolog.assertz(linea.strip()[:-1])

        for pref in preferencias:
            prolog.assertz(f"paciente_no_disponible('{pref['dia_semana']}', '{pref['turno']}')")

        if filtro_turno:
            turno_safe = filtro_turno.lower().replace("ñ", "n")
            prolog.assertz(f"filtro_turno('{turno_safe}')")
        
        if filtro_dias: 
            for d in filtro_dias: prolog.assertz(f"filtro_dia('{d}')")

        fecha_dt = datetime.strptime(fecha, "%Y-%m-%d")
        dia_semana = self._dia_semana_es(fecha_dt)
        dname = dentista.nombre.replace("'", "\\'")
        
        rangos = list(prolog.query(f"horario_laboral('{dname}','{dia_semana}', Ini, Fin)"))
        if not rangos: return []

        # Generar slots basados en la duración del tratamiento + tiempo de limpieza (15 min)
        duracion_slot = tratamiento.duracion_minutos + 15
        slots = []
        for r in rangos: slots += self._generar_slots(r["Ini"], r["Fin"], duracion_slot)

        consultorios = self.consultorio_dao.obtener_todos()
        cons_esp_ids = [c.id for c in consultorios if c.equipo_especial]
        
        if cons_esp_ids:
            for hhmm in slots:
                ocupados = len([c for c in citas_objs if c.hora_inicio[:5] == hhmm and c.consultorio_id in cons_esp_ids])
                if ocupados < len(cons_esp_ids):
                    prolog.assertz(f"equipo_especial_disponible('{fecha}','{hhmm}')")

        tname = tratamiento.nombre.replace("'", "\\'")
        resultados_validos = []
        for hhmm in slots:
            if list(prolog.query(f"encontrar_hora_valida('{dname}','{tname}','{fecha}','{dia_semana}','{hhmm}')")):
                resultados_validos.append(hhmm)

        return [{"fecha": fecha, "hora": h, "dia_semana": dia_semana} for h in sorted(list(set(resultados_validos)))]

    def encontrar_proxima(self, dentista_id, tratamiento_id, paciente_id, turno, dias):
        fecha_actual = date.today() + timedelta(days=1)
        limite = fecha_actual + timedelta(days=90)
        
        while fecha_actual <= limite:
            dia_sem = self._dia_semana_es(fecha_actual)
            if dia_sem in dias:
                res = self.buscar_horarios(fecha_actual.strftime('%Y-%m-%d'), dentista_id, tratamiento_id, paciente_id, turno, [dia_sem])
                if res: return res
            fecha_actual += timedelta(days=1)
        return []

    def confirmar_cita(self, datos: Dict) -> int:
        nueva = Cita(
            paciente_id=datos['paciente_id'],
            dentista_id=datos['dentista_id'],
            consultorio_id=datos['consultorio_id'],
            tratamiento_id=datos['tratamiento_id'],
            fecha=datos['fecha'],
            hora_inicio=datos['hora_inicio']
        )
        return self.cita_dao.crear(nueva)

    def listar_dashboard(self, filtro, busqueda):
        citas = self.cita_dao.obtener_todas_dashboard(filtro, busqueda)
        return [asdict(c) for c in citas] 

    def cambiar_estado(self, id, estado):
        self.cita_dao.actualizar_estado(id, estado)

    def obtener_historial(self, pid):
        return [asdict(c) for c in self.cita_dao.obtener_historial_paciente(pid)]

    def _dia_semana_es(self, d):
        return ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"][d.weekday()]
    
    def _generar_slots(self, inicio, fin, intervalo_minutos=30):
        """
        Genera slots de tiempo entre inicio y fin con el intervalo especificado.
        
        Args:
            inicio: Hora de inicio en formato HH:MM
            fin: Hora de fin en formato HH:MM
            intervalo_minutos: Intervalo entre slots en minutos (por defecto 30)
        
        Returns:
            Lista de slots en formato HH:MM
        """
        h0 = datetime.strptime(inicio, "%H:%M")
        h1 = datetime.strptime(fin, "%H:%M")
        slots = []
        while h0 < h1:
            slots.append(h0.strftime("%H:%M"))
            h0 += timedelta(minutes=intervalo_minutos)
        return slots
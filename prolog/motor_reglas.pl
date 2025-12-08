% --- DECLARACIÓN DE HECHOS DINÁMICOS ---
:- dynamic cita_ocupada/3.          % cita_ocupada(Dentista, Fecha, Hora).
:- dynamic horario_laboral/4.       % horario_laboral(Dentista, DiaSemana, HoraIni, HoraFin).
:- dynamic duracion_tratamiento/2.  % duracion_tratamiento(Tratamiento, Minutos).
:- dynamic requiere_equipo/2.       % requiere_equipo(Tratamiento, si|no).
:- dynamic equipo_especial_disponible/2. % equipo_especial_disponible(Fecha, Hora).
:- dynamic paciente_no_disponible/2.  % Preferencias guardadas del paciente
:- dynamic filtro_turno/1.            % Filtro dinámico de la UI
:- dynamic filtro_dia/1.              % Filtro dinámico de la UI

% --- CONFIGURACIÓN ---
% Tiempo en minutos que debe quedar libre después de una cita (limpieza/preparación)
tiempo_limpieza(15).


% --- REGLAS DE TIEMPO Y COMPARACIÓN ---
antes_igual(H1, H2) :- H1 @=< H2.
despues_igual(H1, H2) :- H1 @>= H2.

sumar_minutos(HHMM, Min, Resultado) :-
    sub_atom(HHMM, 0, 2, _, HhAtom),
    sub_atom(HHMM, 3, 2, _, MmAtom),
    atom_number(HhAtom, Hh), atom_number(MmAtom, Mm),
    Total is Hh*60 + Mm + Min,
    Hh2 is Total // 60,
    Mm2 is Total mod 60,
    format(atom(Resultado), '~|~`0t~d~2+:~|~`0t~d~2+', [Hh2, Mm2]).

% --- DEFINICIÓN DE TURNOS ---
turno(Hora, mañana) :- Hora @>= '08:00', Hora @< '14:00'.
turno(Hora, tarde) :- Hora @>= '14:00', Hora @< '20:00'.


% --- REGLAS DE DISPONIBILIDAD Y RESTRICCIONES ---

% disponible_dentista: El dentista no tiene otra cita JUSTO a esa hora de inicio.
disponible_dentista(Dentista, Fecha, Hora) :- \+ cita_ocupada(Dentista, Fecha, Hora).

% cumple_horario_laboral: La hora de inicio está dentro del rango laboral.
cumple_horario_laboral(Dentista, Dia, Hora) :-
    horario_laboral(Dentista, Dia, Ini, Fin),
    antes_igual(Ini, Hora),
    despues_igual(Fin, Hora).

% franja_libre: Verifica que haya espacio suficiente para el tratamiento MÁS el tiempo de limpieza.
franja_libre(Dentista, Fecha, Dia, Hora, MinDur) :-
    tiempo_limpieza(Buffer),
    DuracionTotal is MinDur + Buffer,              % Sumamos el buffer a la duración del tratamiento
    sumar_minutos(Hora, DuracionTotal, HoraFin),   % Calculamos a qué hora terminaría realmente la ocupación
    \+ cita_ocupada(Dentista, Fecha, Hora),        % No hay cita al inicio
    horario_laboral(Dentista, Dia, Ini, Fin),      % Obtenemos el horario del dentista
    antes_igual(Ini, Hora),                        % La cita empieza después de que llegue el dentista
    despues_igual(Fin, HoraFin).                   % La cita (con limpieza) termina antes de que se vaya

% equipo_ok: Verifica disponibilidad de equipo especial si se requiere.
equipo_ok(Tratamiento, Fecha, Hora) :-
    requiere_equipo(Tratamiento, no) ;
    ( requiere_equipo(Tratamiento, si), equipo_especial_disponible(Fecha, Hora) ).

% cumple_preferencia_paciente: Verifica las restricciones guardadas en la BD.
cumple_preferencia_paciente(Dia, Hora) :-
    turno(Hora, Turno),
    \+ paciente_no_disponible(Dia, Turno).

% --- REGLAS PARA FILTROS DINÁMICOS (UI) ---
% Usamos _ para evitar advertencias de Singleton Variables cuando no hay filtro.

cumple_filtro_turno(_) :- \+ filtro_turno(_), !. % Si no hay filtro, pasa.
cumple_filtro_turno(Hora) :- turno(Hora, Turno), filtro_turno(Turno).

cumple_filtro_dia(_) :- \+ filtro_dia(_), !. % Si no hay filtro, pasa.
cumple_filtro_dia(Dia) :- filtro_dia(Dia).

% --- REGLA PRINCIPAL COMPUESTA ---
encontrar_hora_valida(Dentista, Tratamiento, Fecha, Dia, Hora) :-
    duracion_tratamiento(Tratamiento, Min),
    cumple_horario_laboral(Dentista, Dia, Hora),
    franja_libre(Dentista, Fecha, Dia, Hora, Min),
    equipo_ok(Tratamiento, Fecha, Hora),
    cumple_preferencia_paciente(Dia, Hora),
    cumple_filtro_turno(Hora),
    cumple_filtro_dia(Dia).
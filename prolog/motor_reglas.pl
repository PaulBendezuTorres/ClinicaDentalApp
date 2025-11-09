
:- dynamic cita_ocupada/3.          % cita_ocupada(Dentista, Fecha, Hora).
:- dynamic horario_laboral/4.       % horario_laboral(Dentista, DiaSemana, HoraIni, HoraFin).
:- dynamic duracion_tratamiento/2.  % duracion_tratamiento(Tratamiento, Minutos).
:- dynamic requiere_equipo/2.       % requiere_equipo(Tratamiento, si|no).
:- dynamic equipo_especial_disponible/2. % equipo_especial_disponible(Fecha, Hora).
:- dynamic paciente_no_disponible/2.  % <-- HECHO NUEVO: paciente_no_disponible(Dia, Turno).


% --- REGLAS DE TIEMPO Y COMPARACIÓN ---
% Reglas de ayuda para trabajar con horas en formato 'HH:MM'.
% -----------------------------------------------------------------

% antes_igual(H1, H2): Verdadero si la hora H1 es anterior o igual a la hora H2.
antes_igual(H1, H2) :- H1 @=< H2.

% despues_igual(H1, H2): Verdadero si la hora H1 es posterior o igual a la hora H2.
despues_igual(H1, H2) :- H1 @>= H2.

% sumar_minutos(HHMM, Min, Resultado): Suma 'Min' minutos a una hora 'HHMM'.
sumar_minutos(HHMM, Min, Resultado) :-
    sub_atom(HHMM, 0, 2, _, HhAtom),
    sub_atom(HHMM, 3, 2, _, MmAtom),
    atom_number(HhAtom, Hh), atom_number(MmAtom, Mm),
    Total is Hh*60 + Mm + Min,
    Hh2 is Total // 60,
    Mm2 is Total mod 60,
    format(atom(Resultado), '~|~`0t~d~2+:~|~`0t~d~2+', [Hh2, Mm2]).

% --- REGLA DE TURNOS ---
% <-- SECCIÓN NUEVA: Define los rangos horarios para cada turno.
% -----------------------------------------------------------------

% turno(Hora, NombreTurno): Verdadero si la Hora pertenece al Turno.
turno(Hora, mañana) :- Hora @>= '08:00', Hora @< '14:00'.
turno(Hora, tarde) :- Hora @>= '14:00', Hora @< '20:00'.


% --- REGLAS DE DISPONIBILIDAD Y RESTRICCIONES ---
% El núcleo de la lógica. Cada regla define una condición que debe cumplirse.
% -----------------------------------------------------------------

% disponible_dentista: El dentista no tiene otra cita a esa misma hora.
disponible_dentista(Dentista, Fecha, Hora) :- \+ cita_ocupada(Dentista, Fecha, Hora).

% cumple_horario_laboral: La hora propuesta está dentro del horario de trabajo del dentista para ese día.
cumple_horario_laboral(Dentista, Dia, Hora) :-
    horario_laboral(Dentista, Dia, Ini, Fin),
    antes_igual(Ini, Hora),
    despues_igual(Fin, Hora).

% franja_libre: El intervalo completo de la cita (inicio y fin) está dentro del horario laboral y no hay cita al inicio.
franja_libre(Dentista, Fecha, Dia, Hora, MinDur) :-
    sumar_minutos(Hora, MinDur, HoraFin),
    \+ cita_ocupada(Dentista, Fecha, Hora),
    horario_laboral(Dentista, Dia, Ini, Fin),
    antes_igual(Ini, Hora),
    despues_igual(Fin, HoraFin).

% equipo_ok: El tratamiento no requiere equipo especial, o si lo requiere, hay equipo disponible.
equipo_ok(Tratamiento, Fecha, Hora) :-
    requiere_equipo(Tratamiento, no) ;
    ( requiere_equipo(Tratamiento, si), equipo_especial_disponible(Fecha, Hora) ).

% cumple_preferencia_paciente: <-- REGLA NUEVA: La hora no cae en un día/turno que el paciente ha marcado como no disponible.
cumple_preferencia_paciente(Dia, Hora) :-
    turno(Hora, Turno),
    \+ paciente_no_disponible(Dia, Turno).


% --- REGLA PRINCIPAL Y COMPUESTA ---
% Esta es la regla que llamamos desde Python. Unifica todas las demás.
% Una hora es válida si y solo si CUMPLE TODAS las siguientes condiciones.
% -----------------------------------------------------------------

encontrar_hora_valida(Dentista, Tratamiento, Fecha, Dia, Hora) :-
    duracion_tratamiento(Tratamiento, Min),       % 1. Conocemos la duración del tratamiento.
    cumple_horario_laboral(Dentista, Dia, Hora), % 2. El dentista trabaja a esa hora.
    franja_libre(Dentista, Fecha, Dia, Hora, Min), % 3. La franja completa está libre.
    equipo_ok(Tratamiento, Fecha, Hora),         % 4. El equipo necesario está disponible.
    cumple_preferencia_paciente(Dia, Hora).      % 5. <-- CONDICIÓN NUEVA: Al paciente le viene bien esa hora.
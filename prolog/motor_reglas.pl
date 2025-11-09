:- dynamic cita_ocupada/3.
:- dynamic horario_laboral/4.
:- dynamic duracion_tratamiento/2.
:- dynamic requiere_equipo/2.
:- dynamic equipo_especial_disponible/2.
:- dynamic paciente_no_disponible/2.
:- dynamic filtro_turno/1.
:- dynamic filtro_dia/1.

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

turno(Hora, mañana) :- Hora @>= '08:00', Hora @< '14:00'.
turno(Hora, tarde) :- Hora @>= '14:00', Hora @< '20:00'.

disponible_dentista(Dentista, Fecha, Hora) :- \+ cita_ocupada(Dentista, Fecha, Hora).

cumple_horario_laboral(Dentista, Dia, Hora) :-
    horario_laboral(Dentista, Dia, Ini, Fin),
    antes_igual(Ini, Hora),
    despues_igual(Fin, Hora).

franja_libre(Dentista, Fecha, Dia, Hora, MinDur) :-
    sumar_minutos(Hora, MinDur, HoraFin),
    \+ cita_ocupada(Dentista, Fecha, Hora),
    horario_laboral(Dentista, Dia, Ini, Fin),
    antes_igual(Ini, Hora),
    despues_igual(Fin, HoraFin).

equipo_ok(Tratamiento, Fecha, Hora) :-
    requiere_equipo(Tratamiento, no) ;
    ( requiere_equipo(Tratamiento, si), equipo_especial_disponible(Fecha, Hora) ).

cumple_preferencia_paciente(Dia, Hora) :-
    turno(Hora, Turno),
    \+ paciente_no_disponible(Dia, Turno).

% --- SECCIÓN CORREGIDA ---
% Si no hay filtro, la regla es verdadera sin importar el valor de la Hora.
cumple_filtro_turno(_) :- \+ filtro_turno(_), !.
% Si hay filtro, la Hora sí importa y debe coincidir.
cumple_filtro_turno(Hora) :- turno(Hora, Turno), filtro_turno(Turno).

% Si no hay filtro, la regla es verdadera sin importar el valor del Dia.
cumple_filtro_dia(_) :- \+ filtro_dia(_), !.
% Si hay filtro, el Dia sí importa y debe coincidir.
cumple_filtro_dia(Dia) :- filtro_dia(Dia).
% --- FIN DE LA SECCIÓN CORREGIDA ---

encontrar_hora_valida(Dentista, Tratamiento, Fecha, Dia, Hora) :-
    duracion_tratamiento(Tratamiento, Min),
    cumple_horario_laboral(Dentista, Dia, Hora),
    franja_libre(Dentista, Fecha, Dia, Hora, Min),
    equipo_ok(Tratamiento, Fecha, Hora),
    cumple_preferencia_paciente(Dia, Hora),
    cumple_filtro_turno(Hora),
    cumple_filtro_dia(Dia).
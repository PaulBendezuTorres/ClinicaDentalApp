
:- dynamic cita_ocupada/3.          % cita_ocupada(Dentista, Fecha, Hora).
:- dynamic horario_laboral/4.       % horario_laboral(Dentista, DiaSemana, HoraIni, HoraFin).
:- dynamic duracion_tratamiento/2.  % duracion_tratamiento(Tratamiento, Minutos).
:- dynamic requiere_equipo/2.       % requiere_equipo(Tratamiento, si|no).
:- dynamic equipo_especial_disponible/2. % equipo_especial_disponible(Fecha, Hora).


% comparadores simples para horas en formato 'HH:MM'
% Antes o igual: verdadero si H1 <= H2 (comparación de átomos ordenada).
antes_igual(H1, H2) :- H1 @=< H2.

% Después o igual: verdadero si H1 >= H2.
despues_igual(H1, H2) :- H1 @>= H2.


% sumar_minutos(HHMM, Min, Resultado)
% Conviene usarlo para calcular el fin de una franja: dado 'HH:MM' suma Min minutos y devuelve 'HH:MM'.
% - HHMM: átomo 'HH:MM'
% - Min: entero (puede ser positivo o negativo)
% - Resultado: átomo 'HH2:MM2' con ceros a la izquierda cuando correspondan.
% Ejemplo: sumar_minutos('09:30', 30, R) -> R = '10:00'.
sumar_minutos(HHMM, Min, Resultado) :-
    sub_atom(HHMM, 0, 2, _, HhAtom),        % extrae las dos primeras cifras de hora
    sub_atom(HHMM, 3, 2, _, MmAtom),        % extrae las dos cifras de minutos
    atom_number(HhAtom, Hh), atom_number(MmAtom, Mm),
    Total is Hh*60 + Mm + Min,
    Hh2 is Total // 60,
    Mm2 is Total mod 60,
    format(atom(Resultado), '~|~`0t~d~2+:~|~`0t~d~2+', [Hh2, Mm2]).


% disponible_dentista(Dentista, Fecha, Hora)
% True si no existe una cita ocupada para ese dentista en la fecha y hora dadas.
% Nota: cita_ocupada/3 es un hecho dinámico que normalmente se assertz desde Python con formato
% cita_ocupada('Dr X','2025-10-23','09:30').
disponible_dentista(Dentista, Fecha, Hora) :-
    \+ cita_ocupada(Dentista, Fecha, Hora).


% cumple_horario_laboral(Dentista, Dia, Hora)
% True si existe un hecho horario_laboral(Dentista, Dia, Ini, Fin) tal que Ini <= Hora <= Fin.
% - Dia suele ser un átomo como 'lunes', 'martes', ... (coincidiendo con la DB).
cumple_horario_laboral(Dentista, Dia, Hora) :-
    horario_laboral(Dentista, Dia, Ini, Fin),
    antes_igual(Ini, Hora),
    despues_igual(Fin, Hora).


% franja_libre(Dentista, Fecha, Dia, Hora, MinDur)
% Comprueba que para un dentista en una fecha y día concreto la franja que comienza en Hora
% y tiene duración MinDur minutos cabe dentro de su horario y no está ocupada al inicio.
% Se usa sumar_minutos/3 para calcular la hora de fin de la franja (HoraFin).
franja_libre(Dentista, Fecha, Dia, Hora, MinDur) :-
    sumar_minutos(Hora, MinDur, HoraFin),
    \+ cita_ocupada(Dentista, Fecha, Hora),
    horario_laboral(Dentista, Dia, Ini, Fin),
    antes_igual(Ini, Hora),
    despues_igual(Fin, HoraFin).


% equipo_ok(Tratamiento, Fecha, Hora)
% True si el tratamiento no requiere equipo especial, o si lo requiere y hay equipo disponible
% en esa fecha y hora (hecho dinámico equipo_especial_disponible/2).
% requiere_equipo(Tratamiento, si|no) debe existir como hecho previo.
equipo_ok(Tratamiento, Fecha, Hora) :-
    requiere_equipo(Tratamiento, no) ;
    ( requiere_equipo(Tratamiento, si), equipo_especial_disponible(Fecha, Hora) ).


% encontrar_hora_valida(Dentista, Tratamiento, Fecha, Dia, Hora)
% Regla compuesta que indica si una hora concreta es válida para agendar un tratamiento:
% - verifica la duración del tratamiento
% - que la hora cumpla el horario laboral
% - que exista una franja libre con la duración necesaria
% - y que el equipo especial esté OK si se requiere.
% Output: la consulta típica desde Python será probar diferentes Hora (p. ej. '09:00')
encontrar_hora_valida(Dentista, Tratamiento, Fecha, Dia, Hora) :-
    duracion_tratamiento(Tratamiento, Min),
    cumple_horario_laboral(Dentista, Dia, Hora),
    franja_libre(Dentista, Fecha, Dia, Hora, Min),
    equipo_ok(Tratamiento, Fecha, Hora).

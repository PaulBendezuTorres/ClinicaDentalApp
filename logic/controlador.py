
from logic.sistema import sistema

# --- USUARIOS ---
verificar_credenciales = sistema.usuario.verificar_credenciales
obtener_lista_usuarios = sistema.usuario.obtener_todos
registrar_usuario = sistema.usuario.crear
modificar_usuario = sistema.usuario.actualizar
borrar_usuario = sistema.usuario.eliminar

# --- PACIENTES ---
obtener_lista_pacientes = sistema.paciente.obtener_todos
crear_paciente = sistema.paciente.crear
actualizar_paciente = sistema.paciente.actualizar
eliminar_paciente = sistema.paciente.eliminar

# --- DENTISTAS ---
obtener_lista_dentistas = sistema.dentista.obtener_todos
registrar_dentista = sistema.dentista.crear
modificar_dentista = sistema.dentista.actualizar
borrar_dentista = sistema.dentista.eliminar

# --- TRATAMIENTOS ---
obtener_lista_tratamientos = sistema.tratamiento.obtener_todos
registrar_tratamiento = sistema.tratamiento.crear
modificar_tratamiento = sistema.tratamiento.actualizar
borrar_tratamiento = sistema.tratamiento.eliminar

# --- CONSULTORIOS ---
obtener_lista_consultorios = sistema.consultorio.obtener_todos
registrar_consultorio = sistema.consultorio.crear
modificar_consultorio = sistema.consultorio.actualizar
borrar_consultorio = sistema.consultorio.eliminar

# --- HORARIOS ---
obtener_horarios_dentista = sistema.horario.obtener_por_dentista
crear_horario_dentista = sistema.horario.crear
borrar_horario_dentista = sistema.horario.eliminar

# --- CITAS & PROLOG ---
buscar_horarios_disponibles = sistema.cita.buscar_horarios
encontrar_proxima_cita = sistema.cita.encontrar_proxima
confirmar_cita = sistema.cita.confirmar_cita
listar_citas = sistema.cita.listar_dashboard
cambiar_estado_cita = sistema.cita.cambiar_estado
obtener_historial_paciente = sistema.cita.obtener_historial
cerrar_prolog = sistema.cita.cerrar_motor

# --- PAPELERA  ---
def obtener_eliminados(tipo):
    if tipo == "Usuarios": return sistema.usuario.obtener_eliminados()
    if tipo == "Dentistas": return sistema.dentista.obtener_eliminados()
    if tipo == "Tratamientos": return sistema.tratamiento.obtener_eliminados()
    if tipo == "Consultorios": return sistema.consultorio.obtener_eliminados()
    if tipo == "Pacientes": return sistema.paciente.obtener_eliminados()
    return []

def restaurar_elemento(tipo, id):
    if tipo == "Usuarios": sistema.usuario.restaurar(id)
    elif tipo == "Dentistas": sistema.dentista.restaurar(id)
    elif tipo == "Tratamientos": sistema.tratamiento.restaurar(id)
    elif tipo == "Consultorios": sistema.consultorio.restaurar(id)
    elif tipo == "Pacientes": sistema.paciente.restaurar(id)
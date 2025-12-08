import ttkbootstrap as ttk
from tkinter import messagebox
from logic import controlador
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame
from datetime import date, timedelta, datetime
import threading
import queue

# --- Componente Reutilizable: Tarjeta de Horario ---
class HorarioCard(ttk.Frame):
    def __init__(self, parent, horario_data, select_callback):
        super().__init__(parent, padding=10, bootstyle="light")
        self.horario_data = horario_data
        self.select_callback = select_callback
        
        self.bind("<Button-1>", self._on_select)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.label_hora = ttk.Label(self, text=horario_data['hora'], font=("Segoe UI", 14, "bold"), bootstyle="inverse-light")
        self.label_hora.grid(row=0, column=0, sticky="w")
        
        dia_semana_str = horario_data['dia_semana'].capitalize()
        self.label_dia_fecha = ttk.Label(self, text=f"{dia_semana_str}, {horario_data['fecha']}", bootstyle="secondary-inverse-light")
        self.label_dia_fecha.grid(row=1, column=0, sticky="w")
        
        self.label_hora.bind("<Button-1>", self._on_select)
        self.label_dia_fecha.bind("<Button-1>", self._on_select)

    def _on_select(self, event):
        self.select_callback(self)

    def select(self):
        self.config(bootstyle="info")
        self.label_hora.config(bootstyle="inverse-info")
        self.label_dia_fecha.config(bootstyle="inverse-info")

    def deselect(self):
        self.config(bootstyle="light")
        self.label_hora.config(bootstyle="inverse-light")
        self.label_dia_fecha.config(bootstyle="secondary-inverse-light")


class PaginaAgendarCita(ttk.Frame): 
    # --- CORRECCIÓN AQUÍ: Se añade usuario_data=None ---
    def __init__(self, parent, usuario_data=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self.cola_resultados = queue.Queue()
        self.selected_horario_card = None
        self._build()
        self._cargar_dropdowns()
        self.after(100, self._procesar_cola)

    def _build(self):
        main_frame = ttk.Frame(self, padding=(20, 10))
        main_frame.pack(fill="both", expand=True)
        ttk.Label(main_frame, text="Agendar Nueva Cita", font=("Segoe UI", 18, "bold")).pack(pady=(0, 20), anchor="w")
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)
        form_frame = ttk.Frame(content_frame, padding=(0, 0, 30, 0))
        form_frame.grid(row=0, column=0, sticky="nsew")
        ttk.Label(form_frame, text="1. Seleccione el Paciente:").pack(fill="x", pady=(10, 2))
        self.cmb_paciente = ttk.Combobox(form_frame, state="readonly")
        self.cmb_paciente.pack(fill="x")
        ttk.Label(form_frame, text="2. Seleccione el Dentista:").pack(fill="x", pady=(10, 2))
        self.cmb_dentista = ttk.Combobox(form_frame, state="readonly")
        self.cmb_dentista.pack(fill="x")
        ttk.Label(form_frame, text="3. Seleccione el Tratamiento:").pack(fill="x", pady=(10, 2))
        self.cmb_tratamiento = ttk.Combobox(form_frame, state="readonly")
        self.cmb_tratamiento.pack(fill="x")
        ttk.Label(form_frame, text="4. Seleccione la Fecha (para búsqueda específica):").pack(fill="x", pady=(10, 2))
        self.ent_fecha = DateEntry(form_frame, bootstyle="info", firstweekday=0, dateformat="%Y-%m-%d")
        self.ent_fecha.pack(fill="x")
        filtros_frame = ttk.Labelframe(form_frame, text="Filtros de Preferencia", padding=15)
        filtros_frame.pack(fill="x", pady=20)
        ttk.Label(filtros_frame, text="Turno preferido:").pack(anchor="w")
        self.cmb_turno = ttk.Combobox(filtros_frame, values=["Cualquiera", "Mañana", "Tarde"])
        self.cmb_turno.pack(fill="x", pady=(2, 10))
        self.cmb_turno.set("Cualquiera")
        ttk.Label(filtros_frame, text="Días de la semana preferidos:").pack(anchor="w")
        dias_frame = ttk.Frame(filtros_frame)
        dias_frame.pack(fill="x")
        self.check_dias_vars = {}
        dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
        for dia in dias:
            var = ttk.BooleanVar()
            chk = ttk.Checkbutton(dias_frame, text=dia.capitalize(), variable=var, bootstyle="info")
            chk.pack(side="left", padx=5)
            self.check_dias_vars[dia] = var
        botones_busqueda_frame = ttk.Frame(form_frame)
        botones_busqueda_frame.pack(fill="x", pady=10)
        botones_busqueda_frame.columnconfigure((0,1), weight=1)
        self.btn_buscar_fecha = ttk.Button(botones_busqueda_frame, text="Buscar en Fecha", command=self._on_buscar_fecha, bootstyle="info")
        self.btn_buscar_fecha.grid(row=0, column=0, sticky="ew", padx=(0,5))
        self.btn_buscar_proxima = ttk.Button(botones_busqueda_frame, text="Encontrar Próxima Disponible", command=self._on_buscar_proxima, bootstyle="primary")
        self.btn_buscar_proxima.grid(row=0, column=1, sticky="ew", padx=(5,0))

        results_frame = ttk.Frame(content_frame)
        results_frame.grid(row=0, column=1, sticky="nsew")
        results_frame.rowconfigure(1, weight=1)

        ttk.Label(results_frame, text="5. Horarios Disponibles:").pack(anchor="w")
        
        horarios_canvas = ScrolledFrame(results_frame, autohide=True)
        horarios_canvas.pack(pady=5, fill="both", expand=True)
        self.horarios_container = ttk.Frame(horarios_canvas)
        self.horarios_container.pack(fill="x", expand=True)

        ttk.Label(results_frame, text="6. Seleccione el Consultorio:").pack(anchor="w", pady=(10, 2))
        self.cmb_consultorio = ttk.Combobox(results_frame, state="readonly")
        self.cmb_consultorio.pack(fill="x")
        self.btn_confirmar = ttk.Button(results_frame, text="Confirmar Cita", command=self._on_confirmar, bootstyle="success")
        self.btn_confirmar.pack(pady=20, fill="x")

    def _limpiar_y_cargar(self):
        for widget in self.horarios_container.winfo_children(): widget.destroy()
        ttk.Label(self.horarios_container, text="Buscando...", bootstyle="info").pack(pady=20)
        self.update_idletasks()

    def _procesar_cola(self):
        try:
            resultado = self.cola_resultados.get_nowait()
            for widget in self.horarios_container.winfo_children(): widget.destroy()
            self.selected_horario_card = None

            if isinstance(resultado, Exception):
                messagebox.showerror("Error de Búsqueda", str(resultado), parent=self)
            elif not resultado:
                ttk.Label(self.horarios_container, text="No se encontraron horarios.", bootstyle="warning").pack(pady=20)
            else:
                for horario_data in resultado:
                    card = HorarioCard(self.horarios_container, horario_data, self._on_horario_select)
                    card.pack(fill="x", padx=5, pady=3)
        except queue.Empty:
            pass
        finally:
            self.after(100, self._procesar_cola)
            
    def _on_horario_select(self, selected_card: HorarioCard):
        if self.selected_horario_card:
            self.selected_horario_card.deselect()
        self.selected_horario_card = selected_card
        self.selected_horario_card.select()

    def _on_confirmar(self):
        if not self.selected_horario_card:
            messagebox.showwarning("Validación", "Seleccione un horario de la lista.", parent=self)
            return

        horario_seleccionado = self.selected_horario_card.horario_data
        fecha = horario_seleccionado["fecha"]
        hora = horario_seleccionado["hora"]
        
        pid = self._parse_id_from_combo(self.cmb_paciente.get())
        did = self._parse_id_from_combo(self.cmb_dentista.get())
        tid = self._parse_id_from_combo(self.cmb_tratamiento.get())
        cid = self._parse_id_from_combo(self.cmb_consultorio.get())
        
        if not (pid and did and tid and cid):
            messagebox.showwarning("Validación", "Complete todos los campos del formulario.", parent=self)
            return
        try:
            new_id = controlador.confirmar_cita({
                "paciente_id": pid, "dentista_id": did, "consultorio_id": cid,
                "tratamiento_id": tid, "fecha": fecha, "hora_inicio": hora
            })
            messagebox.showinfo("Éxito", f"Cita creada con ID {new_id}.", parent=self)
            for widget in self.horarios_container.winfo_children(): widget.destroy()
            self.selected_horario_card = None
        except Exception as e:
            messagebox.showerror("Error al Guardar", str(e), parent=self)
    
    def _get_form_data(self):
        data = { "pid": self._parse_id_from_combo(self.cmb_paciente.get()), "did": self._parse_id_from_combo(self.cmb_dentista.get()), "tid": self._parse_id_from_combo(self.cmb_tratamiento.get()), "turno": self.cmb_turno.get(), "dias": [dia for dia, var in self.check_dias_vars.items() if var.get()] }
        if data["turno"] == "Cualquiera": data["turno"] = None
        return data
        
    def _on_buscar_fecha(self):
        self._limpiar_y_cargar()
        data = self._get_form_data()
        data["fecha_str"] = self.ent_fecha.entry.get().strip()
        if not (data["pid"] and data["did"] and data["tid"] and data["fecha_str"]):
            messagebox.showwarning("Validación", "Para buscar por fecha, debe seleccionar paciente, dentista, tratamiento y una fecha.", parent=self)
            self._procesar_cola()
            return
        hilo = threading.Thread(target=self._worker_buscar_fecha, args=(data,), daemon=True)
        hilo.start()
        
    def _worker_buscar_fecha(self, data):
        try:
            resultados = controlador.buscar_horarios_disponibles(data["fecha_str"], data["did"], data["tid"], data["pid"], data["turno"], data["dias"])
            self.cola_resultados.put(resultados)
        except Exception as e: self.cola_resultados.put(e)
        
    def _on_buscar_proxima(self):
        self._limpiar_y_cargar()
        data = self._get_form_data()
        if not (data["pid"] and data["did"] and data["tid"]):
            messagebox.showwarning("Validación", "Debe seleccionar paciente, dentista y tratamiento.", parent=self)
            self._procesar_cola()
            return
        if not data["dias"]:
            messagebox.showwarning("Validación", "Debe seleccionar al menos un día de la semana para esta búsqueda.", parent=self)
            self._procesar_cola()
            return
        hilo = threading.Thread(target=self._worker_buscar_proxima, args=(data,), daemon=True)
        hilo.start()
        
    def _worker_buscar_proxima(self, data):
        try:
            resultados = controlador.encontrar_proxima_cita(data["did"], data["tid"], data["pid"], data["turno"], data["dias"])
            self.cola_resultados.put(resultados)
        except Exception as e: self.cola_resultados.put(e)
        
    def _cargar_dropdowns(self):
        self._pacientes = controlador.obtener_lista_pacientes()
        self.cmb_paciente["values"] = [f'{p["id"]} - {p["nombre"]}' for p in self._pacientes]
        self._dentistas = controlador.obtener_lista_dentistas()
        self.cmb_dentista["values"] = [f'{d["id"]} - {d["nombre"]} ({d["especialidad"]})' for d in self._dentistas]
        self._tratamientos = controlador.obtener_lista_tratamientos()
        self.cmb_tratamiento["values"] = [f'{t["id"]} - {t["nombre"]} ({t["duracion_minutos"]} min)' for t in self._tratamientos]
        self._consultorios = controlador.obtener_lista_consultorios()
        self.cmb_consultorio["values"] = [f'{c["id"]} - {c["nombre_sala"]}{" *" if int(c["equipo_especial"])==1 else ""}' for c in self._consultorios]
        
    def _parse_id_from_combo(self, combo_text: str) -> int:
        try: return int(combo_text.split(" - ")[0])
        except (ValueError, IndexError): return 0
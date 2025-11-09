import ttkbootstrap as ttk
from tkinter import messagebox
from logic import controlador
from ttkbootstrap.widgets import DateEntry
from datetime import date, timedelta, datetime
import threading # Para el "ayudante"
import queue     # Para la comunicación segura

class PaginaAgendarCita(ttk.Frame): 
    def __init__(self, parent):
        super().__init__(parent)
        # 1. Creamos la "bandeja de entrada" para los resultados
        self.cola_resultados = queue.Queue()
        self._build()
        self._cargar_dropdowns()
        # 2. Le decimos al "recepcionista" que revise la bandeja cada 100ms
        self.after(100, self._procesar_cola)

    def _build(self):
        # ... (Toda la construcción de la interfaz es EXACTAMENTE la misma) ...
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
        ttk.Label(form_frame, text="4. Seleccione la Fecha:").pack(fill="x", pady=(10, 2))
        self.ent_fecha = DateEntry(form_frame, bootstyle="info", firstweekday=0, dateformat="%Y-%m-%d")
        self.ent_fecha.pack(fill="x")
        filtros_frame = ttk.Labelframe(form_frame, text="Filtros Opcionales de Preferencia", padding=15)
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
        self.btn_buscar = ttk.Button(form_frame, text="Buscar Horarios Disponibles", command=self._on_buscar, bootstyle="info")
        self.btn_buscar.pack(pady=20, fill="x")
        results_frame = ttk.Frame(content_frame)
        results_frame.grid(row=0, column=1, sticky="nsew")
        results_frame.rowconfigure(1, weight=1)
        ttk.Label(results_frame, text="5. Horarios Disponibles:").pack(anchor="w")
        self.list_horas = ttk.Treeview(results_frame, columns=["hora"], show="headings", height=10)
        self.list_horas.heading("hora", text="Hora")
        self.list_horas.column("hora", width=100, anchor="center")
        self.list_horas.pack(pady=5, fill="both", expand=True)
        ttk.Label(results_frame, text="6. Seleccione el Consultorio:").pack(anchor="w", pady=(10, 2))
        self.cmb_consultorio = ttk.Combobox(results_frame, state="readonly")
        self.cmb_consultorio.pack(fill="x")
        self.btn_confirmar = ttk.Button(results_frame, text="Confirmar Cita", command=self._on_confirmar, bootstyle="success")
        self.btn_confirmar.pack(pady=20, fill="x")

    def _on_buscar(self):
        # 3. La tarea del "recepcionista" ahora es muy simple
        
        # Primero, limpiamos la lista y mostramos un mensaje de "Cargando..."
        for i in self.list_horas.get_children(): self.list_horas.delete(i)
        self.list_horas.insert("", "end", values=("Buscando...",))
        self.update_idletasks() # Forzamos la actualización de la UI

        # Recolectamos los datos (esto no cambia)
        fecha_str = self.ent_fecha.entry.get().strip()
        pid = self._parse_id_from_combo(self.cmb_paciente.get())
        did = self._parse_id_from_combo(self.cmb_dentista.get())
        tid = self._parse_id_from_combo(self.cmb_tratamiento.get())
        turno_preferido = self.cmb_turno.get()
        if turno_preferido == "Cualquiera": turno_preferido = None
        dias_preferidos = [dia for dia, var in self.check_dias_vars.items() if var.get()]
        
        # 4. Creamos y lanzamos al "ayudante" (el hilo)
        # Le pasamos la tarea que tiene que hacer (_worker_buscar_horarios) y los datos que necesita
        hilo_busqueda = threading.Thread(
            target=self._worker_buscar_horarios,
            args=(fecha_str, did, tid, pid, turno_preferido, dias_preferidos),
            daemon=True
        )
        hilo_busqueda.start()

    def _worker_buscar_horarios(self, fecha_str, did, tid, pid, turno, dias):
        # 5. Esta función la ejecuta el "ayudante" en segundo plano
        try:
            # Aquí va la llamada pesada que antes congelaba la app
            resultados = controlador.buscar_horarios_disponibles(fecha_str, did, tid, pid, turno, dias)
            # Cuando termina, pone el resultado en la "bandeja de entrada"
            self.cola_resultados.put(resultados)
        except Exception as e:
            # Si hay un error, también lo ponemos en la bandeja para mostrarlo
            self.cola_resultados.put(e)

    def _procesar_cola(self):
        # 6. El "recepcionista" revisa su bandeja de entrada
        try:
            # get_nowait() coge un mensaje si lo hay, si no, lanza una excepción
            resultado = self.cola_resultados.get_nowait()

            # Limpiamos la lista ("Buscando...")
            for i in self.list_horas.get_children(): self.list_horas.delete(i)

            if isinstance(resultado, Exception):
                # Si el ayudante nos envió un error, lo mostramos
                messagebox.showerror("Error de Búsqueda", str(resultado), parent=self)
            elif not resultado:
                # Si nos envió una lista vacía
                self.list_horas.insert("", "end", values=("No hay horarios",))
            else:
                # Si nos envió la lista de horarios
                for h in resultado: self.list_horas.insert("", "end", values=(h,))

        except queue.Empty:
            # Si la bandeja está vacía, no hacemos nada
            pass
        finally:
            # Y le decimos que vuelva a revisar en 100ms
            self.after(100, self._procesar_cola)

    # El resto de los métodos (_cargar_dropdowns, _parse_id_from_combo, _on_confirmar)
    # no necesitan ningún cambio.
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

    def _on_confirmar(self):
        sel = self.list_horas.focus()
        if not sel:
            messagebox.showwarning("Validación", "Seleccione un horario de la lista.", parent=self)
            return
        hora = self.list_horas.item(sel)["values"][0]
        if hora in ("No hay horarios", "Buscando..."):
             messagebox.showwarning("Validación", "No hay un horario válido seleccionado.", parent=self)
             return
        fecha = self.ent_fecha.entry.get().strip()
        pid = self._parse_id_from_combo(self.cmb_paciente.get())
        did = self._parse_id_from_combo(self.cmb_dentista.get())
        tid = self._parse_id_from_combo(self.cmb_tratamiento.get())
        cid = self._parse_id_from_combo(self.cmb_consultorio.get())
        if not (pid and did and tid and cid and fecha and hora):
            messagebox.showwarning("Validación", "Complete todos los campos antes de confirmar.", parent=self)
            return
        try:
            new_id = controlador.confirmar_cita({
                "paciente_id": pid, "dentista_id": did, "consultorio_id": cid,
                "tratamiento_id": tid, "fecha": fecha, "hora_inicio": hora
            })
            messagebox.showinfo("Éxito", f"Cita creada con ID {new_id}.", parent=self)
            self.list_horas.delete(*self.list_horas.get_children())
        except Exception as e:
            messagebox.showerror("Error al Guardar", str(e), parent=self)
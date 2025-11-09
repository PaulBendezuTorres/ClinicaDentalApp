import ttkbootstrap as ttk
from tkinter import messagebox
from logic import controlador
from ttkbootstrap.widgets import DateEntry
from datetime import date, timedelta, datetime
import threading
import queue

class PaginaAgendarCita(ttk.Frame): 
    def __init__(self, parent):
        super().__init__(parent)
        self.cola_resultados = queue.Queue()
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

        # --- Frame para los botones de búsqueda ---
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
        # --- MODIFICACIÓN DE LA TABLA DE RESULTADOS ---
        self.list_horas = ttk.Treeview(results_frame, columns=("fecha", "hora"), show="headings", height=10)
        self.list_horas.heading("fecha", text="Fecha")
        self.list_horas.heading("hora", text="Hora")
        self.list_horas.column("fecha", width=120, anchor="center")
        self.list_horas.column("hora", width=100, anchor="center")
        self.list_horas.pack(pady=5, fill="both", expand=True)

        ttk.Label(results_frame, text="6. Seleccione el Consultorio:").pack(anchor="w", pady=(10, 2))
        self.cmb_consultorio = ttk.Combobox(results_frame, state="readonly")
        self.cmb_consultorio.pack(fill="x")
        self.btn_confirmar = ttk.Button(results_frame, text="Confirmar Cita", command=self._on_confirmar, bootstyle="success")
        self.btn_confirmar.pack(pady=20, fill="x")

    def _limpiar_y_cargar(self):
        for i in self.list_horas.get_children(): self.list_horas.delete(i)
        self.list_horas.insert("", "end", values=("Buscando...", ""))
        self.update_idletasks()

    def _get_form_data(self):
        data = {
            "pid": self._parse_id_from_combo(self.cmb_paciente.get()),
            "did": self._parse_id_from_combo(self.cmb_dentista.get()),
            "tid": self._parse_id_from_combo(self.cmb_tratamiento.get()),
            "turno": self.cmb_turno.get(),
            "dias": [dia for dia, var in self.check_dias_vars.items() if var.get()]
        }
        if data["turno"] == "Cualquiera": data["turno"] = None
        return data

    def _on_buscar_fecha(self):
        self._limpiar_y_cargar()
        data = self._get_form_data()
        data["fecha_str"] = self.ent_fecha.entry.get().strip()

        if not (data["pid"] and data["did"] and data["tid"] and data["fecha_str"]):
            messagebox.showwarning("Validación", "Para buscar por fecha, debe seleccionar paciente, dentista, tratamiento y una fecha.", parent=self)
            self._procesar_cola() # Para limpiar el "Buscando..."
            return

        hilo = threading.Thread(target=self._worker_buscar_fecha, args=(data,), daemon=True)
        hilo.start()

    def _worker_buscar_fecha(self, data):
        try:
            resultados = controlador.buscar_horarios_disponibles(
                data["fecha_str"], data["did"], data["tid"], data["pid"], data["turno"], data["dias"]
            )
            self.cola_resultados.put(resultados)
        except Exception as e:
            self.cola_resultados.put(e)

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
            resultados = controlador.encontrar_proxima_cita(
                data["did"], data["tid"], data["pid"], data["turno"], data["dias"]
            )
            self.cola_resultados.put(resultados)
        except Exception as e:
            self.cola_resultados.put(e)

    def _procesar_cola(self):
        try:
            resultado = self.cola_resultados.get_nowait()
            for i in self.list_horas.get_children(): self.list_horas.delete(i)

            if isinstance(resultado, Exception):
                messagebox.showerror("Error de Búsqueda", str(resultado), parent=self)
            elif not resultado:
                self.list_horas.insert("", "end", values=("No hay horarios", ""))
            else:
                if isinstance(resultado[0], dict): # Resultado de "Buscar Próxima"
                    for item in resultado:
                        self.list_horas.insert("", "end", values=(item['fecha'], item['hora']))
                else: # Resultado de "Buscar en Fecha"
                    fecha_str = self.ent_fecha.entry.get().strip()
                    for h in resultado:
                        self.list_horas.insert("", "end", values=(fecha_str, h))
        except queue.Empty:
            pass
        finally:
            self.after(100, self._procesar_cola)

    def _on_confirmar(self):
        sel = self.list_horas.focus()
        if not sel:
            messagebox.showwarning("Validación", "Seleccione un horario de la lista.", parent=self)
            return
        
        values = self.list_horas.item(sel)["values"]
        if not values or values[0] in ("No hay horarios", "Buscando..."):
             messagebox.showwarning("Validación", "No hay un horario válido seleccionado.", parent=self)
             return

        fecha, hora = values
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
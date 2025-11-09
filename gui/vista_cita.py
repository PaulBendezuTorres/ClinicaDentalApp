import ttkbootstrap as ttk
from tkinter import messagebox
from logic import controlador
from ttkbootstrap.widgets import DateEntry
from datetime import date, timedelta, datetime 

class PaginaAgendarCita(ttk.Frame): 
    def __init__(self, parent):
        super().__init__(parent)
        self._build()
        self._cargar_dropdowns()

    def _build(self):
        # Frame principal con padding general
        main_frame = ttk.Frame(self, padding=(20, 10))
        main_frame.pack(fill="both", expand=True)

        # Título de la página
        ttk.Label(main_frame, text="Agendar Nueva Cita", font=("Segoe UI", 18, "bold")).pack(pady=(0, 20), anchor="w")

        # --- Contenedor principal con dos columnas: Formulario | Resultados ---
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)
        content_frame.columnconfigure(0, weight=2)
        content_frame.columnconfigure(1, weight=1)

        # --- Columna Izquierda: Formulario de Selección ---
        form_frame = ttk.Frame(content_frame, padding=(0, 0, 30, 0))
        form_frame.grid(row=0, column=0, sticky="nsew")
        
        # Paciente
        ttk.Label(form_frame, text="1. Seleccione el Paciente:").pack(fill="x", pady=(10, 2))
        self.cmb_paciente = ttk.Combobox(form_frame, state="readonly")
        self.cmb_paciente.pack(fill="x")

        # Dentista
        ttk.Label(form_frame, text="2. Seleccione el Dentista:").pack(fill="x", pady=(10, 2))
        self.cmb_dentista = ttk.Combobox(form_frame, state="readonly")
        self.cmb_dentista.pack(fill="x")

        # Tratamiento
        ttk.Label(form_frame, text="3. Seleccione el Tratamiento:").pack(fill="x", pady=(10, 2))
        self.cmb_tratamiento = ttk.Combobox(form_frame, state="readonly")
        self.cmb_tratamiento.pack(fill="x")

        # Fecha (el widget de calendario se queda igual)
        ttk.Label(form_frame, text="4. Seleccione la Fecha:").pack(fill="x", pady=(10, 2))
        self.ent_fecha = DateEntry(form_frame, bootstyle="info", firstweekday=0, dateformat="%Y-%m-%d")
        self.ent_fecha.pack(fill="x")

        # Botón para buscar horarios
        self.btn_buscar = ttk.Button(form_frame, text="Buscar Horarios Disponibles", command=self._on_buscar, bootstyle="info")
        self.btn_buscar.pack(pady=20, fill="x")

        # --- Columna Derecha: Resultados y Confirmación ---
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

    def _on_buscar(self):
        fecha_str = self.ent_fecha.entry.get().strip()
        pid = self._parse_id_from_combo(self.cmb_paciente.get())
        did = self._parse_id_from_combo(self.cmb_dentista.get())
        tid = self._parse_id_from_combo(self.cmb_tratamiento.get())

        if not (pid and did and tid and fecha_str):
            messagebox.showwarning("Validación", "Seleccione paciente, dentista, tratamiento y fecha.", parent=self)
            return

        # --- INICIO DE LA NUEVA LÓGICA DE VALIDACIÓN ---
        try:
            fecha_seleccionada = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hoy = date.today()
            fecha_minima = hoy + timedelta(days=1)
            fecha_maxima = hoy + timedelta(days=60)

            if not (fecha_minima <= fecha_seleccionada <= fecha_maxima):
                messagebox.showwarning(
                    "Fecha inválida", 
                    f"Por favor, seleccione una fecha entre mañana ({fecha_minima}) y los próximos 60 días ({fecha_maxima}).",
                    parent=self
                )
                return
        except ValueError:
            messagebox.showerror("Error de formato", "La fecha no tiene un formato válido.", parent=self)
            return
        # --- FIN DE LA NUEVA LÓGICA DE VALIDACIÓN ---
            
        try:
            # --- MODIFICACIÓN CLAVE: Pasamos el ID del paciente (pid) ---
            horas = controlador.buscar_horarios_disponibles(fecha_str, did, tid, pid)
            
            for i in self.list_horas.get_children(): self.list_horas.delete(i)

            if not horas:
                self.list_horas.insert("", "end", values=("No hay horarios",))
            else:
                for h in horas: self.list_horas.insert("", "end", values=(h,))
        except Exception as e:
            messagebox.showerror("Error de Búsqueda", str(e), parent=self)

    def _on_confirmar(self):
        # (Este método no necesita cambios, ya funciona correctamente)
        sel = self.list_horas.focus()
        if not sel:
            messagebox.showwarning("Validación", "Seleccione un horario de la lista.", parent=self)
            return
        
        hora = self.list_horas.item(sel)["values"][0]
        if hora == "No hay horarios":
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

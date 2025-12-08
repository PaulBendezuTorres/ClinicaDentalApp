import ttkbootstrap as ttk
from tkinter import messagebox
from logic.sistema import sistema  # <-- NUEVO IMPORT
from ttkbootstrap.widgets import DateEntry
from ttkbootstrap.scrolled import ScrolledFrame
from datetime import date, timedelta, datetime
import threading
import queue

class HorarioCard(ttk.Frame):
    def __init__(self, parent, horario_data, select_callback):
        super().__init__(parent, padding=15, bootstyle="secondary")
        self.horario_data = horario_data
        self.select_callback = select_callback
        
        self.bind("<Button-1>", self._on_select)
        self.columnconfigure(1, weight=1)

        self.lbl_icon = ttk.Label(self, text="🕒", font=("Segoe UI", 20), bootstyle="inverse-secondary")
        self.lbl_icon.grid(row=0, column=0, rowspan=2, padx=(0, 15))
        self.lbl_icon.bind("<Button-1>", self._on_select)

        self.label_hora = ttk.Label(self, text=horario_data['hora'], font=("Segoe UI", 16, "bold"), bootstyle="inverse-secondary")
        self.label_hora.grid(row=0, column=1, sticky="w")
        self.label_hora.bind("<Button-1>", self._on_select)
        
        dia_str = horario_data['dia_semana'].capitalize()
        fecha_fmt = datetime.strptime(horario_data['fecha'], "%Y-%m-%d").strftime("%d/%m/%Y")
        
        self.label_dia_fecha = ttk.Label(self, text=f"{dia_str}  |  {fecha_fmt}", font=("Segoe UI", 10), bootstyle="inverse-secondary")
        self.label_dia_fecha.grid(row=1, column=1, sticky="w")
        self.label_dia_fecha.bind("<Button-1>", self._on_select)

    def _on_select(self, event):
        self.select_callback(self)

    def select(self):
        self.config(bootstyle="info")
        for child in self.winfo_children():
            child.config(bootstyle="inverse-info")

    def deselect(self):
        self.config(bootstyle="secondary")
        for child in self.winfo_children():
            child.config(bootstyle="inverse-secondary")


class PaginaAgendarCita(ttk.Frame): 
    def __init__(self, parent, usuario_data=None):
        super().__init__(parent)
        self.usuario_data = usuario_data
        self.cola_resultados = queue.Queue()
        self.selected_horario_card = None
        self._build()
        self._cargar_dropdowns()
        self.after(100, self._procesar_cola)

    def _build(self):
        main_scroll = ScrolledFrame(self, autohide=False)
        main_scroll.pack(fill="both", expand=True)

        header = ttk.Frame(main_scroll, padding=20)
        header.pack(fill="x")
        ttk.Label(header, text="📅 Agendar Nueva Cita", font=("Segoe UI", 24, "bold"), bootstyle="light").pack(side="left")

        body = ttk.Frame(main_scroll, padding=(20, 0, 20, 20))
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=4)
        body.columnconfigure(1, weight=6)

        left_col = ttk.Frame(body, padding=(0, 0, 20, 0))
        left_col.grid(row=0, column=0, sticky="nsew")

        grp_datos = ttk.Labelframe(left_col, text=" 📝 Datos de la Cita ", padding=15, bootstyle="info")
        grp_datos.pack(fill="x", pady=(0, 20))

        self.cmb_paciente = ttk.Combobox(grp_datos, state="readonly")
        self._crear_campo(grp_datos, "👤 Paciente:", self.cmb_paciente)
        self.cmb_dentista = ttk.Combobox(grp_datos, state="readonly")
        self._crear_campo(grp_datos, "👨‍⚕️ Dentista:", self.cmb_dentista)
        self.cmb_tratamiento = ttk.Combobox(grp_datos, state="readonly")
        self._crear_campo(grp_datos, "🦷 Tratamiento:", self.cmb_tratamiento)

        grp_busq = ttk.Labelframe(left_col, text=" 🔎 Criterios de Búsqueda ", padding=15, bootstyle="primary")
        grp_busq.pack(fill="x", pady=(0, 20))

        ttk.Label(grp_busq, text="Fecha Específica:", font=("Segoe UI", 10)).pack(anchor="w")
        self.ent_fecha = DateEntry(grp_busq, bootstyle="primary", firstweekday=0, dateformat="%Y-%m-%d")
        self.ent_fecha.pack(fill="x", pady=(5, 15))

        ttk.Label(grp_busq, text="O busque por disponibilidad:", font=("Segoe UI", 10, "bold"), bootstyle="primary").pack(anchor="w", pady=(0, 10))
        
        self.cmb_turno = ttk.Combobox(grp_busq, values=["Cualquiera", "Mañana", "Tarde"], state="readonly")
        self.cmb_turno.set("Cualquiera")
        self._crear_campo(grp_busq, "Turno Preferido:", self.cmb_turno)

        ttk.Label(grp_busq, text="Días Preferidos:", font=("Segoe UI", 10)).pack(anchor="w", pady=(5, 2))
        dias_frame = ttk.Frame(grp_busq)
        dias_frame.pack(fill="x")
        
        self.check_dias_vars = {}
        dias_corto = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab"]
        dias_full = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado"]
        for i, (nombre, key) in enumerate(zip(dias_corto, dias_full)):
            var = ttk.BooleanVar()
            chk = ttk.Checkbutton(dias_frame, text=nombre, variable=var, bootstyle="round-toggle")
            chk.grid(row=i//3, column=i%3, padx=5, pady=5, sticky="w")
            self.check_dias_vars[key] = var

        btn_frame = ttk.Frame(grp_busq)
        btn_frame.pack(fill="x", pady=15)
        ttk.Button(btn_frame, text="Buscar en Fecha", command=self._on_buscar_fecha, bootstyle="outline-primary").pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttk.Button(btn_frame, text="Buscar Próxima", command=self._on_buscar_proxima, bootstyle="primary").pack(side="left", fill="x", expand=True, padx=(5, 0))

        right_col = ttk.Labelframe(body, text=" Resultados Disponibles ", padding=15, bootstyle="success")
        right_col.grid(row=0, column=1, sticky="nsew")

        self.horarios_scroll = ScrolledFrame(right_col, autohide=True, height=400) 
        self.horarios_scroll.pack(fill="both", expand=True)
        self.horarios_container = ttk.Frame(self.horarios_scroll)
        self.horarios_container.pack(fill="x", expand=True)

        footer_res = ttk.Frame(right_col, padding=(0, 15, 0, 0))
        footer_res.pack(fill="x", side="bottom")
        ttk.Label(footer_res, text="🏥 Asignar Consultorio:", font=("Segoe UI", 10)).pack(anchor="w")
        self.cmb_consultorio = ttk.Combobox(footer_res, state="readonly")
        self.cmb_consultorio.pack(fill="x", pady=5)
        self.btn_confirmar = ttk.Button(footer_res, text="CONFIRMAR CITA", command=self._on_confirmar, bootstyle="success")
        self.btn_confirmar.pack(fill="x", pady=(10, 0))

    def _crear_campo(self, parent, label_text, widget):
        ttk.Label(parent, text=label_text, font=("Segoe UI", 10)).pack(anchor="w")
        widget.pack(fill="x", pady=(2, 10))

    def _limpiar_y_cargar(self):
        for widget in self.horarios_container.winfo_children(): widget.destroy()
        ttk.Label(self.horarios_container, text="⏳ Buscando horarios...", font=("Segoe UI", 12), bootstyle="info").pack(pady=20)
        self.update_idletasks()

    def _procesar_cola(self):
        try:
            resultado = self.cola_resultados.get_nowait()
            for widget in self.horarios_container.winfo_children(): widget.destroy()
            self.selected_horario_card = None

            if isinstance(resultado, Exception):
                ttk.Label(self.horarios_container, text=f"Error: {resultado}", bootstyle="danger").pack(pady=20)
            elif not resultado:
                ttk.Label(self.horarios_container, text="❌ No se encontraron horarios disponibles.\nIntente con otros filtros.", font=("Segoe UI", 12), justify="center").pack(pady=50)
            else:
                ttk.Label(self.horarios_container, text=f"✅ Se encontraron {len(resultado)} opciones:", font=("Segoe UI", 10), bootstyle="success").pack(anchor="w", pady=(0, 10))
                for horario_data in resultado:
                    card = HorarioCard(self.horarios_container, horario_data, self._on_horario_select)
                    card.pack(fill="x", padx=5, pady=5)
        except queue.Empty:
            pass
        finally:
            self.after(100, self._procesar_cola)
            
    def _on_horario_select(self, selected_card: HorarioCard):
        if self.selected_horario_card:
            self.selected_horario_card.deselect()
        self.selected_horario_card = selected_card
        self.selected_horario_card.select()

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
            messagebox.showwarning("Validación", "Complete Paciente, Dentista, Tratamiento y Fecha.", parent=self)
            for widget in self.horarios_container.winfo_children(): widget.destroy()
            return
        threading.Thread(target=self._worker_buscar_fecha, args=(data,), daemon=True).start()

    def _worker_buscar_fecha(self, data):
        try:
            # USAMOS EL SERVICIO DE CITAS
            self.cola_resultados.put(sistema.cita.buscar_horarios(
                data["fecha_str"], data["did"], data["tid"], data["pid"], data["turno"], data["dias"]
            ))
        except Exception as e: self.cola_resultados.put(e)

    def _on_buscar_proxima(self):
        self._limpiar_y_cargar()
        data = self._get_form_data()
        if not (data["pid"] and data["did"] and data["tid"]):
            messagebox.showwarning("Validación", "Seleccione Paciente, Dentista y Tratamiento.", parent=self)
            for widget in self.horarios_container.winfo_children(): widget.destroy()
            return
        if not data["dias"]:
            messagebox.showwarning("Validación", "Seleccione al menos un día de preferencia.", parent=self)
            for widget in self.horarios_container.winfo_children(): widget.destroy()
            return
        threading.Thread(target=self._worker_buscar_proxima, args=(data,), daemon=True).start()

    def _worker_buscar_proxima(self, data):
        try:
            # USAMOS EL SERVICIO DE CITAS
            self.cola_resultados.put(sistema.cita.encontrar_proxima(
                data["did"], data["tid"], data["pid"], data["turno"], data["dias"]
            ))
        except Exception as e: self.cola_resultados.put(e)

    def _on_confirmar(self):
        if not self.selected_horario_card:
            messagebox.showwarning("Atención", "Seleccione un horario.", parent=self)
            return
        sel = self.selected_horario_card.horario_data
        cid = self._parse_id_from_combo(self.cmb_consultorio.get())
        if not cid:
            messagebox.showwarning("Atención", "Asigne un Consultorio.", parent=self)
            return
        pid = self._parse_id_from_combo(self.cmb_paciente.get())
        did = self._parse_id_from_combo(self.cmb_dentista.get())
        tid = self._parse_id_from_combo(self.cmb_tratamiento.get())
        
        try:
            # USAMOS EL SERVICIO DE CITAS
            new_id = sistema.cita.confirmar_cita({
                "paciente_id": pid, "dentista_id": did, "consultorio_id": cid,
                "tratamiento_id": tid, "fecha": sel['fecha'], "hora_inicio": sel['hora']
            })
            messagebox.showinfo("¡Cita Agendada!", f"Cita registrada. ID: {new_id}", parent=self)
            for widget in self.horarios_container.winfo_children(): widget.destroy()
            self.selected_horario_card = None
        except Exception as e: messagebox.showerror("Error al Guardar", str(e), parent=self)

    def _cargar_dropdowns(self):
        # USAMOS LOS SERVICIOS DE CADA ENTIDAD
        self.cmb_paciente["values"] = [f'{p["id"]} - {p["nombre"]}' for p in sistema.paciente.obtener_todos()]
        self.cmb_dentista["values"] = [f'{d["id"]} - {d["nombre"]} ({d["especialidad"]})' for d in sistema.dentista.obtener_todos()]
        self.cmb_tratamiento["values"] = [f'{t["id"]} - {t["nombre"]} ({t["duracion_minutos"]} min)' for t in sistema.tratamiento.obtener_todos()]
        self.cmb_consultorio["values"] = [f'{c["id"]} - {c["nombre_sala"]}{" *" if int(c["equipo_especial"])==1 else ""}' for c in sistema.consultorio.obtener_todos()]

    def _parse_id_from_combo(self, combo_text: str) -> int:
        try: return int(combo_text.split(" - ")[0])
        except (ValueError, IndexError): return 0
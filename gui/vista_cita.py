import tkinter as tk
# Cambia esto: from tkinter import ttk, messagebox
import ttkbootstrap as ttk # <-- CAMBIO AQUÍ
from tkinter import messagebox
from logic import controlador

class VentanaAgendarCita(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Agendar Cita")
        self.geometry("720x520")
        self._build()
        self._cargar_dropdowns()

    def _build(self):
        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Paciente:").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.cmb_paciente = ttk.Combobox(frm, state="readonly", width=40)
        self.cmb_paciente.grid(row=0, column=1, columnspan=3, sticky=tk.W)

        ttk.Label(frm, text="Dentista:").grid(row=1, column=0, sticky=tk.W, pady=4)
        self.cmb_dentista = ttk.Combobox(frm, state="readonly", width=40)
        self.cmb_dentista.grid(row=1, column=1, columnspan=3, sticky=tk.W)

        ttk.Label(frm, text="Tratamiento:").grid(row=2, column=0, sticky=tk.W, pady=4)
        self.cmb_tratamiento = ttk.Combobox(frm, state="readonly", width=40)
        self.cmb_tratamiento.grid(row=2, column=1, columnspan=3, sticky=tk.W)

        ttk.Label(frm, text="Consultorio:").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.cmb_consultorio = ttk.Combobox(frm, state="readonly", width=40)
        self.cmb_consultorio.grid(row=3, column=1, columnspan=3, sticky=tk.W)

        ttk.Label(frm, text="Fecha (YYYY-MM-DD):").grid(row=4, column=0, sticky=tk.W, pady=4)
        self.ent_fecha = ttk.Entry(frm, width=20)
        self.ent_fecha.grid(row=4, column=1, sticky=tk.W)

        self.btn_buscar = ttk.Button(frm, text="Buscar Horarios", command=self._on_buscar)
        self.btn_buscar.grid(row=4, column=3, sticky=tk.E)

        ttk.Label(frm, text="Horarios Disponibles:").grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(12, 6))
        self.list_horas = tk.Listbox(frm, height=12, width=30)
        self.list_horas.grid(row=6, column=0, columnspan=2, sticky=tk.W)

        self.btn_confirmar = ttk.Button(frm, text="Confirmar Cita", command=self._on_confirmar)
        self.btn_confirmar.grid(row=7, column=0, sticky=tk.W, pady=12)

        frm.columnconfigure(2, weight=1)

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
        try:
            return int(combo_text.split(" - ")[0])
        except Exception:
            return 0

    def _on_buscar(self):
        fecha = self.ent_fecha.get().strip()
        if not fecha:
            messagebox.showwarning("Validación", "Ingrese la fecha en formato YYYY-MM-DD.")
            return

        pid = self._parse_id_from_combo(self.cmb_paciente.get())
        did = self._parse_id_from_combo(self.cmb_dentista.get())
        tid = self._parse_id_from_combo(self.cmb_tratamiento.get())

        if not (pid and did and tid):
            messagebox.showwarning("Validación", "Seleccione paciente, dentista y tratamiento.")
            return

        try:
            horas = controlador.buscar_horarios_disponibles(fecha, did, tid)
            self.list_horas.delete(0, tk.END)
            if not horas:
                self.list_horas.insert(tk.END, "No hay horarios disponibles.")
            else:
                for h in horas:
                    self.list_horas.insert(tk.END, h)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_confirmar(self):
        fecha = self.ent_fecha.get().strip()
        sel = self.list_horas.curselection()
        if not sel:
            messagebox.showwarning("Validación", "Seleccione un horario de la lista.")
            return

        pid = self._parse_id_from_combo(self.cmb_paciente.get())
        did = self._parse_id_from_combo(self.cmb_dentista.get())
        tid = self._parse_id_from_combo(self.cmb_tratamiento.get())
        cid = self._parse_id_from_combo(self.cmb_consultorio.get())
        hora = self.list_horas.get(sel[0])

        if not (pid and did and tid and cid and fecha and hora):
            messagebox.showwarning("Validación", "Complete todos los campos.")
            return

        try:
            new_id = controlador.confirmar_cita({
                "paciente_id": pid,
                "dentista_id": did,
                "consultorio_id": cid,
                "tratamiento_id": tid,
                "fecha": fecha,
                "hora_inicio": hora
            })
            messagebox.showinfo("Éxito", f"Cita creada con ID {new_id}.")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))

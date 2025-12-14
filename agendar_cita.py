import tkinter as tk
from tkinter import ttk, messagebox
import csv, os, re
from datetime import datetime, timedelta

RUTA_CITAS = os.path.join("datos", "citas.csv")

HEADER_CITAS = [
    "id_cita",
    "id_doctor",
    "seguro_social",
    "fecha",
    "hora",
    "especialidad",
    "hospital",
    "estatus"
]

HORA_INICIO = 9
HORA_FIN = 17
INTERVALO_MIN = 30

def leer_header_existente():
    if not os.path.exists(RUTA_CITAS) or os.path.getsize(RUTA_CITAS) == 0:
        return HEADER_CITAS

    with open(RUTA_CITAS, "r", encoding="utf-8") as f:
        primera = f.readline().strip()
        partes = [p.strip() for p in primera.split(",")]
        if "id_cita" in partes and "fecha" in partes and "hora" in partes:
            return partes

    return HEADER_CITAS


def generar_nuevo_id():
    if not os.path.exists(RUTA_CITAS):
        return "C0001"

    with open(RUTA_CITAS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        ids = []
        for row in reader:
            cid = row.get("id_cita", "")
            m = re.search(r"\d+", cid)
            if m:
                ids.append(int(m.group()))
        if not ids:
            return "C0001"

        nuevo = max(ids) + 1
        return f"C{str(nuevo).zfill(4)}"


def generar_slots():
    slots = []
    t = datetime(2000, 1, 1, HORA_INICIO, 0)
    fin = datetime(2000, 1, 1, HORA_FIN, 0)
    while t < fin:
        slots.append(t.strftime("%H:%M"))
        t += timedelta(minutes=INTERVALO_MIN)
    return slots


def citas_ocupadas(id_doctor, fecha):
    ocupadas = set()
    if not os.path.exists(RUTA_CITAS):
        return ocupadas

    with open(RUTA_CITAS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("id_doctor") == id_doctor and row.get("fecha") == fecha:
                ocupadas.add(row.get("hora"))
    return ocupadas


def horas_disponibles(id_doctor, fecha):
    slots = generar_slots()
    ocupadas = citas_ocupadas(id_doctor, fecha)
    return [h for h in slots if h not in ocupadas]


def fecha_es_valida(fecha_str):
    try:
        d = datetime.strptime(fecha_str, "%d/%m/%Y").date()
        return d >= datetime.now().date()
    except:
        return False


def abrir_agendar_cita(root, seguro_social, id_doctor, nombre_doctor,
                       especialidad, hospital):

    win = tk.Toplevel(root)
    win.title("Agendar cita")
    win.geometry("450x520")
    win.resizable(False, False)

    tk.Label(win, text="Agendar cita", font=("Arial", 16, "bold")).pack(pady=10)
    tk.Label(win, text=f"Doctor: {nombre_doctor}").pack(pady=3)
    tk.Label(win, text=f"Especialidad: {especialidad}").pack(pady=3)
    tk.Label(win, text=f"Hospital: {hospital}").pack(pady=3)

    frame_fecha = tk.Frame(win)
    frame_fecha.pack(pady=15)

    tk.Label(frame_fecha, text="Fecha:").grid(row=0, column=0, padx=5)

    fecha_var = tk.StringVar()

    try:
        from tkcalendar import DateEntry
    except Exception:
        messagebox.showerror(
            "Falta tkcalendar",
            "No tienes instalada la librería tkcalendar.\n"
            "Instálala con:\n\npip install tkcalendar"
        )
        win.destroy()
        return

    fecha_picker = DateEntry(
        frame_fecha,
        textvariable=fecha_var,
        date_pattern="dd/mm/yyyy",
        width=12
    )
    fecha_picker.grid(row=0, column=1)

    frame_hora = tk.Frame(win)
    frame_hora.pack(pady=10)

    tk.Label(frame_hora, text="Hora disponible:").grid(row=0, column=0, padx=5)

    hora_cmb = ttk.Combobox(frame_hora, values=[], state="readonly", width=12)
    hora_cmb.grid(row=0, column=1, padx=5)

    def refrescar_horas(*_):
        fecha = fecha_var.get().strip()

        if not fecha_es_valida(fecha):
            hora_cmb["values"] = []
            hora_cmb.set("")
            messagebox.showwarning("Fecha inválida", "Elige una fecha válida (hoy o después).")
            return

        disponibles = horas_disponibles(id_doctor, fecha)
        hora_cmb["values"] = disponibles

        if disponibles:
            hora_cmb.set(disponibles[0])
        else:
            hora_cmb.set("")
            messagebox.showinfo("Sin horarios", "Ese día ya no tiene horarios libres.")

    fecha_picker.bind("<<DateEntrySelected>>", refrescar_horas)
    refrescar_horas()
    def guardar_cita():
        fecha = fecha_var.get().strip()
        hora = hora_cmb.get().strip()

        if not fecha or not hora:
            messagebox.showwarning("Aviso", "Selecciona fecha y hora.")
            return

        if not fecha_es_valida(fecha):
            messagebox.showwarning("Fecha inválida", "No puedes agendar en fechas pasadas.")
            return

        if hora in citas_ocupadas(id_doctor, fecha):
            messagebox.showerror("Ocupado", "Ese horario ya fue tomado. Elige otro.")
            refrescar_horas()
            return

        header = leer_header_existente()
        nuevo_id = generar_nuevo_id()

        nueva_cita = {
            "id_cita": nuevo_id,
            "id_doctor": id_doctor,
            "seguro_social": seguro_social,
            "fecha": fecha,
            "hora": hora,
            "especialidad": especialidad,
            "hospital": hospital,
            "estatus": "ACTIVA"
        }

        escribir_header = (not os.path.exists(RUTA_CITAS)) or os.path.getsize(RUTA_CITAS) == 0

        with open(RUTA_CITAS, "a", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=header)
            if escribir_header:
                writer.writeheader()
            writer.writerow(nueva_cita)

        messagebox.showinfo("Éxito", "Cita registrada correctamente.")
        win.destroy()

    tk.Button(
        win,
        text="Guardar cita",
        width=18,
        height=1,
        bg="#00A0D6",
        fg="white",
        command=guardar_cita
    ).pack(pady=25)

    return win

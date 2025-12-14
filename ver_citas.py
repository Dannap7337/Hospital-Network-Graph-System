import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

RUTA_CITAS = os.path.join("datos", "citas.csv")
RUTA_DOCTORES = os.path.join("datos", "doctores_hospitales_con_id.csv")

COLUMNAS_SALIDA = ("id_cita", "doctor", "especialidad", "hospital", "fecha", "hora", "estatus")

def _cargar_doctores():
    if not os.path.exists(RUTA_DOCTORES):
        return {}

    doctores = {}
    with open(RUTA_DOCTORES, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            did = (row.get("id_doctor") or "").strip()
            if did:
                doctores[did] = {
                    "nombre": (row.get("nombre") or "").strip(),
                    "especialidad": (row.get("especialidad") or "").strip(),
                    "hospital": (row.get("hospital") or "").strip(),
                }
    return doctores


def _leer_citas():
    if not os.path.exists(RUTA_CITAS):
        return [], []

    with open(RUTA_CITAS, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        citas = []
        for row in reader:
            citas.append(row)
    return citas, fieldnames


def _guardar_citas(citas, fieldnames):
    if "estatus" not in fieldnames:
        fieldnames.append("estatus")

    os.makedirs(os.path.dirname(RUTA_CITAS), exist_ok=True)
    with open(RUTA_CITAS, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for c in citas:
            # Completar estatus si falta
            if "estatus" not in c or not c["estatus"]:
                c["estatus"] = "ACTIVA"
            writer.writerow(c)


def abrir_ver_citas(parent, seguro_social, titulo_extra=""):
    doctores = _cargar_doctores()
    citas, fieldnames = _leer_citas()

    ss = str(seguro_social).strip()
    mis_citas = [c for c in citas if str(c.get("seguro_social", "")).strip() == ss]

    win = tk.Toplevel(parent)
    win.title("Mis citas" + (f" - {titulo_extra}" if titulo_extra else ""))
    win.geometry("900x450")
    win.resizable(True, True)

    tk.Label(win, text="Historial de citas", font=("Arial", 16, "bold")).pack(pady=8)

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True, padx=10, pady=5)

    tree = ttk.Treeview(frame, columns=COLUMNAS_SALIDA, show="headings", height=12)
    tree.pack(side="left", fill="both", expand=True)

    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    sb.pack(side="right", fill="y")
    tree.configure(yscrollcommand=sb.set)

    headers = {
        "id_cita": "ID Cita",
        "doctor": "Doctor(a)",
        "especialidad": "Especialidad",
        "hospital": "Hospital",
        "fecha": "Fecha",
        "hora": "Hora",
        "estatus": "Estatus",
    }

    widths = {
        "id_cita": 80,
        "doctor": 240,
        "especialidad": 200,
        "hospital": 200,
        "fecha": 90,
        "hora": 70,
        "estatus": 90,
    }

    for col in COLUMNAS_SALIDA:
        tree.heading(col, text=headers[col])
        tree.column(col, width=widths[col], anchor="center")

    def refrescar_tabla():
        tree.delete(*tree.get_children())
        if not mis_citas:
            return
        for c in mis_citas:
            did = (c.get("id_doctor") or "").strip()
            info_doc = doctores.get(did, {})
            nombre_doc = info_doc.get("nombre") or did or "Desconocido"
            esp = (c.get("especialidad") or info_doc.get("especialidad") or "").strip()
            hosp = (c.get("hospital") or info_doc.get("hospital") or "").strip()
            estatus = (c.get("estatus") or "ACTIVA").strip()

            tree.insert(
                "", "end",
                values=(
                    c.get("id_cita", ""),
                    nombre_doc,
                    esp,
                    hosp,
                    c.get("fecha", ""),
                    c.get("hora", ""),
                    estatus
                )
            )

    refrescar_tabla()

    botones = tk.Frame(win)
    botones.pack(pady=6)

    def cancelar_seleccionada():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona una cita de la tabla.")
            return

        vals = tree.item(sel[0], "values")
        id_cita = vals[0]
        estatus_actual = vals[6]

        if estatus_actual.upper() != "ACTIVA":
            messagebox.showinfo("No permitido", "Solo puedes cancelar citas ACTIVAS.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Cancelar la cita {id_cita}?"):
            return

        for c in citas:
            if str(c.get("id_cita", "")).strip() == str(id_cita).strip():
                c["estatus"] = "CANCELADA"
                break

        _guardar_citas(citas, fieldnames)

        nonlocal_mis = []
        for c in citas:
            if str(c.get("seguro_social", "")).strip() == ss:
                nonlocal_mis.append(c)
        mis_citas[:] = nonlocal_mis

        refrescar_tabla()
        messagebox.showinfo("Listo", "Cita cancelada.")

    def ver_detalle():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona una cita.")
            return
        vals = tree.item(sel[0], "values")
        detalle = (
            f"ID Cita: {vals[0]}\n"
            f"Doctor(a): {vals[1]}\n"
            f"Especialidad: {vals[2]}\n"
            f"Hospital: {vals[3]}\n"
            f"Fecha: {vals[4]}\n"
            f"Hora: {vals[5]}\n"
            f"Estatus: {vals[6]}"
        )
        messagebox.showinfo("Detalle de cita", detalle)

    ttk.Button(botones, text="Ver detalle", command=ver_detalle).grid(row=0, column=0, padx=8)
    ttk.Button(botones, text="Cancelar cita", command=cancelar_seleccionada).grid(row=0, column=1, padx=8)
    ttk.Button(botones, text="Cerrar", command=win.destroy).grid(row=0, column=2, padx=8)

    if not mis_citas:
        tk.Label(win, text="No tienes citas registradas.", fg="#555").pack(pady=8)

    return win

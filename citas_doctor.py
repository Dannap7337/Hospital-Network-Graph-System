import tkinter as tk
from tkinter import ttk, messagebox
import csv, os

BASE_DIR = os.path.dirname(__file__)
RUTA_CITAS = os.path.join(BASE_DIR, "datos", "citas.csv")
RUTA_PACIENTES = os.path.join(BASE_DIR, "datos", "pacientes.csv")

COLUMNAS = ("id_cita", "paciente", "nss", "especialidad", "hospital", "fecha", "hora", "estatus")


def _leer_csv(ruta):
    if not os.path.exists(ruta):
        return [], []
    with open(ruta, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r), (r.fieldnames or [])


def _guardar_csv(ruta, datos, fieldnames):
    if "estatus" not in fieldnames:
        fieldnames.append("estatus")
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for d in datos:
            if not d.get("estatus"):
                d["estatus"] = "ACTIVA"
            w.writerow(d)


def _mapa_pacientes():
    pacientes, _ = _leer_csv(RUTA_PACIENTES)
    mapa = {}
    for p in pacientes:
        nss = str(p.get("seguro_social", "")).strip()
        nombre = " ".join([
            p.get("nombre", ""),
            p.get("apellido_paterno", ""),
            p.get("apellido_materno", "")
        ]).strip()
        if nss:
            mapa[nss] = nombre
    return mapa


def abrir_citas_doctor(parent, id_doctor, nombre_doctor=""):
    citas, fieldnames = _leer_csv(RUTA_CITAS)
    mapa_p = _mapa_pacientes()

    did = str(id_doctor).strip()
    mis_citas = [c for c in citas if str(c.get("id_doctor", "")).strip() == did]

    win = tk.Toplevel(parent)
    win.title(f"Mis citas - Dr(a). {nombre_doctor or did}")
    win.geometry("980x480")
    win.resizable(True, True)

    tk.Label(win, text="Mis citas", font=("Arial", 16, "bold")).pack(pady=8)

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True, padx=10, pady=5)

    tree = ttk.Treeview(frame, columns=COLUMNAS, show="headings", height=12)
    tree.pack(side="left", fill="both", expand=True)

    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    sb.pack(side="right", fill="y")
    tree.configure(yscrollcommand=sb.set)

    headers = {
        "id_cita": "ID",
        "paciente": "Paciente",
        "nss": "NSS",
        "especialidad": "Especialidad",
        "hospital": "Hospital",
        "fecha": "Fecha",
        "hora": "Hora",
        "estatus": "Estatus",
    }
    widths = {
        "id_cita": 70,
        "paciente": 220,
        "nss": 120,
        "especialidad": 180,
        "hospital": 200,
        "fecha": 90,
        "hora": 70,
        "estatus": 110,
    }

    for col in COLUMNAS:
        tree.heading(col, text=headers[col])
        tree.column(col, width=widths[col], anchor="center")

    def refrescar():
        tree.delete(*tree.get_children())
        for c in mis_citas:
            nss = str(c.get("seguro_social", "")).strip()
            paciente_nombre = mapa_p.get(nss, "Desconocido")
            tree.insert("", "end", values=(
                c.get("id_cita", ""),
                paciente_nombre,
                nss,
                c.get("especialidad", ""),
                c.get("hospital", ""),
                c.get("fecha", ""),
                c.get("hora", ""),
                (c.get("estatus") or "ACTIVA").strip()
            ))

    def marcar_atendida():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona una cita.")
            return
        vals = tree.item(sel[0], "values")
        id_cita = vals[0]
        estatus = vals[7].upper()

        if estatus != "ACTIVA":
            messagebox.showinfo("No permitido", "Solo puedes atender citas ACTIVAS.")
            return

        for c in citas:
            if str(c.get("id_cita", "")).strip() == str(id_cita).strip():
                c["estatus"] = "ATENDIDA"
                break

        _guardar_csv(RUTA_CITAS, citas, fieldnames)
        mis_citas[:] = [c for c in citas if str(c.get("id_doctor", "")).strip() == did]
        refrescar()
        messagebox.showinfo("Listo", "Cita marcada como ATENDIDA.")

    def cancelar_cita():
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona una cita.")
            return
        vals = tree.item(sel[0], "values")
        id_cita = vals[0]
        estatus = vals[7].upper()

        if estatus != "ACTIVA":
            messagebox.showinfo("No permitido", "Solo puedes cancelar citas ACTIVAS.")
            return

        if not messagebox.askyesno("Confirmar", f"¿Cancelar la cita {id_cita}?"):
            return

        for c in citas:
            if str(c.get("id_cita", "")).strip() == str(id_cita).strip():
                c["estatus"] = "CANCELADA"
                break

        _guardar_csv(RUTA_CITAS, citas, fieldnames)
        mis_citas[:] = [c for c in citas if str(c.get("id_doctor", "")).strip() == did]
        refrescar()
        messagebox.showinfo("Listo", "Cita cancelada.")

    refrescar()

    def accion_refrescar():
        mis_citas[:] = [c for c in citas if str(c.get("id_doctor", "")).strip() == did]
        refrescar()


    botones = tk.Frame(win)
    botones.pack(pady=8)

    ttk.Button(botones, text="Refrescar", command=accion_refrescar).grid(row=0, column=0, padx=6)
    ttk.Button(botones, text="Marcar ATENDIDA", command=marcar_atendida).grid(row=0, column=1, padx=6)
    ttk.Button(botones, text="Cancelar cita", command=cancelar_cita).grid(row=0, column=2, padx=6)
    ttk.Button(botones, text="Cerrar", command=win.destroy).grid(row=0, column=3, padx=6)


    if not mis_citas:
        tk.Label(win, text="No tienes citas registradas.", fg="#555").pack(pady=6)

    return win

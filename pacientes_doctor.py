import tkinter as tk
from tkinter import ttk
import csv, os

BASE_DIR = os.path.dirname(__file__)
RUTA_CITAS = os.path.join(BASE_DIR, "datos", "citas.csv")
RUTA_PACIENTES = os.path.join(BASE_DIR, "datos", "pacientes.csv")

def _leer_csv(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def abrir_pacientes_atendidos(parent, id_doctor, nombre_doctor=""):
    citas = _leer_csv(RUTA_CITAS)
    pacientes = _leer_csv(RUTA_PACIENTES)

    did = str(id_doctor).strip()

    nss_del_doc = {
        str(c.get("seguro_social", "")).strip()
        for c in citas
        if str(c.get("id_doctor", "")).strip() == did
    }
    nss_del_doc.discard("")

    info_por_nss = {nss: {"citas": 0, "ultima_fecha": "", "ultimo_estatus": ""} for nss in nss_del_doc}

    for c in citas:
        if str(c.get("id_doctor", "")).strip() != did:
            continue

        nss = str(c.get("seguro_social", "")).strip()
        if nss in info_por_nss:
            info_por_nss[nss]["citas"] += 1
            fecha = (c.get("fecha") or "").strip()

            if fecha and fecha >= info_por_nss[nss]["ultima_fecha"]:
                info_por_nss[nss]["ultima_fecha"] = fecha
                info_por_nss[nss]["ultimo_estatus"] = (c.get("estatus") or "ACTIVA").strip()

    registros = []
    for p in pacientes:
        nss = str(p.get("seguro_social", "")).strip()
        if nss not in nss_del_doc:
            continue

        nombre = " ".join([
            p.get("nombre", ""),
            p.get("apellido_paterno", ""),
            p.get("apellido_materno", "")
        ]).strip()

        meta = info_por_nss.get(nss, {})

        registros.append({
            "paciente": nombre,
            "nss": nss,
            "num_citas": meta.get("citas", 0),
            "ultima_fecha": meta.get("ultima_fecha", ""),
            "estatus": meta.get("ultimo_estatus", "")
        })

    registros.sort(key=lambda r: r["paciente"])

    # VENTANA
    win = tk.Toplevel(parent)
    win.title(f"Pacientes atendidos - Dr(a). {nombre_doctor or did}")
    win.geometry("800x450")
    win.resizable(True, True)

    tk.Label(win, text="Pacientes atendidos", font=("Arial", 15, "bold")).pack(pady=8)

    frame = tk.Frame(win)
    frame.pack(fill="both", expand=True, padx=10, pady=5)

    cols = ("paciente", "nss", "num_citas", "ultima_fecha", "estatus")

    tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
    tree.pack(side="left", fill="both", expand=True)

    sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    sb.pack(side="right", fill="y")
    tree.configure(yscrollcommand=sb.set)

    headers = {
        "paciente": "Paciente",
        "nss": "NSS",
        "num_citas": "# Citas",
        "ultima_fecha": "Última cita",
        "estatus": "Último estatus"
    }

    widths = {
        "paciente": 260,
        "nss": 140,
        "num_citas": 80,
        "ultima_fecha": 100,
        "estatus": 120
    }

    for c in cols:
        tree.heading(c, text=headers[c])
        tree.column(c, width=widths[c], anchor="center")

    for r in registros:
        tree.insert("", "end", values=(
            r["paciente"],
            r["nss"],
            r["num_citas"],
            r["ultima_fecha"],
            r["estatus"]
        ))

    ttk.Button(win, text="Cerrar", command=win.destroy).pack(pady=8)

    if not registros:
        tk.Label(win, text="Aún no tienes pacientes con cita.", fg="#555").pack(pady=5)

    return win
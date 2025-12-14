# hospital_cercano.py
import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from math import radians, sin, cos, sqrt, atan2
import unicodedata
import re

from utils import cargar_grafo_hospitales, dijkstra
RUTA_PACIENTES = os.path.join("datos", "pacientes.csv")
RUTA_DOCTORES = os.path.join("datos", "doctores_hospitales_con_id.csv")


def _normalizar_nss(x):
    s = str(x).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s

def _norm_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", " ", s)
    return s

def _split_especialidades(campo: str):
    if not campo:
        return []
    partes = re.split(r"[,;/|]+", campo)
    tokens = []
    for p in partes:
        t = p.strip()
        if t:
            tokens.append(t)
    return tokens

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def cargar_paciente_por_nss(seguro_social):
    if not os.path.exists(RUTA_PACIENTES):
        return None

    nss = _normalizar_nss(seguro_social)
    with open(RUTA_PACIENTES, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            val = _normalizar_nss(row.get("seguro_social", row.get("NSS", "")))
            if val == nss:
                return row
    return None

def cargar_doctores():
    if not os.path.exists(RUTA_DOCTORES):
        return []
    with open(RUTA_DOCTORES, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def obtener_lista_especialidades(doctores):
    tokens_norm = {}
    for d in doctores:
        esp_raw = d.get("especialidad", "")
        for tok in _split_especialidades(esp_raw):
            n = _norm_text(tok)
            if n and n not in tokens_norm:
                tokens_norm[n] = tok.strip()
    return sorted(tokens_norm.values(), key=lambda x: _norm_text(x))

def hospitales_por_especialidad(doctores, especialidad_obj):
    
    objetivo_norm = _norm_text(especialidad_obj)

    acumulado = {}
    for row in doctores:
        hosp = (row.get("hospital") or "Desconocido").strip()
        esp_raw = row.get("especialidad", "")

        tokens = [_norm_text(t) for t in _split_especialidades(esp_raw)]
        if objetivo_norm not in tokens:
            continue

        try:
            lat = float(row.get("latitud"))
            lon = float(row.get("longitud"))
        except (TypeError, ValueError):
            continue

        if hosp not in acumulado:
            acumulado[hosp] = [0.0, 0.0, 0]
        acumulado[hosp][0] += lat
        acumulado[hosp][1] += lon
        acumulado[hosp][2] += 1

    hospitales = {}
    for hosp, (s_lat, s_lon, c) in acumulado.items():
        if c > 0:
            hospitales[hosp] = {"lat_avg": s_lat / c,
                "lon_avg": s_lon / c,
                "count": c}
    return hospitales


def abrir_hospital_cercano(parent, seguro_social):
    paciente = cargar_paciente_por_nss(seguro_social)
    if not paciente:
        messagebox.showerror("Error", "No se encontró al paciente en pacientes.csv")
        return None

    try:
        lat_p = float(paciente.get("latitud"))
        lon_p = float(paciente.get("longitud"))
    except (TypeError, ValueError):
        messagebox.showerror(
            "Sin ubicación",
            "El paciente no tiene latitud/longitud válidas.\n"
            "Regístralas primero en pacientes.csv."
        )
        return None

    doctores = cargar_doctores()
    if not doctores:
        messagebox.showerror("Error", "No se pudieron cargar doctores.")
        return None

    especialidades = obtener_lista_especialidades(doctores)
    if not especialidades:
        messagebox.showerror("Error", "No se encontraron especialidades.")
        return None

    win = tk.Toplevel(parent)
    win.title("Hospital más cercano por especialidad")
    win.geometry("860x560")
    win.resizable(False, False)

    nombre_p = f"{paciente.get('nombre','')} {paciente.get('apellido_paterno','')}".strip()

    tk.Label(win, text="Hospital más cercano por especialidad", font=("Arial", 18, "bold")).pack(pady=10)
    tk.Label(win, text=f"Paciente: {nombre_p}  (NSS: {_normalizar_nss(seguro_social)})").pack()

    frm_sel = tk.Frame(win)
    frm_sel.pack(pady=10)

    tk.Label(frm_sel, text="Especialidad:").grid(row=0, column=0, padx=6)
    cb_esp = ttk.Combobox(frm_sel, values=especialidades, state="readonly", width=40)
    cb_esp.grid(row=0, column=1, padx=6)
    cb_esp.current(0)

    btn_filtrar = ttk.Button(frm_sel, text="Buscar")
    btn_filtrar.grid(row=0, column=2, padx=6)
    frame_top = tk.Frame(win, bd=1, relief="groove", padx=10, pady=8)
    frame_top.pack(padx=12, pady=8, fill="x")

    lbl_hosp = tk.Label(frame_top, text="Más cercano: -", font=("Arial", 14, "bold"))
    lbl_hosp.grid(row=0, column=0, sticky="w")
    lbl_dist = tk.Label(frame_top, text="Distancia aproximada: - km")
    lbl_dist.grid(row=1, column=0, sticky="w")
    lbl_docs = tk.Label(frame_top, text="Doctores de esta especialidad: -")
    lbl_docs.grid(row=2, column=0, sticky="w")

    tk.Label(win, text="Top hospitales cercanos (con la especialidad)").pack(pady=(4, 6))

    cols = ("hospital", "dist_km", "doctores")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=10)
    tree.pack(padx=12, pady=6, fill="both", expand=True)

    tree.heading("hospital", text="Hospital")
    tree.heading("dist_km", text="Distancia (km)")
    tree.heading("doctores", text="# Doctores")

    tree.column("hospital", width=440)
    tree.column("dist_km", width=140, anchor="center")
    tree.column("doctores", width=120, anchor="center")

    def cargar_ranking():
        tree.delete(*tree.get_children())
        esp = cb_esp.get().strip()

        hospitales = hospitales_por_especialidad(doctores, esp)

        if not hospitales:
            lbl_hosp.config(text="Más cercano: -")
            lbl_dist.config(text="Distancia aproximada: - km")
            lbl_docs.config(text="Doctores de esta especialidad: -")
            messagebox.showinfo(
                "Sin resultados",
                f"No hay hospitales con especialidad '{esp}'."
            )
            return

        ranking = []

        origen = None
        min_hav = float('inf')
        for hosp, info in hospitales.items():
            dist_hav = haversine_km(lat_p, lon_p, info["lat_avg"], info["lon_avg"])
            if dist_hav < min_hav:
                min_hav = dist_hav
                origen = hosp

        grafo = cargar_grafo_hospitales()
        origen_norm = _norm_text(origen) if origen else None
        dist_grafo = dijkstra(grafo, origen_norm) if grafo and origen_norm else {}


        for hosp, info in hospitales.items():
            hosp_norm = _norm_text(hosp)
            dist_origen_a_hosp = dist_grafo.get(hosp_norm)

            if dist_origen_a_hosp is not None:
                dist_final = min_hav + dist_origen_a_hosp
            else:
                dist_final = haversine_km(lat_p, lon_p, info["lat_avg"], info["lon_avg"])
            ranking.append((hosp, dist_final, info["count"]))
        ranking.sort(key=lambda x: x[1])

        hosp1, dist1, n1 = ranking[0]
        lbl_hosp.config(text=f"Más cercano: {hosp1}")
        lbl_dist.config(text=f"Distancia aproximada: {dist1:.2f} km")
        lbl_docs.config(text=f"Doctores de esta especialidad: {n1}")

        for hosp, dist, n_docs in ranking[:5]:
            tree.insert("", "end", values=(hosp, f"{dist:.2f}", n_docs))

    btn_filtrar.config(command=cargar_ranking)
    cargar_ranking()

    ttk.Button(win, text="Cerrar", command=win.destroy).pack(pady=8)

    return win
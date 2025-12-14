import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import re
from utils import doctores_ordenados_por_cercania
RUTA_DOCTORES = os.path.join("datos", "doctores_hospitales_con_id.csv")

def obtener_doctores():
    if not os.path.exists(RUTA_DOCTORES):
        messagebox.showerror("Error", f"No se encontró:\n{RUTA_DOCTORES}")
        return []

    doctores = []
    with open(RUTA_DOCTORES, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            doctores.append(row)
    return doctores


def obtener_especialidades():
    doctores = obtener_doctores()
    especialidades_set = set()

    for d in doctores:
        esp_raw = d.get("especialidad", "")
        esp_raw = esp_raw.lower()

        # separa por / , ; o " y "
        partes = re.split(r"\/|,|;| y ", esp_raw)
        partes = [p.strip() for p in partes if p.strip()]

        for p in partes:
            especialidades_set.add(p.title())

    return sorted(especialidades_set)

def doctores_por_especialidad(especialidad):
    doctores = obtener_doctores()
    esp_sel = especialidad.strip().lower()

    filtrados = []
    for d in doctores:
        esp_raw = d.get("especialidad", "").lower()

        partes = re.split(r"\/|,|;| y ", esp_raw)
        partes = [p.strip() for p in partes if p.strip()]

        if esp_sel in partes:
            filtrados.append(d)

    return filtrados

def abrir_buscar_doctores(root, seguro_social):
    win = tk.Toplevel(root)
    win.title("Buscar doctores por especialidad")
    win.geometry("900x600")
    win.resizable(False, False)

    tk.Label(win, text="Buscar doctores", font=("Arial", 18, "bold")).pack(pady=10)

    frame_top = tk.Frame(win)
    frame_top.pack(pady=8)

    tk.Label(frame_top, text="Especialidad:").grid(row=0, column=0, padx=5)

    lista_especialidades = obtener_especialidades()
    if not lista_especialidades:
        lista_especialidades = ["Sin datos"]

    cmb = ttk.Combobox(
        frame_top,
        values=lista_especialidades,
        state="readonly",
        width=45
    )
    cmb.grid(row=0, column=1, padx=5)
    cmb.set(lista_especialidades[0])

    btn_filtrar = tk.Button(frame_top, text="Filtrar", width=10)
    btn_filtrar.grid(row=0, column=2, padx=10)
    columnas = ("id_doctor", "nombre", "especialidad", "hospital", "dist_km")
    tabla = ttk.Treeview(win, columns=columnas, show="headings", height=17)
    tabla.pack(fill="both", expand=True, padx=15, pady=10)

    tabla.heading("id_doctor", text="Id Doctor")
    tabla.heading("nombre", text="Nombre")
    tabla.heading("especialidad", text="Especialidad")
    tabla.heading("hospital", text="Hospital")
    tabla.heading("dist_km", text="Distancia (km)")

    tabla.column("id_doctor", width=0, stretch=False)
    tabla.column("nombre", width=280)
    tabla.column("especialidad", width=260)
    tabla.column("hospital", width=260)
    tabla.column("dist_km", width=110, anchor="center")

    def limpiar_tabla():
        for item in tabla.get_children():
            tabla.delete(item)

    def actualizar_tabla():
        limpiar_tabla()
        esp = cmb.get().strip()

        resultados = doctores_ordenados_por_cercania(seguro_social, esp)

        if not resultados:
            messagebox.showinfo("Sin resultados", f"No hay doctores para '{esp}'.")
            return

        for d in resultados:
            tabla.insert("", "end", values=(
                d.get("id_doctor", ""),
                d.get("nombre", ""),
                d.get("especialidad", ""),
                d.get("hospital", ""),
                f"{d.get('dist_km', 0):.2f} km"
            ))

    btn_filtrar.config(command=actualizar_tabla)
    actualizar_tabla()

    btn_volver = ttk.Button(win, text="Volver", command=win.destroy)
    btn_volver.pack(pady=10)

    from agendar_cita import abrir_agendar_cita

    def agendar():
        sel = tabla.focus()
        if not sel:
            messagebox.showwarning("Aviso", "Selecciona un doctor.")
            return

        vals = tabla.item(sel, "values")
        id_doc, nombre_doc, esp, hosp = vals[:4]
        abrir_agendar_cita(win, seguro_social, id_doc, nombre_doc, esp, hosp)

    tk.Button(
        win,
        text="Agendar cita con este doctor",
        bg="#00A0D6", fg="white",
        width=30, height=2,
        command=agendar
    ).pack(pady=12)

    return win
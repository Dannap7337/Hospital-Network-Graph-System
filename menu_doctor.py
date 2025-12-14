import csv
import tkinter as tk
from tkinter import messagebox
import os
from pacientes_doctor import abrir_pacientes_atendidos
from citas_doctor import abrir_citas_doctor
from rutas_hospitales_doctor import abrir_rutas_hospitales
BASE_DIR = os.path.dirname(__file__)
RUTA_DOCTORES = os.path.join(BASE_DIR, "datos", "doctores_hospitales_con_id.csv")


def cargar_doctores():
    doctores = {}
    try:
        with open(RUTA_DOCTORES, newline="", encoding="utf-8") as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                fila = {k: v.strip() for k, v in fila.items()}
                doctores[fila["id_doctor"]] = fila
    except FileNotFoundError:
        messagebox.showerror("Error", "El archivo doctores_hospitales_con_id.csv no se encontró")
    return doctores


def abrir_menu_doctor(root, id_doctor):
    try:
        root.withdraw()
    except Exception:
        pass

    doctores = cargar_doctores()

    if id_doctor not in doctores:
        messagebox.showerror("Error", f"No se encontró información del doctor con ID {id_doctor}")
        try:
            root.deiconify()
        except Exception:
            pass
        return

    doctor = doctores[id_doctor]

    nombre = doctor.get("nombre", "Sin nombre")
    especialidad = doctor.get("especialidad", "No registrada")
    hospital = doctor.get("hospital", "No registrado")

    ventana = tk.Toplevel(root)
    ventana.title("Panel del Doctor")
    ventana.geometry("650x600")
    ventana.resizable(False, False)

    def al_cerrar():
        ventana.destroy()
        try:
            root.deiconify()
        except Exception:
            pass

    ventana.protocol("WM_DELETE_WINDOW", al_cerrar)

    tk.Label(
        ventana,
        text=f"Bienvenido {nombre}",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    tk.Label(
        ventana,
        text=f"Especialidad: {especialidad}\nHospital: {hospital}",
        font=("Arial", 12)
    ).pack(pady=10)

    tk.Button(
        ventana, text="Gestionar Citas", width=30, height=2,
        command=lambda: abrir_citas_doctor(ventana, id_doctor, nombre)
    ).pack(pady=10)

    tk.Button(
        ventana, text="Pacientes", width=30, height=2,
        command=lambda: abrir_pacientes_atendidos(ventana, id_doctor, nombre)).pack(pady=10)


    tk.Button(
        ventana, text="Rutas entre hospitales", width=30, height=2,
        command=lambda: abrir_rutas_hospitales(ventana, hospital)
    ).pack(pady=10)

    tk.Button(
        ventana, text="Cerrar sesión", width=20, height=2,
        command=al_cerrar
    ).pack(pady=30)

    return ventana

import tkinter as tk
from tkinter import messagebox

from buscar_doctores import abrir_buscar_doctores
from ver_citas import abrir_ver_citas
from hospital_cercano import abrir_hospital_cercano

def abrir_menu_paciente(root, nombre, ap_paterno, ap_materno, seguro_social):
    try:
        root.withdraw()
    except Exception:
        pass

    ventana = tk.Toplevel(root)
    ventana.title("Panel del Paciente")
    ventana.geometry("520x650")
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
        text=f"Bienvenido(a) {nombre} {ap_paterno}",
        font=("Arial", 16, "bold")
    ).pack(pady=15)

    tk.Label(
        ventana,
        text=f"Número de Seguro Social: {seguro_social}",
        font=("Arial", 12)
    ).pack(pady=5)

    tk.Button(
        ventana,
        text="Buscar doctores / Agendar cita",
        width=30,
        height=2,
        command=lambda: abrir_buscar_doctores(ventana, seguro_social)
    ).pack(pady=12)

    tk.Button(
        ventana,
        text="Ver mis citas",
        width=30,
        height=2,
        command=lambda: abrir_ver_citas(ventana, seguro_social, titulo_extra=nombre)
    ).pack(pady=10)

    tk.Button(
        ventana,
        text="Hospital / Centro médico cercano",
        width=30,
        height=2,
        command=lambda: abrir_hospital_cercano(ventana, seguro_social)
    ).pack(pady=10)

    tk.Button(
        ventana,
        text="Cerrar sesión",
        width=20,
        height=2,
        command=al_cerrar
    ).pack(pady=35)

    return ventana

import tkinter as tk
from tkinter import messagebox
import os

from pacientes import buscar_por_nss, obtener_pacientes, registrar_paciente
from utils import generar_id, _norm_text

BASE_DIR = os.path.dirname(__file__)
RUTA_PACIENTES = os.path.join(BASE_DIR, "datos", "pacientes.csv")

def ventana_registro(root, datos_login):
    nombre, ap_pat, ap_mat, seguro = datos_login

    win = tk.Toplevel(root)
    win.title("Registro de Paciente")
    win.geometry("350x350")
    win.resizable(False, False)

    tk.Label(win, text="Registro de nuevo paciente", font=("Arial", 14, "bold")).pack(pady=10)

    tk.Label(win, text="Latitud:").pack()
    entrada_lat = tk.Entry(win)
    entrada_lat.pack(pady=5)

    tk.Label(win, text="Longitud:").pack()
    entrada_lon = tk.Entry(win)
    entrada_lon.pack(pady=5)

    def guardar():
        lat = entrada_lat.get().strip()
        lon = entrada_lon.get().strip()

        if not lat or not lon:
            messagebox.showwarning("Aviso", "Ingresa latitud y longitud")
            return

        pacientes = obtener_pacientes()
        nuevo_id = generar_id("P", len(pacientes) + 1)

        datos = {
            "id_paciente": nuevo_id,
            "nombre": nombre.strip(),
            "apellido_paterno": ap_pat.strip(),
            "apellido_materno": ap_mat.strip(),
            "seguro_social": seguro.strip(),
            "latitud": lat,
            "longitud": lon
        }

        ok, msg = registrar_paciente(datos)
        if ok:
            messagebox.showinfo("Éxito", msg)
            win.destroy()

            from menu_paciente import abrir_menu_paciente
            abrir_menu_paciente(root, nombre, ap_pat, ap_mat, seguro)
        else:
            messagebox.showerror("Error", msg)

    tk.Button(win, text="Registrar", width=20, command=guardar).pack(pady=20)

def mostrar_login_paciente(root):
    ventana = tk.Toplevel(root)
    ventana.title("Login Paciente")
    ventana.geometry("400x400")
    ventana.resizable(False, False)

    tk.Label(ventana, text="LOGIN PACIENTE", font=("Arial", 16, "bold")).pack(pady=10)

    # Nombre
    tk.Label(ventana, text="Nombre:").pack()
    entrada_nombre = tk.Entry(ventana)
    entrada_nombre.pack(pady=5)

    # Apellido paterno
    tk.Label(ventana, text="Apellido paterno:").pack()
    entrada_ap = tk.Entry(ventana)
    entrada_ap.pack(pady=5)

    # Apellido materno
    tk.Label(ventana, text="Apellido materno:").pack()
    entrada_am = tk.Entry(ventana)
    entrada_am.pack(pady=5)

    # Seguro social
    tk.Label(ventana, text="NSS (Seguro Social):").pack()
    entrada_seguro = tk.Entry(ventana)
    entrada_seguro.pack(pady=5)

    def intentar_login():
        nombre = entrada_nombre.get().strip()
        ap_pat = entrada_ap.get().strip()
        ap_mat = entrada_am.get().strip()
        seguro = entrada_seguro.get().strip()

        if not (nombre and ap_pat and ap_mat and seguro):
            messagebox.showwarning("Aviso", "Completa todos los campos")
            return
        paciente = buscar_por_nss(seguro)

        if paciente:
            if (_norm_text(nombre) == _norm_text(paciente.get("nombre", "")) and
                _norm_text(ap_pat) == _norm_text(paciente.get("apellido_paterno", "")) and
                _norm_text(ap_mat) == _norm_text(paciente.get("apellido_materno", ""))):

                messagebox.showinfo("Bienvenido", f"Hola {paciente['nombre']}")
                ventana.destroy()

                from menu_paciente import abrir_menu_paciente
                abrir_menu_paciente(root,
                            paciente["nombre"],
                            paciente["apellido_paterno"],
                            paciente["apellido_materno"],
                            paciente["seguro_social"])
            else:
                messagebox.showerror(
                    "Error",
                    "Los datos no son correctos.\n"
             )
                return
        else:
            resp = messagebox.askyesno(
                "No encontrado",
                "Paciente no registrado.\n¿Deseas registrarte?"
            )
            if resp:
                ventana_registro(root, (nombre, ap_pat, ap_mat, seguro))

    tk.Button(ventana, text="Ingresar", width=20, command=intentar_login).pack(pady=20)

    return ventana


def mostrar_login(root):
    return mostrar_login_paciente(root)

def abrir_login(root):
    return mostrar_login_paciente(root)

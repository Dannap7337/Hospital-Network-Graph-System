import tkinter as tk
from tkinter import messagebox
import os
from doctores import login_doctor as validar_login
from ui_tema import cargar_fondo, crear_card_centrada, configurar_estilos, crear_boton_redondo_imagen

def mostrar_login(root):
    configurar_estilos()

    ventana = tk.Toplevel(root)
    ventana.title("Login Doctor")
    ventana.geometry("700x500")
    ventana.resizable(False, False)

    # Tarjeta blanca centrada
    card = crear_card_centrada(ventana, 350, 260, bg="white")

    tk.Label(card, text="LOGIN DOCTOR", font=("Segoe UI", 16, "bold"), bg="white").pack(pady=10)

    # Usuario
    tk.Label(card, text="Usuario:", bg="white").pack(anchor="w", padx=20)
    entrada_usuario = tk.Entry(card)
    entrada_usuario.pack(pady=5)

    # Contraseña
    tk.Label(card, text="Contraseña:", bg="white").pack(anchor="w", padx=20)
    entrada_pass = tk.Entry(card, show="*")
    entrada_pass.pack(pady=5)

    def intentar_login():
        usuario = entrada_usuario.get()
        contrasena = entrada_pass.get()

        valido, id_doctor = validar_login(usuario, contrasena)

        if valido:
            messagebox.showinfo("Éxito", f"Bienvenido doctor {usuario}")
            ventana.destroy()

            from menu_doctor import abrir_menu_doctor
            abrir_menu_doctor(root, id_doctor)
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    boton_img = crear_boton_redondo_imagen("Iniciar sesion", color="#00A0D6", ancho=200)
    boton = tk.Button(card, image=boton_img, bd=0, command=intentar_login, bg="white")
    boton.image = boton_img
    boton.pack(pady=15)

    return ventana

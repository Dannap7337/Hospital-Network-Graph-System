# inicio.py
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys

try:
    from ui_tema import cargar_fondo, configurar_estilos, crear_card_centrada, crear_boton_redondo_imagen
    UI_TEMA_OK = True
except Exception:
    UI_TEMA_OK = False

APP_DIR = os.path.dirname(__file__)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)


class InicioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Atención Médica - Inicio")
        self.geometry("900x600")
        self.resizable(False, False)
        self.icon_photo = None

        if UI_TEMA_OK and os.path.exists(os.path.join(APP_DIR, "f1.jpg")):
            try:
                self.bg_label = cargar_fondo(self, os.path.join(APP_DIR, "f1.jpg"), 900, 600)
            except Exception:
                self.bg_label = None
        else:
            self.configure(bg="#f4f6f8")
            self.bg_label = None

        if UI_TEMA_OK:
            configurar_estilos()

        self.img_cache = {}
        self._crear_ui()

    def _crear_ui(self):
        # Card centrado
        if UI_TEMA_OK:
            card = crear_card_centrada(self, width=480, height=450, bg="white")
        else:
            card = tk.Frame(self, bg="white", bd=0, highlightthickness=0)
            card.place(relx=0.5, rely=0.5, anchor="center", width=480, height=420)

        # Logo (opcional)
        logo_path = os.path.join(APP_DIR, "f3.png")
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path).resize((160, 120), Image.Resampling.LANCZOS)
                self.icon_photo = ImageTk.PhotoImage(img)
                tk.Label(card, image=self.icon_photo, bg="white").pack(pady=(18, 6))
            except Exception:
                tk.Label(card, text="[logo]", bg="white", fg="#777", font=("Segoe UI", 12)).pack(pady=(18, 6))
        else:
            tk.Label(card, text="Sistema de Atención Médica", bg="white", fg="#222", font=("Segoe UI", 18, "bold")).pack(pady=(18, 6))

        # Título y subtítulo
        tk.Label(card, text="Bienvenido", bg="white", fg="#333", font=("Segoe UI", 16, "bold")).pack(pady=(6, 2))
        tk.Label(card, text="Seleccione el rol para iniciar sesión", bg="white", fg="#555", font=("Segoe UI", 11)).pack(pady=(0, 18))

        # Botones rol: Doctor / Paciente
        btn_doctor = self._crear_boton(card, "Doctor", self.abrir_login_doctor)
        btn_doctor.pack(pady=8)

        btn_paciente = self._crear_boton(card, "Paciente", self.abrir_login_paciente)
        btn_paciente.pack(pady=8)

        # Nota y salir
        tk.Label(card, text="", bg="white").pack(pady=(10, 2))
        tk.Button(card, text="Salir", bd=0, bg="white", fg="#0088B5", cursor="hand2", command=self.quit).pack(side="bottom", pady=8)

    def _crear_boton(self, parent, texto, comando):
        if UI_TEMA_OK:
            img = crear_boton_redondo_imagen(texto, color="#00A0D6")
            self.img_cache[texto] = img
            b = tk.Button(parent, image=img, bd=0,bg="white", activebackground="white", cursor="hand2", command=comando)
            return b
        return tk.Button(parent, text=texto, width=28, height=2, bg="#00A0D6", fg="white", bd=0, font=("Segoe UI", 11, "bold"), command=comando)

    def abrir_login_doctor(self):
        
        try:
            import login_doctor
            for fn in ("mostrar_login", "abrir_login", "main", "start"):
                if hasattr(login_doctor, fn):
                    getattr(login_doctor, fn)(self)
                    return
            if hasattr(login_doctor, "InicioLogin") or hasattr(login_doctor, "LoginDoctorApp") or hasattr(login_doctor, "App"):
                cls = getattr(login_doctor, "InicioLogin", None) or getattr(login_doctor, "LoginDoctorApp", None) or getattr(login_doctor, "App", None)
                top = tk.Toplevel(self)
                try:
                    cls(top)
                except Exception:
                    messagebox.showinfo("Info", "Módulo de login de doctor encontrado, pero no se pudo inicializar la ventana. Revisa la función de arranque.")
                return
            messagebox.showinfo("Info", "Módulo 'login_doctor.py' encontrado pero no contiene una función pública para abrir la ventana.\n\nImplementa 'mostrar_login(root)' o 'abrir_login(root)' en login_doctor.py.")
        except ModuleNotFoundError:
            messagebox.showwarning("Modulo faltante", "El archivo 'login_doctor.py' no está creado todavía.\nCrea /app/login_doctor.py y define una función pública 'mostrar_login(root)'.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al abrir el login de doctor:\n{e}")

    def abrir_login_paciente(self):
        try:
            import login_paciente
            for fn in ("mostrar_login", "abrir_login", "main", "start"):
                if hasattr(login_paciente, fn):
                    getattr(login_paciente, fn)(self)
                    return
            if hasattr(login_paciente, "InicioLogin") or hasattr(login_paciente, "LoginPacienteApp") or hasattr(login_paciente, "App"):
                cls = getattr(login_paciente, "InicioLogin", None) or getattr(login_paciente, "LoginPacienteApp", None) or getattr(login_paciente, "App", None)
                top = tk.Toplevel(self)
                try:
                    cls(top)
                except Exception:
                    messagebox.showinfo("Info", "Módulo de login de paciente encontrado, pero no se pudo inicializar la ventana. Revisa la función de arranque.")
                return
            messagebox.showinfo("Info", "Módulo 'login_paciente.py' encontrado pero no contiene una función pública para abrir la ventana.\n\nImplementa 'mostrar_login(root)' o 'abrir_login(root)' en login_paciente.py.")
        except ModuleNotFoundError:
            messagebox.showwarning("Modulo faltante", "El archivo 'login_paciente.py' no está creado todavía.\nCrea /app/login_paciente.py y define una función pública 'mostrar_login(root)'.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al abrir el login de paciente:\n{e}")


if __name__ == "__main__":
    # Ejecutar la app
    app = InicioApp()
    app.mainloop()

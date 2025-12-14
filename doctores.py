# doctores.py
import os
from utils import cargar_csv

RUTA_DOCTORES = os.path.join(os.path.dirname(__file__), "datos", "doctores_hospitales_con_id.csv")
RUTA_USUARIOS = os.path.join("datos", "usuarios_doctores.csv")

def obtener_doctores():
    return cargar_csv(RUTA_DOCTORES)

def obtener_usuarios_doctores():
    return cargar_csv(RUTA_USUARIOS)

def login_doctor(usuario, contrasena):
    usuarios = obtener_usuarios_doctores()
    for u in usuarios:
        if u["usuario_login"] == usuario and u["contrasena"] == contrasena:
            return True, u["id_doctor"]
    return False, None


def get_doctor_por_id(id_doctor):
    doctores = obtener_doctores()
    id_doctor = id_doctor.strip()

    for d in doctores:
        if d["id_doctor"].strip() == id_doctor:
            return d

    return None

def doctores_por_especialidad(especialidad):
    doctores = obtener_doctores()
    return [d for d in doctores if especialidad.lower() in d["especialidad"].lower()]

def obtener_coordenadas_doctor(id_doctor):
    d = get_doctor_por_id(id_doctor)
    if d:
        return float(d["latitud"]), float(d["longitud"])
    return None

print("Cargando:", RUTA_USUARIOS)

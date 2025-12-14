# pacientes.py
import os
from utils import cargar_csv, guardar_csv, validar_campos

RUTA = os.path.join("datos", "pacientes.csv")

CAMPOS = [
    "id_paciente",
    "nombre",
    "apellido_paterno",
    "apellido_materno",
    "seguro_social",
    "latitud",
    "longitud"
]

def obtener_pacientes():
    return cargar_csv(RUTA)

def buscar_por_nss(nss):
    pacientes = obtener_pacientes()
    for p in pacientes:
        if p["seguro_social"] == nss:
            return p
    return None

def registrar_paciente(datos):
    if not validar_campos(datos):
        return False, "Faltan datos obligatorios."

    pacientes = obtener_pacientes()

    for p in pacientes:
        if p["seguro_social"] == datos["seguro_social"]:
            return False, "El paciente ya está registrado."

    pacientes.append(datos)
    guardar_csv(RUTA, pacientes, CAMPOS)
    return True, "Paciente registrado correctamente."

def actualizar_ubicacion(nss, lat, lon):
    pacientes = obtener_pacientes()
    actualizado = False

    for p in pacientes:
        if p["seguro_social"] == nss:
            p["latitud"] = str(lat)
            p["longitud"] = str(lon)
            actualizado = True
            break

    if actualizado:
        guardar_csv(RUTA, pacientes, CAMPOS)
        return True, "Ubicación actualizada."
    else:
        return False, "Paciente no encontrado."

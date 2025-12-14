import csv, os, unicodedata, re, json
from math import radians, sin, cos, sqrt, atan2

def cargar_grafo_hospitales(ruta_json: str = None):

    posibles = []
    if ruta_json:
        posibles.append(ruta_json)
    posibles += [os.path.join("datos", "grafo_hospitales.json"),
        "grafo_hospitales.json",
        ]
    for p in posibles:
        if p and os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)

            grafo_norm = {}
            for hosp, vecinos in data.items():
                h_key = _norm_text(hosp)
                grafo_norm[h_key] = {}
                for destino, dist in vecinos:
                    grafo_norm[h_key][_norm_text(destino)] = float(dist)
            return grafo_norm

    return {}

def dijkstra(grafo, origen):
    if origen not in grafo:
        return {}
    dist = {nodo: float("inf") for nodo in grafo}
    dist[origen] = 0.0
    visitado = set()

    import heapq
    heap = [(0.0, origen)]
    while heap:
        d_act, u = heapq.heappop(heap)
        if u in visitado:
            continue
        visitado.add(u)
        for v, w in grafo.get(u, {}).items():
            nd = d_act + float(w)
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
    return dist


RUTA_PACIENTES = os.path.join("datos", "pacientes.csv")
RUTA_DOCTORES = os.path.join("datos", "doctores_hospitales_con_id.csv")

def cargar_csv(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r", encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        return list(lector)

def guardar_csv(ruta, datos, campos):
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(datos)

def generar_id(prefijo, numero):
    return f"{prefijo}{str(numero).zfill(4)}"

def validar_campos(diccionario):
    return all(valor.strip() != "" for valor in diccionario.values())


def _norm_text(s):
    s = (s or "").strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"\s+", " ", s)
    return s

def _split_especialidades(campo):
    if not campo:
        return []
    partes = re.split(r"[,;/|]+", campo)
    return [p.strip() for p in partes if p.strip()]

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def cargar_paciente_nss(nss):
    with open(RUTA_PACIENTES, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if str(row["seguro_social"]).strip() == str(nss).strip():
                return row
    return None

def doctores_ordenados_por_cercania(nss, especialidad):
    
    from pacientes import buscar_por_nss
    from doctores import obtener_doctores

    paciente = buscar_por_nss(str(nss).strip())
    if not paciente:
        return []

    try:
        lat_p = float(paciente.get("latitud", 0))
        lon_p = float(paciente.get("longitud", 0))
    except Exception:
        lat_p = lon_p = 0.0

    doctores = obtener_doctores()
    esp_norm = _norm_text(especialidad)

    docs_filtrados = []
    hospitales = {}
    hosp_original = {}

    for d in doctores:
        tokens = [_norm_text(t) for t in _split_especialidades(d.get("especialidad", ""))]
        if not any(esp_norm in t for t in tokens):
            continue

        hosp = (d.get("hospital") or "").strip()
        hosp_n = _norm_text(hosp)

        try:
            lat_h = float(d.get("latitud", 0))
            lon_h = float(d.get("longitud", 0))
        except Exception:
            lat_h = lon_h = 0.0

        if hosp_n not in hospitales:
            hospitales[hosp_n] = [0.0, 0.0, 0]
            hosp_original[hosp_n] = hosp or hosp_n

        hospitales[hosp_n][0] += lat_h
        hospitales[hosp_n][1] += lon_h
        hospitales[hosp_n][2] += 1

        d2 = dict(d)
        d2["hospital_norm"] = hosp_n
        d2["hospital"] = hosp_original[hosp_n]
        docs_filtrados.append(d2)

    if not docs_filtrados:
        return []

    hosp_coords = {}
    for hosp_n, (s_lat, s_lon, c) in hospitales.items():
        if c > 0:
            hosp_coords[hosp_n] = (s_lat / c, s_lon / c)

    origen = None
    min_hav = float("inf")
    for hosp_n, (lat_h, lon_h) in hosp_coords.items():
        d_hav = haversine_km(lat_p, lon_p, lat_h, lon_h)
        if d_hav < min_hav:
            min_hav = d_hav
            origen = hosp_n

    grafo = cargar_grafo_hospitales()
    dist_grafo = dijkstra(grafo, origen) if origen in grafo else {}

    resultado = []
    for d in docs_filtrados:
        hosp_n = d["hospital_norm"]

        # Recupera la distancia de Origen a este hospital (Hospital A -> Hospital B)
        dist_inter_hosp = dist_grafo.get(hosp_n) 
        
        if dist_inter_hosp is not None:
            # Caso A: El hospital está en el grafo. 
            # Distancia Total = (Paciente -> Origen) + (Origen -> Este Hospital)
            dist_final = min_hav + dist_inter_hosp
        else:
            # Caso B: El hospital NO está en el grafo. 
            # Se usa Haversine directo (Paciente -> Este Hospital)
            lat_h, lon_h = hosp_coords.get(hosp_n, (0.0, 0.0))
            dist_final = haversine_km(lat_p, lon_p, lat_h, lon_h)

        d2 = dict(d)
        d2["dist_km"] = float(dist_final) # <--- Usar la distancia final calculada
        resultado.append(d2)

    resultado.sort(key=lambda x: x["dist_km"])
    return resultado

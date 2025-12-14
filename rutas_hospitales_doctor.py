import tkinter as tk
from tkinter import ttk, messagebox
import json, os

from utils import cargar_grafo_hospitales, _norm_text

BASE_DIR = os.path.dirname(__file__)
RUTA_GRAFO = os.path.join(BASE_DIR, "datos", "grafo_hospitales.json")


def _cargar_grafo_raw():
    if not os.path.exists(RUTA_GRAFO):
        alt = os.path.join(BASE_DIR, "grafo_hospitales.json")
        if os.path.exists(alt):
            with open(alt, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    with open(RUTA_GRAFO, "r", encoding="utf-8") as f:
        return json.load(f)


def dijkstra_con_camino(grafo_norm, origen_norm):
    import heapq

    if origen_norm not in grafo_norm:
        return {}, {}

    dist = {n: float("inf") for n in grafo_norm}
    prev = {n: None for n in grafo_norm}
    dist[origen_norm] = 0.0

    heap = [(0.0, origen_norm)]
    visitado = set()

    while heap:
        d_act, u = heapq.heappop(heap)
        if u in visitado:
            continue
        visitado.add(u)

        for v, w in grafo_norm.get(u, {}).items():
            nd = d_act + float(w)
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))

    return dist, prev


def reconstruir_camino(prev, origen_norm, destino_norm):
    if destino_norm not in prev:
        return []
    cam = []
    cur = destino_norm
    while cur is not None:
        cam.append(cur)
        if cur == origen_norm:
            break
        cur = prev[cur]
    cam.reverse()
    if cam and cam[0] == origen_norm:
        return cam
    return []


def abrir_rutas_hospitales(parent, hospital_preseleccionado=None):
    grafo_raw = _cargar_grafo_raw()
    if not grafo_raw:
        messagebox.showerror("Error", "No se encontró grafo_hospitales.json")
        return

    hospitales = sorted(grafo_raw.keys())

    grafo_norm = cargar_grafo_hospitales()

    win = tk.Toplevel(parent)
    win.title("Rutas entre hospitales")
    win.geometry("820x520")
    win.resizable(True, True)

    tk.Label(win, text="Rutas entre hospitales (Dijkstra)",
             font=("Arial", 15, "bold")).pack(pady=8)

    top = tk.Frame(win)
    top.pack(pady=6)

    tk.Label(top, text="Origen:").grid(row=0, column=0, padx=5)
    cb_origen = ttk.Combobox(top, values=hospitales, state="readonly", width=40)
    cb_origen.grid(row=0, column=1, padx=5)

    tk.Label(top, text="Destino:").grid(row=0, column=2, padx=5)
    cb_dest = ttk.Combobox(top, values=hospitales, state="readonly", width=40)
    cb_dest.grid(row=0, column=3, padx=5)

    if hospital_preseleccionado in hospitales:
        cb_origen.set(hospital_preseleccionado)

    lbl_dist = tk.Label(win, text="Distancia mínima: - km",
                        font=("Arial", 12))
    lbl_dist.pack(pady=6)

    tk.Label(win, text="Camino:", font=("Arial", 11, "bold")).pack()

    txt_camino = tk.Text(win, height=8, wrap="word")
    txt_camino.pack(fill="x", padx=12, pady=5)

    frame_tbl = tk.Frame(win)
    frame_tbl.pack(fill="both", expand=True, padx=12, pady=8)

    cols = ("vecino", "distancia")
    tree = ttk.Treeview(frame_tbl, columns=cols, show="headings", height=8)
    tree.pack(side="left", fill="both", expand=True)
    sb = ttk.Scrollbar(frame_tbl, orient="vertical", command=tree.yview)
    sb.pack(side="right", fill="y")
    tree.configure(yscrollcommand=sb.set)

    tree.heading("vecino", text="Vecino directo del origen")
    tree.heading("distancia", text="Km")
    tree.column("vecino", width=420)
    tree.column("distancia", width=120, anchor="center")

    def mostrar_vecinos(origen):
        tree.delete(*tree.get_children())
        vecinos = grafo_raw.get(origen, [])
        vecinos = sorted(vecinos, key=lambda x: x[1])
        for v, w in vecinos[:15]:
            tree.insert("", "end", values=(v, f"{float(w):.2f}"))

    def calcular():
        origen = cb_origen.get().strip()
        destino = cb_dest.get().strip()

        if not origen or not destino:
            messagebox.showwarning("Falta dato", "Selecciona origen y destino.")
            return
        if origen == destino:
            messagebox.showinfo("Aviso", "Origen y destino son iguales.")
            lbl_dist.config(text="Distancia mínima: 0.00 km")
            txt_camino.delete("1.0", "end")
            txt_camino.insert("end", origen)
            mostrar_vecinos(origen)
            return

        origen_n = _norm_text(origen)
        destino_n = _norm_text(destino)

        dist, prev = dijkstra_con_camino(grafo_norm, origen_n)
        dmin = dist.get(destino_n)

        if dmin is None or dmin == float("inf"):
            lbl_dist.config(text="Distancia mínima: - km")
            txt_camino.delete("1.0", "end")
            txt_camino.insert("end", "No hay ruta encontrada en el grafo.")
            mostrar_vecinos(origen)
            return

        camino_norm = reconstruir_camino(prev, origen_n, destino_n)

        mapa_norm_a_bonito = {_norm_text(h): h for h in hospitales}
        camino_bonito = [mapa_norm_a_bonito.get(n, n) for n in camino_norm]

        lbl_dist.config(text=f"Distancia mínima: {dmin:.2f} km")
        txt_camino.delete("1.0", "end")
        txt_camino.insert("end", " → ".join(camino_bonito))

        mostrar_vecinos(origen)

    ttk.Button(win, text="Calcular ruta", command=calcular).pack(pady=6)
    ttk.Button(win, text="Cerrar", command=win.destroy).pack(pady=6)

    return win

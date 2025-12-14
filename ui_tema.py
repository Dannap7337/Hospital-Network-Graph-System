import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont


def cargar_fondo(ventana, ruta_imagen, ancho, alto):
    imagen = Image.open(ruta_imagen).resize((ancho, alto), Image.LANCZOS)
    fondo = ImageTk.PhotoImage(imagen)

    label = tk.Label(ventana, image=fondo)
    label.image = fondo 
    label.place(x=0, y=0, relwidth=1, relheight=1)
    return label


def configurar_estilos():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "BotonPrincipal.TButton",
        font=("Segoe UI", 11, "bold"),
        foreground="white",
        background="#00A0D6",
        padding=(10, 6),
        borderwidth=0
    )
    style.map(
        "BotonPrincipal.TButton",
        background=[("active", "#0088B5")]
    )


def crear_card_centrada(ventana, width, height, bg="white"):
    card = tk.Frame(ventana, bg=bg, bd=0, highlightthickness=0)
    card.place(relx=0.5, rely=0.5, anchor="center",
               width=width, height=height)
    return card


def crear_boton_redondo_imagen(
    texto,
    color="#00A0D6",
    color_texto="white",
    ancho=220,
    alto=46,
    radio=23,
    font_name="Segoe UI",
    font_size=14
):
    img = Image.new("RGBA", (ancho, alto), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle(
        (0, 0, ancho, alto),
        radius=radio,
        fill=color
    )

    try:
        font = ImageFont.truetype(font_name, font_size)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), texto, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (ancho - text_w) // 2
    y = (alto - text_h) // 2

    draw.text((x, y), texto, font=font, fill=color_texto)

    return ImageTk.PhotoImage(img)

#!/usr/bin/env python3
"""Genera los recursos del perfil de desarrollador de Google Play.

Salidas (play-assets/):
    header-4096x2304.png   cabecera de la pagina de desarrollador
    developer-icon-512.png icono del perfil

App Store no tiene cabecera de desarrollador personalizable: Apple genera esas
paginas automaticamente, asi que esto solo aplica a Play.

La cabecera NO lleva texto a proposito: Play superpone el nombre y el icono del
desarrollador encima, y cualquier titular propio acaba duplicando o chocando con
lo que pinta la tienda. El concepto es un solo trazo de luz, que nace de la
mecanica de ESTELA abstraida hasta ser una firma.

La mitad izquierda se deja deliberadamente tranquila y oscura: es donde Play
suele colocar el nombre, y ahi necesita contraste.

Uso: python3 scripts/gen_perfil_tienda.py   (desde la raiz del repo)
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "play-assets"

# Tokens de rafaelge.es
TINTA = (20, 23, 26)
ORO = (201, 162, 39)
BLANCO = (255, 255, 255)

W, H = 4096, 2304


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def mezcla(c1, c2, t: float):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def bezier(p0, p1, p2, p3, t: float):
    mt = 1 - t
    x = mt**3 * p0[0] + 3 * mt**2 * t * p1[0] + 3 * mt * t**2 * p2[0] + t**3 * p3[0]
    y = mt**3 * p0[1] + 3 * mt**2 * t * p1[1] + 3 * mt * t**2 * p2[1] + t**3 * p3[1]
    return x, y


def fondo() -> Image.Image:
    """Tinta con un halo calido muy tenue detras de donde acaba el trazo."""
    img = Image.new("RGB", (W, H), TINTA)

    # Muchos pasos con caida suave: con pocos circulos grandes el desenfoque no
    # llega a disolverlos y quedan anillos concentricos visibles.
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(halo)
    cx, cy = int(W * 0.73), int(H * 0.28)
    pasos = 60
    for i in range(pasos, 0, -1):
        t = i / pasos
        r = int(1600 * t)
        a = int(26 * (1 - t) ** 2)
        if a > 0:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*ORO, a))
    halo = halo.filter(ImageFilter.GaussianBlur(220))

    return Image.alpha_composite(img.convert("RGBA"), halo)


def estrellas(img: Image.Image) -> Image.Image:
    """Polvo de estrellas escaso: da profundidad sin convertirlo en un poster
    espacial, que es justo el lenguaje del que se viene."""
    import random

    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    rng = random.Random(30072026)
    for _ in range(190):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.uniform(1.5, 4.5)
        a = rng.randint(18, 70)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))
    return Image.alpha_composite(img, capa)


def trazo() -> tuple[Image.Image, tuple[float, float]]:
    """El gesto: de fino y apagado abajo a la izquierda, a grueso y blanco
    arriba a la derecha."""
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)

    p0 = (-0.05 * W, 0.88 * H)
    p1 = (0.28 * W, 0.88 * H)
    p2 = (0.55 * W, 0.44 * H)
    p3 = (0.76 * W, 0.27 * H)

    pasos = 2600
    for i in range(pasos):
        t = i / (pasos - 1)
        x, y = bezier(p0, p1, p2, p3, t)
        # El grosor crece de forma no lineal: casi nada al principio, cuerpo
        # al final. Asi el ojo entra por la cola y termina en la cabeza.
        r = lerp(5.0, 46.0, t**1.7)
        if t < 0.55:
            color = mezcla((120, 92, 26), ORO, t / 0.55)
        else:
            color = mezcla(ORO, BLANCO, (t - 0.55) / 0.45)
        a = int(lerp(70, 255, t**0.6))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(*color, a))

    cabeza = bezier(p0, p1, p2, p3, 1.0)
    return capa, cabeza


def header() -> None:
    img = estrellas(fondo())

    capa, (hx, hy) = trazo()

    # Resplandor: la misma forma desenfocada dos veces, una amplia y otra
    # cerrada, para que el trazo parezca emitir luz en vez de estar pintado.
    img = Image.alpha_composite(img, capa.filter(ImageFilter.GaussianBlur(120)))
    img = Image.alpha_composite(img, capa.filter(ImageFilter.GaussianBlur(38)))
    img = Image.alpha_composite(img, capa)

    # Nucleo blanco de la cabeza, por encima de todo.
    nucleo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dn = ImageDraw.Draw(nucleo)
    pasos = 40
    for i in range(pasos, 0, -1):
        t = i / pasos
        r = 165 * t
        a = int(255 * (1 - t) ** 1.6)
        if a > 0:
            dn.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(*BLANCO, a))
    dn.ellipse([hx - 32, hy - 32, hx + 32, hy + 32], fill=(*BLANCO, 255))
    img = Image.alpha_composite(img, nucleo.filter(ImageFilter.GaussianBlur(10)))

    OUT.mkdir(parents=True, exist_ok=True)
    destino = OUT / "header-4096x2304.png"
    img.convert("RGB").save(destino, optimize=True)
    print(f"  ✓ {destino.relative_to(ROOT)}  ({W}x{H})")


def monograma(lado: int) -> Image.Image:
    """La 'R' dorada sobre tinta del icon.svg del sitio, redibujada.

    El icono si lleva marca: es la identidad, y Play lo muestra pequeño y
    recortado en circulo junto al nombre.
    """
    ss = 4  # supermuestreo, para que la esquina redondeada quede limpia
    img = Image.new("RGBA", (lado * ss, lado * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    radio = int(lado * ss * 116 / 512)
    d.rounded_rectangle([0, 0, lado * ss - 1, lado * ss - 1], radius=radio, fill=(*TINTA, 255))

    # Los indices de HelveticaNeue.ttc son 0=Regular, 1=Bold, 2=Italic.
    try:
        f = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc",
                               int(lado * ss * 290 / 512), index=1)
    except Exception:
        f = ImageFont.load_default()
    d.text((lado * ss * 252 / 512, lado * ss * 352 / 512), "R",
           font=f, fill=(*ORO, 255), anchor="ms")

    r = int(lado * ss * 26 / 512)
    cx, cy = lado * ss * 386 / 512, lado * ss * 326 / 512
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*BLANCO, 255))

    return img.resize((lado, lado), Image.LANCZOS)


def icono() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    destino = OUT / "developer-icon-512.png"
    monograma(512).save(destino, optimize=True)
    print(f"  ✓ {destino.relative_to(ROOT)}  (512x512)")


if __name__ == "__main__":
    header()
    icono()

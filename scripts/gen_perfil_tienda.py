#!/usr/bin/env python3
"""Genera los recursos del perfil de desarrollador de Google Play.

Salidas (play-assets/):
    header-4096x2304.jpg   cabecera de la pagina de desarrollador
    developer-icon-512.png icono del perfil

App Store no tiene cabecera de desarrollador personalizable: Apple genera esas
paginas automaticamente, asi que esto solo aplica a Play.

La cabecera lleva una sola frase, deliberadamente ajena al catalogo: las apps
van y vienen y el perfil no deberia envejecer con ellas. Todo lo demas es
espacio en blanco, que es lo que hace que una pagina de tienda parezca
cuidada.

Fondo claro y grano muy fino: en plano queda barato, y el grano es lo que
da sensacion de papel impreso en vez de PNG.

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
HUESO = (240, 234, 222)   # fondo del icono: no es blanco puro a proposito,
                          # sobre el blanco de la tienda el icono debe leerse
PAPEL_A = (255, 253, 250)
PAPEL_B = (246, 241, 232)

FRASE = "Las cosas bien hechas se notan"

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


def fuente(tam: int, indice: int = 0):
    """Indices de HelveticaNeue.ttc: 0=Regular, 1=Bold, 2=Italic, 7=Light."""
    for ruta, i in (("/System/Library/Fonts/HelveticaNeue.ttc", indice),
                    ("/System/Library/Fonts/Helvetica.ttc", 0)):
        try:
            return ImageFont.truetype(ruta, tam, index=i)
        except Exception:
            continue
    return ImageFont.load_default()


def papel(w: int, h: int) -> Image.Image:
    """Blanco calido con degradado suave y grano fino.

    El degradado se dibuja pequeno y se escala: pintar 9,4 millones de
    pixeles uno a uno en Python tarda una eternidad y el resultado es el
    mismo. El grano es lo que evita que parezca un PNG plano.
    """
    chico = Image.new("RGB", (64, 64))
    d = ImageDraw.Draw(chico)
    for y in range(64):
        d.line([(0, y), (63, y)], fill=mezcla(PAPEL_A, PAPEL_B, y / 63))
    img = chico.resize((w, h), Image.BICUBIC)

    grano = Image.effect_noise((w, h), 22).convert("L")
    return Image.blend(img, Image.merge("RGB", (grano, grano, grano)), 0.028)


def ancho_espaciado(d, texto: str, font, tracking: float) -> float:
    return sum(d.textlength(c, font=font) for c in texto) + tracking * (len(texto) - 1)


def escribe_espaciado(d, x: float, y: float, texto: str, font, fill, tracking: float) -> float:
    """PIL no sabe de tracking, asi que hay que ir letra a letra.

    Devuelve la x donde termina, para poder encadenar el punto en oro.
    """
    for c in texto:
        d.text((x, y), c, font=font, fill=fill, anchor="ls")
        x += d.textlength(c, font=font) + tracking
    return x - tracking


def header() -> None:
    img = papel(W, H)
    d = ImageDraw.Draw(img)
    cx, cy = W // 2, H // 2

    # UltraLight y con aire entre letras: a este tamano es lo que separa un
    # titular cuidado de un texto puesto ahi.
    tam = 190
    tracking = 4.0
    f = fuente(tam, indice=5)
    # 0.52 y no mas: Play recorta la cabecera y a un 64% del ancho la frase
    # ya rozaba los bordes.
    while ancho_espaciado(d, FRASE, f, tracking) > W * 0.52 and tam > 70:
        tam -= 4
        f = fuente(tam, indice=5)

    # El punto va aparte y en oro: es el mismo remate que la "R." del icono.
    punto = fuente(tam, indice=0)
    ancho = ancho_espaciado(d, FRASE, f, tracking) + d.textlength(".", font=punto)

    # El bloque va del filete a la linea base: se centra ese conjunto, no
    # el texto suelto, o queda opticamente alto.
    base = cy + tam * 0.75
    x = escribe_espaciado(d, cx - ancho / 2, base, FRASE, f, TINTA, tracking)
    d.text((x + tracking, base), ".", font=punto, fill=ORO, anchor="ls")

    # Filete de oro sobre la frase.
    ancho_filete = tam * 0.95
    grosor = max(4, tam // 34)
    y_filete = base - tam * 1.55
    d.rectangle([cx - ancho_filete / 2, y_filete,
                 cx + ancho_filete / 2, y_filete + grosor], fill=ORO)

    OUT.mkdir(parents=True, exist_ok=True)
    # JPEG y no PNG: el grano es ruido puro y en PNG se va a 5,6 MB, muy por
    # encima del limite de 1 MB de Play. Play acepta JPEG para la cabecera.
    destino = OUT / "header-4096x2304.jpg"
    img.save(destino, quality=90, subsampling=0, optimize=True, progressive=True)
    kb = destino.stat().st_size / 1024
    print(f"  ✓ {destino.relative_to(ROOT)}  ({W}x{H}, {kb:.0f} KB)")
    if kb > 1024:
        raise SystemExit("la cabecera pasa de 1 MB, Play la rechazara")


def monograma(lado: int, redondeado: bool = False) -> Image.Image:
    """La "R." de la marca, en tinta sobre hueso.

    Play recorta el icono en circulo, asi que por defecto va a sangre y sin
    alfa. El fondo no es blanco puro a proposito: sobre el blanco de la
    tienda, un icono blanco desaparece.
    """
    ss = 4  # supermuestreo
    L = lado * ss
    img = Image.new("RGBA", (L, L), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if redondeado:
        d.rounded_rectangle([0, 0, L - 1, L - 1], radius=int(L * 116 / 512), fill=(*HUESO, 255))
    else:
        d.rectangle([0, 0, L - 1, L - 1], fill=(*HUESO, 255))

    f = fuente(int(L * 0.52), indice=0)
    caja = d.textbbox((0, 0), "R", font=f, anchor="ls")
    ancho_r = caja[2] - caja[0]
    alto_r = caja[1]  # negativo: del baseline hacia arriba

    radio = L * 0.043
    hueco = L * 0.030
    total = ancho_r + hueco + radio * 2
    x0 = (L - total) / 2
    base = (L - alto_r) / 2

    d.text((x0 - caja[0], base), "R", font=f, fill=(*TINTA, 255), anchor="ls")
    cxp = x0 + ancho_r + hueco + radio
    d.ellipse([cxp - radio, base - radio * 2, cxp + radio, base], fill=(*ORO, 255))

    return img.resize((lado, lado), Image.LANCZOS)


def icono() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    destino = OUT / "developer-icon-512.png"
    monograma(512).convert("RGB").save(destino, optimize=True)
    print(f"  ✓ {destino.relative_to(ROOT)}  (512x512, sin alfa)")

    alterno = OUT / "developer-icon-512-redondeado.png"
    monograma(512, redondeado=True).save(alterno, optimize=True)
    print(f"  ✓ {alterno.relative_to(ROOT)}  (512x512, con alfa)")


if __name__ == "__main__":
    header()
    icono()

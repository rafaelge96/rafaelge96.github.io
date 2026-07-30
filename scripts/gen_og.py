#!/usr/bin/env python3
"""Genera assets/og.png (1200x630), la imagen que se ve al compartir el enlace.

Misma estetica que el sitio: azul noche, estrellas y la marca Caelyn.
Uso:  python3 scripts/gen_og.py     (requiere Pillow)
"""

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
OUT = Path(__file__).resolve().parent.parent / "assets" / "og.png"

TEXT = (16, 21, 26)
ACCENT = (18, 80, 110)
MUTED = (90, 102, 114)
LINEA = (236, 232, 224)
TINTA = (20, 23, 26)
ORO = (201, 162, 39)

FONTS = {
    "bold": ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf"],
    "reg": ["/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf"],
}


def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    for path in FONTS[kind]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def background() -> Image.Image:
    """Blanco con un velo azul muy tenue abajo: limpio y minimalista."""
    base = Image.new("RGB", (W, H), (255, 255, 255))
    px = base.load()
    for y in range(H):
        k = (y / (H - 1)) ** 2.2
        row = tuple(round(255 + (247 - 255) * k) if i != 2 else round(255 + (250 - 255) * k)
                    for i in range(3))
        for x in range(W):
            px[x, y] = row
    return base


def filete(d: ImageDraw.ImageDraw) -> None:
    """Banda de acento arriba y filete inferior: el mismo lenguaje que el CV."""
    d.rectangle([0, 0, W, 8], fill=TINTA)
    d.line([96, H - 96, W - 96, H - 96], fill=LINEA, width=2)


def monogram(size: int) -> Image.Image:
    """Marca personal: cuadrado redondeado azul noche con la R en cian."""
    ss = size * 4                                   # supersampling para bordes suaves
    img = Image.new("RGBA", (ss, ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, ss - 1, ss - 1], radius=round(ss * 0.227), fill=TINTA)
    f = font("bold", round(ss * 0.62))
    d.text((ss * 0.47, ss * 0.52), "R", font=f, fill=ORO, anchor="mm")
    dot = round(ss * 0.052)
    d.ellipse([ss * 0.755 - dot, ss * 0.635 - dot, ss * 0.755 + dot, ss * 0.635 + dot],
              fill=(255, 255, 255))
    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    img = background()
    d = ImageDraw.Draw(img)
    filete(d)

    logo = monogram(184)
    img.paste(logo, (96, 224), logo)

    x = 330
    d.text((x, 214), "Rafael González Escobar", font=font("bold", 62), fill=TEXT)
    d.text((x + 2, 300), "Senior Software Engineer · Desarrollo móvil", font=font("bold", 30), fill=ACCENT)
    d.text((x + 2, 352), "Android · Kotlin Multiplatform · Compose · SwiftUI",
           font=font("reg", 24), fill=MUTED)
    d.line([x + 2, 410, x + 520, 410], fill=LINEA, width=2)
    d.text((x + 2, 428), "Apps con millones de usuarios · Producto propio en Google Play y App Store",
           font=font("reg", 21), fill=MUTED)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print(f"OK -> {OUT}  ({OUT.stat().st_size / 1024:.0f} KB)")

    touch = OUT.parent / "apple-touch-icon.png"
    monogram(180).convert("RGB").save(touch, optimize=True)
    print(f"OK -> {touch}  ({touch.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()

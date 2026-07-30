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

TEXT = (234, 246, 248)
ACCENT = (63, 208, 224)
MUTED = (138, 160, 173)

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
    """Degradado vertical + resplandor cian en el horizonte."""
    base = Image.new("RGB", (W, H))
    top, bottom = (6, 16, 28), (13, 34, 54)
    px = base.load()
    for y in range(H):
        k = (y / (H - 1)) ** 1.6
        row = tuple(round(top[i] + (bottom[i] - top[i]) * k) for i in range(3))
        for x in range(W):
            px[x, y] = row

    glow = Image.radial_gradient("L").resize((int(W * 1.7), int(H * 1.5)))
    glow = Image.eval(glow, lambda v: max(0, 210 - v) // 3)
    layer = Image.new("RGB", glow.size, ACCENT)
    base.paste(layer, (int(-W * 0.35), int(H * 0.42)), glow)
    return base


def stars(d: ImageDraw.ImageDraw) -> None:
    random.seed(96)
    for _ in range(90):
        x, y = random.uniform(0, W), random.uniform(0, H)
        r = random.choice([0.9, 1.1, 1.4, 1.9])
        a = random.uniform(0.25, 0.75)
        c = tuple(round(207 + (255 - 207) * 0) for _ in range(3))
        d.ellipse([x - r, y - r, x + r, y + r],
                  fill=(round(207 * a + 10), round(238 * a + 16), round(243 * a + 24)))


def monogram(size: int) -> Image.Image:
    """Marca personal: cuadrado redondeado azul noche con la R en cian."""
    ss = size * 4                                   # supersampling para bordes suaves
    img = Image.new("RGBA", (ss, ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, ss - 1, ss - 1], radius=round(ss * 0.227), fill=(15, 39, 64))
    f = font("bold", round(ss * 0.62))
    d.text((ss * 0.47, ss * 0.52), "R", font=f, fill=ACCENT, anchor="mm")
    dot = round(ss * 0.052)
    d.ellipse([ss * 0.755 - dot, ss * 0.635 - dot, ss * 0.755 + dot, ss * 0.635 + dot], fill=TEXT)
    return img.resize((size, size), Image.LANCZOS)


def main() -> None:
    img = background()
    d = ImageDraw.Draw(img)
    stars(d)

    logo = monogram(184)
    img.paste(logo, (96, 224), logo)

    x = 330
    d.text((x, 214), "Rafael González Escobar", font=font("bold", 62), fill=TEXT)
    d.text((x + 2, 300), "Senior Software Engineer · Desarrollo móvil", font=font("bold", 30), fill=ACCENT)
    d.text((x + 2, 352), "Android · Kotlin Multiplatform · Compose · SwiftUI",
           font=font("reg", 24), fill=MUTED)
    d.line([x + 2, 410, x + 520, 410], fill=(46, 68, 88), width=2)
    d.text((x + 2, 428), "Apps con millones de usuarios · Productos propios en Google Play",
           font=font("reg", 22), fill=MUTED)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, optimize=True)
    print(f"OK -> {OUT}  ({OUT.stat().st_size / 1024:.0f} KB)")

    touch = OUT.parent / "apple-touch-icon.png"
    monogram(180).convert("RGB").save(touch, optimize=True)
    print(f"OK -> {touch}  ({touch.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()

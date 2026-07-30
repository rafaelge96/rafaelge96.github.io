#!/bin/bash
# Descarga las insignias oficiales de las tiendas y recorta el margen
# transparente de la de Google para que ambas se vean a la misma altura.
#
# Uso:  bash scripts/fetch_badges.sh
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p assets/badges tmp

curl -sL -o tmp/google-play-raw.png \
  "https://play.google.com/intl/en_us/badges/static/images/badges/es_badge_web_generic.png"

curl -sL -o assets/badges/app-store.svg \
  "https://tools.applemediaservices.com/api/badges/download-on-the-app-store/black/es-es?size=250x83"

python3 - <<'PY'
from PIL import Image

img = Image.open("tmp/google-play-raw.png").convert("RGBA")
img = img.crop(img.getbbox())                      # fuera el margen transparente
h = 120                                            # 3x de los 40px a los que se muestra
img = img.resize((round(img.width * h / img.height), h), Image.LANCZOS)
img.save("assets/badges/google-play.png", optimize=True)
print("google-play.png", img.size)
PY

rm -rf tmp
ls -la assets/badges

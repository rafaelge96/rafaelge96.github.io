# rafaelge96.github.io

Portafolio personal de **Rafael González Escobar** — Senior Software Engineer.
Publicado con GitHub Pages en <https://rafaelge96.github.io>.

## Cómo está hecho

- Un solo `index.html` con el CSS y el JS en línea: **sin dependencias, sin build, sin frameworks**.
- Tipografía del sistema y paleta propia (blanco + azul pizarra, la misma del CV) con variables CSS.
- Animaciones con `IntersectionObserver` y respeto por `prefers-reduced-motion`.
- Diagrama de arquitectura en SVG inline, con `aria-label` descriptivo.
- SEO: metadatos Open Graph, `sitemap.xml`, `robots.txt` y datos estructurados JSON-LD (`Person`).

## Estructura

```
index.html                 el portafolio completo
404.html                   página de error con la misma identidad
icon.svg                   monograma (favicon)
assets/og.png              imagen para redes (1200x630)
assets/apple-touch-icon.png
assets/cv_*.pdf            CV descargable
assets/apps/               iconos de mis apps
proyectos/android/          logos de los proyectos de cliente
scripts/gen_og.py          regenera og.png y el touch icon
sitemap.xml, robots.txt
```

## Regenerar las imágenes

```bash
python3 scripts/gen_og.py
```

Requiere Pillow (`pip3 install --user Pillow`).

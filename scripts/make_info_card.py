"""Static SVG that looks like the output of a neofetch command: a title
bar, then key/value rows that fade in line by line. Edit FIELDS below to
keep it current -- this is hand-authored, not scraped."""

import os
from pathlib import Path
from xml.sax.saxutils import escape

OUT_PATH = Path(__file__).resolve().parent.parent / "info-card.svg"
FONT = "JetBrains Mono, Consolas, monospace"

TITLE = "frank@github"

FIELDS = [
    ("Role", "Software Developer"),
    ("Location", "Colombia"),
    ("Tecnólogo", "Análisis y Desarrollo de Software (SENA)"),
    ("Ingeniería", "Ingeniero en Sistemas"),
    ("Focus", "Products built to last, not just ship"),
    ("Status", "Open to remote roles"),
]

WIDTH = 520
LINE_H = 26
TOP_PAD = 56
PAD_X = 24


def main():
    static = os.environ.get("STATIC") == "1"
    height = TOP_PAD + len(FIELDS) * LINE_H + 20

    rows = []
    for i, (key, value) in enumerate(FIELDS):
        y = TOP_PAD + i * LINE_H
        delay = 0 if static else i * 0.12
        opacity_style = "opacity:1" if static else f"animation-delay:{delay:.2f}s"
        rows.append(
            f'<text class="row" x="{PAD_X}" y="{y}" style="{opacity_style}">'
            f'<tspan class="key">{escape(key)}</tspan>'
            f'<tspan class="sep">  </tspan>'
            f'<tspan class="val">{escape(value)}</tspan>'
            f'</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <style>
    .bg {{ fill: #0d1117; stroke: #21262d; stroke-width: 1; }}
    .bar {{ fill: #161b22; }}
    .dot {{ opacity: 0.55; }}
    .title {{ fill: #c9c9c9; font: 600 12px {FONT}; }}
    .row {{
      font: 13px {FONT};
      opacity: {"1" if static else "0"};
      transform: translateX(-8px);
      animation: {"none" if static else "slide-in 0.4s ease-out forwards"};
    }}
    .key {{ fill: #2EA043; font-weight: 600; }}
    .val {{ fill: #c9c9c9; }}
    @keyframes slide-in {{
      to {{ opacity: 1; transform: translateX(0); }}
    }}
  </style>
  <rect class="bg" width="{WIDTH}" height="{height}" rx="8"/>
  <rect class="bar" width="{WIDTH}" height="32" rx="8"/>
  <rect class="bar" x="0" y="16" width="{WIDTH}" height="16"/>
  <circle class="dot" cx="20" cy="16" r="5" fill="#ff5f56"/>
  <circle class="dot" cx="38" cy="16" r="5" fill="#ffbd2e"/>
  <circle class="dot" cx="56" cy="16" r="5" fill="#27c93f"/>
  <text class="title" x="{WIDTH / 2}" y="20" text-anchor="middle">{TITLE}</text>
  {"".join(rows)}
</svg>'''

    OUT_PATH.write_text(svg)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()

"""Render the `</>` brand mark as real ASCII art -- rasterize the glyphs,
downsample to a character grid, map pixel density to a character ramp --
then wrap it in an SVG that prints row by row, terminal-style.

Only used locally when you want to regenerate the mark (font/shape
changes). The daily workflow never touches this -- it only refreshes the
contribution heatmap."""

import os
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont

OUT_PATH = Path(__file__).resolve().parent.parent / "brand-mark.svg"
FONT_STACK = "JetBrains Mono, Consolas, monospace"
GREEN = "#2EA043"

MARK = "</>"
GRID_COLS = 64
GRID_ROWS = 34
CELL_PX = 16  # supersample resolution per grid cell, for smooth sampling

RAMP = " .:-=+*#%@"  # dark/empty (sparse) -> bright/ink (dense)

FONT_CANDIDATES = [
    "C:/Windows/Fonts/consolab.ttf",
    "C:/Windows/Fonts/courbd.ttf",
]


def rasterize():
    w, h = GRID_COLS * CELL_PX, GRID_ROWS * CELL_PX
    img = Image.new("L", (w, h), color=0)
    draw = ImageDraw.Draw(img)

    font_path = next((p for p in FONT_CANDIDATES if Path(p).exists()), None)
    font_size = int(h * 0.78)
    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()

    bbox = draw.textbbox((0, 0), MARK, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (w - tw) / 2 - bbox[0]
    y = (h - th) / 2 - bbox[1]
    draw.text((x, y), MARK, font=font, fill=255)
    return img


def to_grid(img):
    rows = []
    for r in range(GRID_ROWS):
        row_chars = []
        for c in range(GRID_COLS):
            box = (c * CELL_PX, r * CELL_PX, (c + 1) * CELL_PX, (r + 1) * CELL_PX)
            cell = img.crop(box)
            mean = sum(cell.getdata()) / (CELL_PX * CELL_PX)
            idx = round((mean / 255) * (len(RAMP) - 1))
            row_chars.append(RAMP[idx])
        rows.append("".join(row_chars))
    # drop fully-blank rows at top/bottom so the art isn't padded with air
    while rows and rows[0].strip() == "":
        rows.pop(0)
    while rows and rows[-1].strip() == "":
        rows.pop()
    return rows


def main():
    static = os.environ.get("STATIC") == "1"
    rows = to_grid(rasterize())

    char_w = 9.5
    line_h = 17
    pad = 24
    width = int(GRID_COLS * char_w) + pad * 2
    height = int(len(rows) * line_h) + pad * 2 + 30

    row_svgs = []
    for i, row in enumerate(rows):
        y = pad + (i + 1) * line_h
        delay = 0 if static else i * 0.05
        style = "" if static else f' style="animation-delay:{delay:.2f}s"'
        row_svgs.append(
            f'<g class="row"{style}>'
            f'<text class="ascii" x="{pad}" y="{y}" xml:space="preserve">{escape(row)}</text>'
            f"</g>"
        )

    caption_delay = 0 if static else len(rows) * 0.05 + 0.3
    caption = "frankalessandro"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>
    .bg {{ fill: #0d1117; stroke: #21262d; stroke-width: 1; }}
    .ascii {{
      font: 12px {FONT_STACK};
      fill: {GREEN};
      white-space: pre;
    }}
    .row {{
      clip-path: {"inset(0 0% 0 0)" if static else "inset(0 100% 0 0)"};
      animation: {"none" if static else "wipe 0.35s steps(24) forwards"};
    }}
    @keyframes wipe {{
      to {{ clip-path: inset(0 0% 0 0); }}
    }}
    .caption {{
      fill: #8b949e;
      font: 13px {FONT_STACK};
      opacity: {"1" if static else "0"};
      animation: {"none" if static else f"fade-in 0.6s ease-out {caption_delay:.2f}s forwards"};
    }}
    @keyframes fade-in {{
      to {{ opacity: 1; }}
    }}
  </style>
  <rect class="bg" width="{width}" height="{height}" rx="8"/>
  {"".join(row_svgs)}
  <text class="caption" x="{width / 2}" y="{height - pad + 6}" text-anchor="middle">{caption}</text>
</svg>'''

    OUT_PATH.write_text(svg)
    print(f"wrote {OUT_PATH} ({len(rows)} rows x {GRID_COLS} cols)")


if __name__ == "__main__":
    main()

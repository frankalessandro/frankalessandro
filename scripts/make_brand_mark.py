"""Static SVG of the `</>` brand mark that 'types' itself in, character
by character, in monochrome green -- the profile's answer to the ASCII
portrait, without putting a photo in the repo."""

import os
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "brand-mark.svg"
GREEN = "#2EA043"
FONT = "JetBrains Mono, Consolas, monospace"

MARK = "</>"
WIDTH = 370
HEIGHT = 370


def main():
    static = os.environ.get("STATIC") == "1"
    char_delay = 0.35
    cursor_start = char_delay * len(MARK) + 0.3

    glyphs = []
    for i, ch in enumerate(MARK):
        delay = 0 if static else i * char_delay
        glyphs.append(
            f'<tspan style="animation-delay:{delay:.2f}s">{ch}</tspan>'
        )

    caption = "frankalessandro"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <style>
    .bg {{ fill: #0d1117; stroke: #21262d; stroke-width: 1; }}
    .mark {{
      font: 700 96px {FONT};
      fill: {GREEN};
    }}
    .mark tspan {{
      opacity: {"1" if static else "0"};
      animation: {"none" if static else "type-in 0.05s steps(1) forwards"};
    }}
    @keyframes type-in {{
      to {{ opacity: 1; }}
    }}
    .cursor {{
      fill: {GREEN};
      opacity: {"0" if static else "1"};
      animation: {"none" if static else f"blink 1s steps(1) {cursor_start:.2f}s 4"};
    }}
    @keyframes blink {{
      50% {{ opacity: 0; }}
    }}
    .caption {{
      fill: #8b949e;
      font: 13px {FONT};
      opacity: 0;
      animation: {"none" if static else f"fade-in 0.6s ease-out {cursor_start:.2f}s forwards"};
    }}
    @keyframes fade-in {{
      to {{ opacity: 1; }}
    }}
  </style>
  <rect class="bg" width="{WIDTH}" height="{HEIGHT}" rx="8"/>
  <text class="mark" x="50%" y="52%" text-anchor="middle" dominant-baseline="middle">{"".join(glyphs)}</text>
  <rect class="cursor" x="{WIDTH / 2 + 88}" y="{HEIGHT * 0.52 - 40}" width="10" height="60"/>
  <text class="caption" x="50%" y="80%" text-anchor="middle">{caption}</text>
</svg>'''

    OUT_PATH.write_text(svg)
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()

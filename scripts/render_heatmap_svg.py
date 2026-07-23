"""Render data/contributions.json as a self-contained animated SVG:
the classic 53-week x 7-day grid, boxes sliding in diagonally, one time,
in a monochrome green ramp -- no third-party stats service involved."""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "contributions.json"
OUT_PATH = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BOX = 11
GAP = 3
LEFT_PAD = 28
TOP_PAD = 34
FONT = "JetBrains Mono, Consolas, monospace"


def build_weeks(days):
    by_date = {d["date"]: d for d in days}
    if not days:
        return []
    dates = sorted(by_date)
    first = datetime.strptime(dates[0], "%Y-%m-%d").date()
    last = datetime.strptime(dates[-1], "%Y-%m-%d").date()

    # align grid start to the preceding Sunday
    start = first
    while start.weekday() != 6:
        from datetime import timedelta
        start -= timedelta(days=1)

    from datetime import timedelta
    weeks = []
    cur = start
    week = []
    while cur <= last:
        key = cur.strftime("%Y-%m-%d")
        cell = by_date.get(key, {"date": key, "level": -1, "count": 0})
        week.append(cell)
        if cur.weekday() == 6 and week:
            pass
        if len(week) == 7:
            weeks.append(week)
            week = []
        cur += timedelta(days=1)
    if week:
        while len(week) < 7:
            week.append({"date": None, "level": -1, "count": 0})
        weeks.append(week)
    return weeks


def render(days, stats):
    weeks = build_weeks(days)
    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * (BOX + GAP) + 160
    height = TOP_PAD + 7 * (BOX + GAP) + 40

    boxes = []
    delay_step = 0.55 / max(n_weeks, 1)
    for wi, week in enumerate(weeks):
        for di, cell in enumerate(week):
            if cell["level"] < 0:
                continue
            x = LEFT_PAD + wi * (BOX + GAP)
            y = TOP_PAD + di * (BOX + GAP)
            color = PALETTE[min(cell["level"], len(PALETTE) - 1)]
            delay = wi * delay_step + di * 0.02
            title = f"{cell['count']} contributions on {cell['date']}" if cell["date"] else ""
            boxes.append(
                f'<rect class="cell" x="{x}" y="{y}" width="{BOX}" height="{BOX}" '
                f'rx="2" fill="{color}" style="animation-delay:{delay:.3f}s">'
                f'<title>{title}</title></rect>'
            )

    legend_x = width - 150
    legend_y = height - 18
    legend_boxes = "".join(
        f'<rect x="{legend_x + 34 + i * (BOX + 3)}" y="{legend_y - BOX + 2}" '
        f'width="{BOX}" height="{BOX}" rx="2" fill="{c}"/>'
        for i, c in enumerate(PALETTE)
    )

    footer = (
        f"{stats['total']:,} contributions in the last year "
        f"&#183; current streak {stats['current_streak']}d "
        f"&#183; longest {stats['longest_streak']}d"
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <style>
    .bg {{ fill: #0d1117; }}
    .cell {{
      opacity: 0;
      transform-origin: center;
      transform: translate(-6px, -6px);
      animation: reveal 0.5s ease-out forwards;
    }}
    @keyframes reveal {{
      to {{ opacity: 1; transform: translate(0, 0); }}
    }}
    .label {{ fill: #8b949e; font: 11px {FONT}; }}
    .footer {{ fill: #2EA043; font: 12px {FONT}; }}
  </style>
  <rect class="bg" width="{width}" height="{height}" rx="6"/>
  {"".join(boxes)}
  <text class="label" x="{legend_x}" y="{legend_y + 4}">Less</text>
  {legend_boxes}
  <text class="label" x="{legend_x + 34 + len(PALETTE) * (BOX + 3) + 6}" y="{legend_y + 4}">More</text>
  <text class="footer" x="{LEFT_PAD}" y="{height - 14}">{footer}</text>
</svg>'''

    OUT_PATH.write_text(svg)
    print(f"wrote {OUT_PATH}")


def main():
    if not DATA_PATH.exists():
        raise SystemExit("data/contributions.json missing -- run fetch_contributions.py first")
    payload = json.loads(DATA_PATH.read_text())
    render(payload["days"], payload["stats"])


if __name__ == "__main__":
    main()

"""Scrape the public (no-auth) contribution calendar HTML fragment GitHub
serves at /users/<username>/contributions and write a normalized JSON with
raw days + derived stats (streaks, best day, totals)."""

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "frankalessandro"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    cells = soup.select("td[data-date]")
    days = []
    for cell in cells:
        d = cell.get("data-date")
        level = cell.get("data-level")
        if level is None:
            # older markup encoded level in a class like ContributionCalendar-day--level-3
            cls = " ".join(cell.get("class", []))
            m = re.search(r"level-(\d)", cls)
            level = m.group(1) if m else "0"
        level = int(level)

        count = 0
        tooltip_id = cell.get("id", "").replace("contribution-day-component", "")
        tooltip = soup.select_one(f'tool-tip[for="{cell.get("id")}"]') if cell.get("id") else None
        text = tooltip.get_text(strip=True) if tooltip else cell.get("aria-label", "")
        m = re.match(r"([\d,]+)\s+contribution", text)
        if m:
            count = int(m.group(1).replace(",", ""))
        elif "No contributions" not in text:
            count = 0

        days.append({"date": d, "level": level, "count": count})

    days.sort(key=lambda x: x["date"])
    return days


def compute_stats(days):
    total = sum(d["count"] for d in days)
    best = max(days, key=lambda d: d["count"], default={"date": None, "count": 0})

    current_streak = 0
    longest_streak = 0
    running = 0
    today = date.today()
    for d in days:
        if d["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    for d in reversed(days):
        d_date = datetime.strptime(d["date"], "%Y-%m-%d").date()
        if d_date > today:
            continue
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best["date"],
        "best_day_count": best["count"],
    }


def main():
    try:
        days = fetch_days()
        if not days:
            raise ValueError("no contribution cells parsed")
        stats = compute_stats(days)
    except Exception as exc:  # network hiccups shouldn't break the daily workflow
        print(f"fetch failed: {exc}", file=sys.stderr)
        if OUT_PATH.exists():
            print("keeping previous data/contributions.json", file=sys.stderr)
            return
        days, stats = [], {"total": 0, "current_streak": 0, "longest_streak": 0, "best_day": None, "best_day_count": 0}

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"days": days, "stats": stats}, indent=2))
    print(f"wrote {len(days)} days, total={stats['total']}")


if __name__ == "__main__":
    main()

"""Fuellt template.dc.html mit echten Tagesdaten fuer eine Story-Analyse.

Nimmt ein JSON mit den Feldern unten, berechnet daraus die abgeleiteten
Werte (Score-Ring-Dashoffset, Chart-Polyline aus echten Schlusskursen)
und schreibt die ausgefuellte .dc.html an den angegebenen Ort.

Erwartetes JSON-Schema (alle Werte sind echte Tagesdaten, keine Platzhalter):
{
  "time": "10:30 AM",
  "country": "US",
  "company": "NVIDIA",
  "ticker": "NVDA",
  "sector": "Technology",
  "score": 8,
  "score_trend": "6 -> 7 -> 8",
  "headline": "Strong momentum, fair valuation",
  "tag1": "RSI 62", "tag2": "Trend up", "tag3": "Risk: Medium",
  "chart_range_label": "10 DAYS",
  "closes": [228.1, 229.4, 227.8, 231.0, 233.5, 232.9, 235.1, 236.8, 238.2, 239.9],
  "chart_note": "10-Tage-Range: $227.80 - $239.90, +5.2% im Zeitraum.",
  "market_cap": "$2.1T", "pe_ratio": "34.2x",
  "high_52w": "$152.30", "low_52w": "$86.10",
  "avg_volume": "48.2M", "div_yield": "0.03%", "next_earnings": "Feb 25",
  "why_today": "Breaking out of a 3-month consolidation range on rising volume.",
  "pro_1": "Earnings trend still pointing up",
  "pro_2": "Institutional buying picked up this week",
  "con_1": "Valuation richer than sector average",
  "con_2": "Nearing short-term overbought territory (RSI 62)"
}

Nutzung:
  python3 quantcode/stories/fill_template.py data.json output.dc.html
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

TEMPLATE_PATH = Path(__file__).parent / "template.dc.html"

CIRCUMFERENCE = 515.2


def _score_dashoffset(score: float) -> str:
    score = max(0.0, min(10.0, score))
    return f"{CIRCUMFERENCE * (1 - score / 10):.1f}"


def _chart_points(closes: list[float]) -> str:
    """Normalisiert echte Schlusskurse auf die 400x240-viewBox (mit Rand)."""
    n = len(closes)
    if n < 2:
        raise ValueError("closes braucht mindestens 2 Werte")
    lo, hi = min(closes), max(closes)
    span = hi - lo or 1.0
    pts = []
    for i, c in enumerate(closes):
        x = i * (400 / (n - 1))
        y = 220 - ((c - lo) / span) * 200
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)


def fill(data: dict) -> str:
    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    replacements = {
        "TIME": data["time"],
        "COUNTRY": data["country"],
        "COMPANY": data["company"],
        "TICKER": data["ticker"],
        "SECTOR": data["sector"],
        "SCORE": str(data["score"]),
        "SCORE_DASHOFFSET": _score_dashoffset(float(data["score"])),
        "HEADLINE": data["headline"],
        "SCORE_TREND": data["score_trend"],
        "TAG1": data["tag1"],
        "TAG2": data["tag2"],
        "TAG3": data["tag3"],
        "CHART_RANGE_LABEL": data["chart_range_label"],
        "CHART_POINTS": _chart_points(data["closes"]),
        "CHART_NOTE": data["chart_note"],
        "MARKET_CAP": data["market_cap"],
        "PE_RATIO": data["pe_ratio"],
        "HIGH_52W": data["high_52w"],
        "LOW_52W": data["low_52w"],
        "AVG_VOLUME": data["avg_volume"],
        "DIV_YIELD": data["div_yield"],
        "NEXT_EARNINGS": data["next_earnings"],
        "WHY_TODAY": data["why_today"],
        "PRO_1": data["pro_1"],
        "PRO_2": data["pro_2"],
        "CON_1": data["con_1"],
        "CON_2": data["con_2"],
    }
    for key, value in replacements.items():
        html = html.replace("{{" + key + "}}", str(value))
    return html


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: fill_template.py <data.json> <output.dc.html>", file=sys.stderr)
        raise SystemExit(1)
    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    out_path = Path(sys.argv[2])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(fill(data), encoding="utf-8")
    print(f"geschrieben: {out_path}")


if __name__ == "__main__":
    main()

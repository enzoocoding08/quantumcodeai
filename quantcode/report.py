"""Formatiert Scoring-Ergebnisse fuer Konsole und als JSON-Report."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

from .data import StockSnapshot
from .scoring import StockScore

DISCLAIMER = "Keine Anlageberatung. Alle Angaben ohne Gewaehr, rein informativ."


def print_score(snapshot: StockSnapshot, score: StockScore) -> None:
    bar = "#" * score.score + "-" * (10 - score.score)
    print(f"\n{snapshot.ticker} ({snapshot.name}) - {snapshot.price} {snapshot.currency}")
    print(f"Score: {score.score}/10  [{bar}]  -> {score.recommendation}")
    print(f"  {score.headline}")
    print("  Pro:")
    for point in score.bullish_points:
        print(f"    + {point}")
    print("  Contra:")
    for point in score.bearish_points:
        print(f"    - {point}")
    print(f"  Risiko: {score.risk_level}")
    print(f"  ({DISCLAIMER})")


def save_report(snapshot: StockSnapshot, score: StockScore, out_dir: str = "reports") -> Path:
    """Speichert das Ergebnis als JSON, ein File pro Tag, ergaenzt statt zu ueberschreiben."""
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    file_path = out_path / f"{date.today().isoformat()}.json"

    entries = json.loads(file_path.read_text()) if file_path.exists() else []
    entries.append({"snapshot": asdict(snapshot), "score": score.model_dump()})
    file_path.write_text(json.dumps(entries, indent=2, ensure_ascii=False))
    return file_path

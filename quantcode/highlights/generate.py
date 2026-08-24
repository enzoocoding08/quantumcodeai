#!/usr/bin/env python3
"""Generiert eine Highlight-Serie aus einer JSON-Definition.

Beispiel:
    python -m quantcode.highlights.generate examples/rsi.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .deck import HighlightDeck


def build_deck(spec: dict, out_root: Path) -> list[Path]:
    thema = spec["thema"]
    out_dir = out_root / thema.lower().replace(" ", "-")
    deck = HighlightDeck(thema=thema, out_dir=out_dir)

    paths = [deck.slide_title(spec["titel_wort"], spec["untertitel"])]
    for eintrag in spec["eintraege"]:
        paths.append(deck.slide_text(
            eyebrow=spec.get("eyebrow", thema),
            headline=eintrag["headline"],
            body=eintrag["body"],
        ))
    return paths


def main() -> None:
    parser = argparse.ArgumentParser(description="QuantCode AI Highlight-Cover-Generator")
    parser.add_argument("spec", help="Pfad zur JSON-Definition der Highlight-Serie")
    parser.add_argument("--out", default=str(Path(__file__).parent / "output"), help="Output-Basisordner")
    args = parser.parse_args()

    spec = json.loads(Path(args.spec).read_text())
    paths = build_deck(spec, Path(args.out))

    print(f"{len(paths)} Folien erstellt:")
    for p in paths:
        print(f"  {p}")


if __name__ == "__main__":
    main()

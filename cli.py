#!/usr/bin/env python3
"""QuantCode AI - Phase 1: Aktien-Scoring per Yahoo-Finance-Daten + Claude.

Beispiel:
    python cli.py AAPL MSFT NVDA
"""

from __future__ import annotations

import argparse
import sys

from dotenv import load_dotenv

from quantcode.data import fetch_snapshot
from quantcode.report import print_score, save_report
from quantcode.scoring import score_stock


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="QuantCode AI Aktien-Scoring (1-10)")
    parser.add_argument("tickers", nargs="+", help="Yahoo-Finance-Ticker, z.B. AAPL MSFT NVDA")
    parser.add_argument("--no-save", action="store_true", help="Ergebnis nicht als JSON speichern")
    args = parser.parse_args()

    for ticker in args.tickers:
        try:
            snapshot = fetch_snapshot(ticker)
            score = score_stock(snapshot)
        except Exception as exc:
            print(f"\n{ticker}: Fehler - {exc}", file=sys.stderr)
            continue

        print_score(snapshot, score)
        if not args.no_save:
            save_report(snapshot, score)


if __name__ == "__main__":
    main()

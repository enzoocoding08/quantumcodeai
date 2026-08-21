# QuantCode AI

Phase 1: Aktien werden anhand oeffentlicher Yahoo-Finance-Daten von Claude
mit einem Score von 1-10 bewertet. Kein Broker, kein automatisierter Handel -
reine Analyse.

**Keine Anlageberatung. Alle Ausgaben ohne Gewaehr, rein informativ.**

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ANTHROPIC_API_KEY eintragen
```

Yahoo-Finance-Daten brauchen keinen API-Key (laufen ueber `yfinance`).

## Benutzung

```bash
python cli.py AAPL MSFT NVDA
```

Gibt fuer jeden Ticker Score, Empfehlung, Pro/Contra-Punkte und Risiko aus
und speichert das Ergebnis zusaetzlich unter `reports/<datum>.json`.

## Projektstruktur

```
quantcode/
  data.py      # Kursdaten + Kennzahlen von Yahoo Finance (yfinance)
  scoring.py   # Claude-Scoring (1-10) via strukturiertem Output
  report.py    # Konsolen-Ausgabe + JSON-Report
cli.py         # Einstiegspunkt
```

## Naechste Schritte (noch nicht umgesetzt)

- Paper Trading (simuliertes Portfolio auf Basis der Scores)
- Broker-Anbindung fuer echten Handel: Trade Republic und Smartbroker haben
  keine oeffentliche Trading-API. Realistische Optionen: Interactive Brokers,
  Lynx oder CapTrader (alle auf IBKR-Technik, mit Python ansteuerbar).

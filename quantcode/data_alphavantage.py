"""Marktdaten-Abruf ueber die Alpha-Vantage-REST-API, als Fallback fuer
fetch_snapshot() in data.py. Braucht ALPHA_VANTAGE_API_KEY (.env).

Warum ein Fallback noetig ist: Yahoo Finance (yfinance, kostenlos, kein Key)
blockt bzw. drosselt aggressiv Anfragen von Cloud-/Rechenzentrum-IPs (HTTP 429)
- auf einem Heim-PC laeuft yfinance meist sofort, auf einem Server/CI/Cloud-Host
nicht zuverlaessig. Alpha Vantage funktioniert ueberall gleich gut, hat dafuer
aber ein Limit von 25 Requests/Tag auf dem kostenlosen Tier.
"""

from __future__ import annotations

import os
import time

import requests

from .data import StockSnapshot, _rsi

BASE_URL = "https://www.alphavantage.co/query"


class AlphaVantageError(RuntimeError):
    """Rate-Limit erreicht oder unerwartete API-Antwort."""


def _get(params: dict) -> dict:
    key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not key:
        raise AlphaVantageError("ALPHA_VANTAGE_API_KEY ist nicht gesetzt (.env).")
    resp = requests.get(BASE_URL, params={**params, "apikey": key}, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if "Information" in data or "Note" in data:
        raise AlphaVantageError(data.get("Information") or data.get("Note"))
    return data


def fetch_snapshot(ticker: str) -> StockSnapshot:
    """Holt Kursdaten und Kennzahlen fuer einen Ticker von Alpha Vantage.

    Braucht 3 Requests (Quote, Overview, Daily Series) - Vorsicht mit dem
    25/Tag-Limit des kostenlosen Keys bei mehreren Tickern hintereinander.
    """
    quote = _get({"function": "GLOBAL_QUOTE", "symbol": ticker}).get("Global Quote", {})
    if not quote:
        raise ValueError(f"Keine Kursdaten fuer '{ticker}' gefunden.")

    time.sleep(1)  # Alpha Vantage: max. 1 Request/Sekunde auf dem Free-Tier
    overview = _get({"function": "OVERVIEW", "symbol": ticker})

    time.sleep(1)
    series = _get({"function": "TIME_SERIES_DAILY", "symbol": ticker, "outputsize": "compact"})
    daily = series.get("Time Series (Daily)", {})
    if not daily:
        raise ValueError(f"Keine historischen Kurse fuer '{ticker}' gefunden.")

    dates_sorted = sorted(daily.keys())
    closes = [float(daily[d]["4. close"]) for d in dates_sorted]
    volumes = [float(daily[d]["5. volume"]) for d in dates_sorted]

    import pandas as pd
    closes_series = pd.Series(closes)
    volumes_series = pd.Series(volumes)

    def pct_change(days: int) -> float | None:
        if len(closes) <= days:
            return None
        old, new = closes[-days], closes[-1]
        if old == 0:
            return None
        return round((new - old) / old * 100, 2)

    return StockSnapshot(
        ticker=ticker.upper(),
        name=overview.get("Name") or ticker.upper(),
        sector=(overview.get("Sector") or "unbekannt").title(),
        price=round(float(quote.get("05. price", closes[-1])), 2),
        currency="USD",
        market_cap=float(overview["MarketCapitalization"]) if overview.get("MarketCapitalization") else None,
        trailing_pe=float(overview["TrailingPE"]) if overview.get("TrailingPE") not in (None, "None", "-") else None,
        forward_pe=float(overview["ForwardPE"]) if overview.get("ForwardPE") not in (None, "None", "-") else None,
        fifty_two_week_high=float(overview["52WeekHigh"]) if overview.get("52WeekHigh") else None,
        fifty_two_week_low=float(overview["52WeekLow"]) if overview.get("52WeekLow") else None,
        sma_20=round(closes_series.tail(20).mean(), 2) if len(closes) >= 20 else None,
        sma_50=round(closes_series.tail(50).mean(), 2) if len(closes) >= 50 else None,
        sma_200=None,  # TIME_SERIES_DAILY (compact) liefert nur ~100 Tage
        rsi_14=_rsi(closes_series),
        volume_avg_30d=round(volumes_series.tail(30).mean(), 0) if len(volumes) >= 30 else None,
        volume_latest=round(volumes[-1], 0),
        price_change_1m_pct=pct_change(21),
        price_change_6m_pct=pct_change(126) if len(closes) > 126 else None,
    )

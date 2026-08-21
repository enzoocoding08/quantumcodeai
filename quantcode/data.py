"""Marktdaten-Abruf ueber Yahoo Finance (yfinance). Keine API-Key noetig."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import yfinance as yf


@dataclass
class StockSnapshot:
    ticker: str
    name: str
    sector: str
    price: float
    currency: str
    market_cap: float | None
    trailing_pe: float | None
    forward_pe: float | None
    fifty_two_week_high: float | None
    fifty_two_week_low: float | None
    sma_20: float | None
    sma_50: float | None
    sma_200: float | None
    rsi_14: float | None
    volume_avg_30d: float | None
    volume_latest: float | None
    price_change_1m_pct: float | None
    price_change_6m_pct: float | None


def _rsi(closes: pd.Series, period: int = 14) -> float | None:
    if len(closes) < period + 1:
        return None
    delta = closes.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    value = rsi.iloc[-1]
    return None if pd.isna(value) else round(float(value), 1)


def _pct_change(closes: pd.Series, days: int) -> float | None:
    if len(closes) <= days:
        return None
    old = closes.iloc[-days]
    new = closes.iloc[-1]
    if old == 0 or pd.isna(old) or pd.isna(new):
        return None
    return round(float((new - old) / old * 100), 2)


def fetch_snapshot(ticker: str) -> StockSnapshot:
    """Holt Kursdaten und Kennzahlen fuer einen Ticker von Yahoo Finance."""
    t = yf.Ticker(ticker)
    info = t.info or {}
    hist = t.history(period="1y", auto_adjust=True)

    if hist.empty:
        raise ValueError(f"Keine Kursdaten fuer '{ticker}' gefunden.")

    closes = hist["Close"]
    volumes = hist["Volume"]

    return StockSnapshot(
        ticker=ticker.upper(),
        name=info.get("shortName") or ticker.upper(),
        sector=info.get("sector") or "unbekannt",
        price=round(float(closes.iloc[-1]), 2),
        currency=info.get("currency") or "USD",
        market_cap=info.get("marketCap"),
        trailing_pe=info.get("trailingPE"),
        forward_pe=info.get("forwardPE"),
        fifty_two_week_high=info.get("fiftyTwoWeekHigh"),
        fifty_two_week_low=info.get("fiftyTwoWeekLow"),
        sma_20=round(float(closes.tail(20).mean()), 2) if len(closes) >= 20 else None,
        sma_50=round(float(closes.tail(50).mean()), 2) if len(closes) >= 50 else None,
        sma_200=round(float(closes.tail(200).mean()), 2) if len(closes) >= 200 else None,
        rsi_14=_rsi(closes),
        volume_avg_30d=round(float(volumes.tail(30).mean()), 0) if len(volumes) >= 30 else None,
        volume_latest=round(float(volumes.iloc[-1]), 0),
        price_change_1m_pct=_pct_change(closes, 21),
        price_change_6m_pct=_pct_change(closes, 126),
    )

"""Claude-basiertes 1-10 Scoring fuer Aktien anhand eines StockSnapshot."""

from __future__ import annotations

import os
from dataclasses import asdict
from typing import List, Literal

import anthropic
from pydantic import BaseModel, Field

from .data import StockSnapshot

DEFAULT_MODEL = os.environ.get("QUANTCODE_MODEL", "claude-opus-5")

SYSTEM_PROMPT = (
    "Du bist der Analyse-Kern von QuantCode AI, einem Bot, der Aktien anhand "
    "oeffentlicher Markt- und Fundamentaldaten bewertet. Du gibst ausschliesslich "
    "eine strukturierte, datenbasierte Einschaetzung ab - keine individuelle "
    "Anlageberatung und KEINE Kauf-/Verkaufsempfehlung. Bewerte nuechtern anhand "
    "der gelieferten Kennzahlen, ohne zu beschoenigen und ohne Panik zu verbreiten. "
    "Fehlende Kennzahlen (None) einfach in der Bewertung auslassen statt zu "
    "spekulieren. Formuliere headline und bullish/bearish_points als neutrale "
    "Beobachtungen ueber die Daten, nie als Handlungsaufforderung ('kaufen', "
    "'verkaufen', 'jetzt einsteigen' o.ae. sind tabu)."
)


class StockScore(BaseModel):
    ticker: str
    score: int = Field(ge=1, le=10, description="Gesamtbewertung: 1 sehr schwach, 10 sehr stark")
    signal: Literal["Stark", "Solide", "Neutral", "Schwach"] = Field(
        description="Rein datenbasierte Charakterisierung des Scores - keine Handlungsempfehlung"
    )
    headline: str = Field(description="Kurzer Claim fuer Content, max. ~8 Woerter, neutral formuliert")
    bullish_points: List[str] = Field(description="2-4 Stichpunkte, die fuer die Aktie sprechen")
    bearish_points: List[str] = Field(description="2-4 Stichpunkte, die gegen die Aktie sprechen")
    risk_level: Literal["niedrig", "mittel", "hoch"]


def score_stock(snapshot: StockSnapshot, *, model: str | None = None) -> StockScore:
    """Laesst Claude eine Aktie anhand des Snapshots 1-10 bewerten."""
    client = anthropic.Anthropic()

    data_block = "\n".join(f"- {k}: {v}" for k, v in asdict(snapshot).items())

    response = client.messages.parse(
        model=model or DEFAULT_MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                "Bewerte folgende Aktie anhand dieser Daten:\n\n"
                f"{data_block}\n\n"
                "Gib eine Gesamtbewertung von 1-10 sowie kurze Pro/Contra-Punkte."
            ),
        }],
        output_format=StockScore,
    )
    return response.parsed_output

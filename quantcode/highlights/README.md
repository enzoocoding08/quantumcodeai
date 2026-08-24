# Highlight-Cover-Generator

Erzeugt Instagram-Story-Highlight-Cover (1080x1920 PNGs) aus einer JSON-Definition.

## Benutzung

```bash
python -m quantcode.highlights.generate quantcode/highlights/examples/rsi.json
```

Erstellt eine Titel-Folie plus eine Inhalts-Folie pro Eintrag unter
`quantcode/highlights/output/<thema>/`.

## JSON-Format

```json
{
  "thema": "RSI",
  "titel_wort": "RSI",
  "untertitel": "Kurzer Untertitel fuer die Titel-Folie",
  "eyebrow": "RSI",
  "eintraege": [
    { "headline": "Text mit *Akzentwort*.", "body": "Erklaerender Fliesstext." }
  ]
}
```

`*wort*` in der Headline wird in der Akzentfarbe (Teal) gesetzt.

## Branding anpassen

Farben, Schriften und Masse stehen zentral in `brand.py`. Aktuell auf das
dunkle Terminal-Theme von QuantCode AI eingestellt (nicht den
Creme-Editorial-Look anderer Accounts).

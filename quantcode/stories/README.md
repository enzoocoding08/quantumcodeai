# Story-Analysen (taegliche Aktienanalyse fuer Instagram Stories)

Erzeugt eine 1080x1920-PNG im QuantCode-AI-Story-Design mit echten
Marktdaten: Score-Ring, Kursverlauf (aus echten Schlusskursen), RSI,
Fundamentaldaten, Pro/Contra.

## Pipeline

1. Echte Daten holen (Alpha Vantage MCP-Tools, siehe unten).
2. Daten in ein JSON nach dem Schema in `fill_template.py` (Docstring) packen.
3. `python3 fill_template.py data.json filled.dc.html`
4. `node render.mjs filled.dc.html output.png`
5. PNG an den Nutzer liefern.

## Warum nur 1 Aktie pro Tag (Stand jetzt)

Eine vollstaendige Analyse braucht ~4-5 Alpha-Vantage-Calls
(GLOBAL_QUOTE, COMPANY_OVERVIEW, TIME_SERIES_DAILY, RSI - manche
Endpunkte muessen wegen Rate-Limits einzeln nachgefragt werden). Der
kostenlose Alpha-Vantage-Key ist auf **25 Requests pro Tag** begrenzt
- das reicht fuer ~1 komplette Aktie mit Puffer, nicht fuer eine ganze
Watchlist von 3 Titeln an einem Tag.

Deshalb rotiert die taegliche Routine `state.json` durch
`watchlist.json` - jeden Tag eine andere Aktie, statt jeden Tag alle
drei mit unvollstaendigen/fehlenden Daten.

**Um taeglich die ganze Watchlist zu bekommen:** ein bezahlter Alpha
Vantage Plan (ab ca. 25-50 USD/Monat, siehe alphavantage.co/premium)
hebt das Tageslimit auf und erlaubt mehrere Requests pro Sekunde -
dann kann die Routine alle Watchlist-Titel an einem Tag durchgehen.

## Dateien

- `template.dc.html` - das Design mit `{{PLATZHALTERN}}`
- `fill_template.py` - fuellt Platzhalter mit echten Daten, berechnet
  Score-Ring-Winkel und Chart-Polyline aus echten Schlusskursen
- `render.mjs` - Playwright-Screenshot der gefuellten Vorlage zu PNG
- `watchlist.json` - Liste der taeglich rotierenden Ticker
- `state.json` - merkt sich, welcher Ticker als naechstes dran ist
- `data/` - archivierte Tages-JSONs (ein Beleg pro generierter Story)

# docs/ - oeffentliches Hosting fuer Social-Media-Dateien

Dieser Ordner wird ueber **GitHub Pages** oeffentlich ausgeliefert
(Repo-Settings -> Pages -> Branch `main`, Ordner `/docs`).
Alles hier liegt unter `https://enzoocoding08.github.io/quantumcodeai/...`
und ist damit fuer die Instagram Graph API abrufbar (media_url/image_url
brauchen eine oeffentliche URL, kein direkter Datei-Upload moeglich).

## Struktur

- `content/daily/<YYYY-MM-DD>/` - taeglich produzierter Content (1 Reel +
  2 Carousels, siehe quantcode/stories/README.md fuer die Story-Analysen,
  die separat unter quantcode/stories/data/ liegen und beim Publizieren
  ebenfalls hierher kopiert werden muessen, falls sie live gepostet werden
  sollen)

## Publizieren

`quantcode/social/publish_instagram.py` nimmt Pfade relativ zum Repo-Root
(z.B. `docs/content/daily/2026-09-01/reel.mp4`) und baut daraus automatisch
die oeffentliche URL ueber `PUBLIC_BASE_URL` aus der `.env`.

Wichtig: Dateien muessen erst **gepusht** sein (git push), bevor GitHub
Pages sie ausliefert - lokale Commits reichen nicht.

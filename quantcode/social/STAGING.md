# Content staging: Queue + GitHub Action

Posting laeuft ohne Claude-Session und ohne `.env` im Container:

1. Eine Session (oder du von Hand) **stagt** Content: Dateien nach `docs/content/...`, Eintrag in `quantcode/content_queue.json`, commit + push.
2. Die GitHub Action `.github/workflows/post-queue.yml` laeuft 5x taeglich (UTC 07:20, 09:50, 12:10, 15:20, 18:25) und postet alles, was faellig ist (`quantcode/social/queue_runner.py`). Danach schreibt sie den Status (`posted` + Permalink) zurueck in die Queue.

## Einmal einrichten

GitHub-Repo -> Settings -> Secrets and variables -> Actions:

- Secret `IG_ACCESS_TOKEN`
- Secret `IG_BUSINESS_ACCOUNT_ID`
- (optional) Variable `PUBLIC_BASE_URL` (Standard: `https://enzoocoding08.github.io/quantumcodeai`)

Test: Actions -> "Post queue to Instagram" -> Run workflow -> `dry_run=true`.

## Queue-Eintrag

```json
{
  "id": "story-lexikon-bullbaer",
  "order": 60,
  "type": "story",              // image | reel | carousel | story
  "status": "pending",          // -> posted | skipped | failed
  "files": ["docs/content/queue/.../lexikon_bullbaer.png"],
  "caption": "",                // Feed-Typen: Caption inkl. Hashtags
  "story_file": null,           // optional: zusaetzlich als Story teilen
  "not_before": "2026-10-23T12:05:00Z",   // optional, UTC
  "valid_until": "2026-10-23T20:00:00Z"   // optional, UTC; danach -> skipped
}
```

Regeln:

- **Zeitabhaengiges** (Kurse, Ticker, Trading-Updates) immer mit `valid_until`, damit nichts Veraltetes erscheint.
- Pro Lauf maximal 1 Feed-Beitrag/Reel (`--max-feed`), Stories bis `--max`.
- Reels brauchen eine AAC-Tonspur (stumm reicht), 1080x1920.
- Dateien muessen oeffentlich ueber Pages erreichbar sein; der Runner wartet bis zu 7 Minuten.
- Der Runner sichert die Queue nach jedem Item; 3 Fehlversuche -> `failed`.

## Von Hand

```
python3 quantcode/social/queue_runner.py --list
python3 quantcode/social/queue_runner.py --dry-run
python3 quantcode/social/queue_runner.py --max 8 --max-feed 1   # braucht IG_* Env-Variablen
```

## Nachschub

Mindestens ~10 `pending` Items vorhalten. Formate mischen: Boersen-Lexikon-Story, Quiz (Frage + Aufloesung 3 h spaeter), Mythen-Check-Karussell, Pexels-Reel, 4:5-Bild, Konzept-Story.

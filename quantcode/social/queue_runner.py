"""Postet faellige Items aus quantcode/content_queue.json auf Instagram.

Laeuft ohne Claude-Session, z.B. als GitHub Action (.github/workflows/post-queue.yml)
oder von Hand. Benoetigt nur drei Umgebungsvariablen:

  IG_ACCESS_TOKEN, IG_BUSINESS_ACCOUNT_ID, PUBLIC_BASE_URL

(PUBLIC_BASE_URL faellt auf die GitHub-Pages-Adresse des Repos zurueck.)

Queue-Format (quantcode/content_queue.json, Feld "items"):
  id, order, type, status, files, caption, story_file (optional)
  type:        "image" (Feed-Bild) | "reel" | "carousel" | "story" (Bild oder Video)
  status:      "pending" -> "posted" | "skipped" | "failed"
  not_before:  optional, ISO-Zeit in UTC, z.B. "2026-10-22T09:45:00Z" - vorher wird nicht gepostet
  valid_until: optional, ISO-Zeit in UTC - danach gilt das Item als veraltet und wird uebersprungen
               (wichtig fuer Kurs-/Ticker-Stories)

Nutzung:
  python3 quantcode/social/queue_runner.py --list
  python3 quantcode/social/queue_runner.py --dry-run
  python3 quantcode/social/queue_runner.py --max 8 --max-feed 1
"""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
QUEUE_PATH = ROOT / "quantcode" / "content_queue.json"
DEFAULT_BASE_URL = "https://enzoocoding08.github.io/quantumcodeai"
FEED_TYPES = {"image", "reel", "carousel"}
MAX_ATTEMPTS = 3


def _load_publisher():
    spec = importlib.util.spec_from_file_location("publish_instagram", ROOT / "quantcode" / "social" / "publish_instagram.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _parse(ts: str | None) -> dt.datetime | None:
    if not ts:
        return None
    return dt.datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def _now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def load_queue() -> dict:
    return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))


def save_queue(queue: dict) -> None:
    QUEUE_PATH.write_text(json.dumps(queue, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def due_items(queue: dict, now: dt.datetime) -> list[dict]:
    """Pending items, die jetzt dran sind - nach not_before, dann order sortiert."""
    due = []
    for item in queue["items"]:
        if item.get("status") != "pending":
            continue
        start = _parse(item.get("not_before"))
        if start and start > now:
            continue
        due.append(item)
    due.sort(key=lambda i: (_parse(i.get("not_before")) or dt.datetime.min.replace(tzinfo=dt.timezone.utc), i.get("order", 0)))
    return due


def _public_url(path: str) -> str:
    base = (os.environ.get("PUBLIC_BASE_URL", "").strip() or DEFAULT_BASE_URL).rstrip("/")
    rel = path[len("docs/"):] if path.startswith("docs/") else path
    return f"{base}/{rel}"


def wait_for_pages(paths: list[str], timeout_s: int = 420) -> bool:
    """Wartet, bis alle Dateien oeffentlich (HTTP 200) erreichbar sind."""
    deadline = time.time() + timeout_s
    pending = list(paths)
    while pending and time.time() < deadline:
        still = []
        for path in pending:
            try:
                ok = requests.head(_public_url(path), timeout=20, allow_redirects=True).status_code == 200
            except requests.RequestException:
                ok = False
            if not ok:
                still.append(path)
        pending = still
        if pending:
            time.sleep(15)
    return not pending


def _retry(fn, *args, tries: int = 4, wait_s: int = 20):
    """Wiederholt bei 'Media not ready' (Graph-API-Code 9007 / 2207027)."""
    for attempt in range(1, tries + 1):
        try:
            return fn(*args)
        except RuntimeError as exc:
            text = str(exc)
            transient = "9007" in text or "2207027" in text or "not ready" in text.lower()
            if not transient or attempt == tries:
                raise
            time.sleep(wait_s)


def publish(pub, item: dict) -> str:
    kind = item["type"]
    files = item["files"]
    caption = item.get("caption", "")
    if kind == "image":
        return _retry(pub.publish_image, files[0], caption)
    if kind == "reel":
        return _retry(pub.publish_video, files[0], caption)
    if kind == "carousel":
        return _retry(pub.publish_carousel, caption, files)
    if kind == "story":
        if files[0].lower().endswith((".mp4", ".mov")):
            return _retry(pub.publish_story_video, files[0])
        return _retry(pub.publish_story_image, files[0])
    raise ValueError(f"Unbekannter type: {kind}")


def verify(media_id: str) -> dict:
    token = os.environ["IG_ACCESS_TOKEN"].strip()
    resp = requests.get(
        f"{pub_graph_base()}/{media_id}",
        params={"fields": "id,media_product_type,permalink,timestamp", "access_token": token},
        timeout=30,
    )
    return resp.json()


def pub_graph_base() -> str:
    return "https://graph.instagram.com/v21.0"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="faellige und kommende Items anzeigen")
    parser.add_argument("--dry-run", action="store_true", help="nichts posten, nur anzeigen was gepostet wuerde")
    parser.add_argument("--max", type=int, default=8, help="maximal so viele Items pro Lauf (Standard 8)")
    parser.add_argument("--max-feed", type=int, default=1, help="davon maximal so viele Feed-Beitraege/Reels (Standard 1)")
    args = parser.parse_args()

    now = _now()
    queue = load_queue()

    if args.list:
        for item in queue["items"]:
            if item.get("status") == "pending":
                print(f"{item.get('not_before', '-'):<22} order={item.get('order'):<4} {item['type']:<9} {item['id']}")
        return 0

    # Veraltete Items (valid_until ueberschritten) aufraeumen, nie mehr posten.
    changed = False
    for item in queue["items"]:
        if item.get("status") == "pending":
            until = _parse(item.get("valid_until"))
            if until and until < now:
                item["status"] = "skipped"
                item["skip_reason"] = "stale (valid_until ueberschritten)"
                changed = True
                print(f"uebersprungen (veraltet): {item['id']}")

    todo = due_items(queue, now)
    if not todo:
        print("Nichts faellig.")
        if changed and not args.dry_run:
            save_queue(queue)
        return 0

    missing = [v for v in ("IG_ACCESS_TOKEN", "IG_BUSINESS_ACCOUNT_ID") if not os.environ.get(v, "").strip()]
    if missing and not args.dry_run:
        print(f"FEHLER: {', '.join(missing)} fehlt (GitHub: Settings > Secrets and variables > Actions).")
        return 2
    os.environ.setdefault("PUBLIC_BASE_URL", DEFAULT_BASE_URL)
    if not os.environ["PUBLIC_BASE_URL"].strip():
        os.environ["PUBLIC_BASE_URL"] = DEFAULT_BASE_URL

    pub = None if args.dry_run else _load_publisher()
    posted = feed_posted = failures = 0

    for item in todo:
        if posted >= args.max:
            break
        is_feed = item["type"] in FEED_TYPES
        if is_feed and feed_posted >= args.max_feed:
            continue
        paths = list(item["files"]) + ([item["story_file"]] if item.get("story_file") else [])
        label = f"{item['id']} ({item['type']})"
        if args.dry_run:
            print(f"wuerde posten: {label}")
            posted += 1
            feed_posted += is_feed
            continue
        if not wait_for_pages(paths):
            print(f"uebersprungen (Dateien noch nicht ueber Pages erreichbar): {label}")
            continue
        try:
            media_id = publish(pub, item)
            if item.get("story_file") and item["type"] != "story":
                _retry(pub.publish_story_image, item["story_file"])
            info = verify(media_id)
            item["status"] = "posted"
            item["posted_at"] = _now().isoformat(timespec="seconds")
            item["media_id"] = media_id
            if info.get("permalink"):
                item["permalink"] = info["permalink"]
            print(f"gepostet: {label} -> {info.get('media_product_type')} {info.get('permalink', media_id)}")
            posted += 1
            feed_posted += is_feed
            changed = True
        except Exception as exc:  # noqa: BLE001 - jeden Fehler pro Item festhalten, Rest weiterlaufen lassen
            item["attempts"] = item.get("attempts", 0) + 1
            item["last_error"] = str(exc)[:300]
            if item["attempts"] >= MAX_ATTEMPTS:
                item["status"] = "failed"
            failures += 1
            changed = True
            print(f"FEHLER bei {label}: {str(exc)[:300]}")
        save_queue(queue)  # nach jedem Item sichern, damit ein Abbruch nichts doppelt postet
        time.sleep(3)

    if changed and not args.dry_run:
        save_queue(queue)
    print(f"Fertig: {posted} gepostet, {failures} Fehler.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

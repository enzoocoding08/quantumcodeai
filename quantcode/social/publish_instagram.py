"""Veroeffentlicht Reels, Carousels und Bilder ueber die Instagram Graph API.

Voraussetzungen (siehe .env):
- IG_ACCESS_TOKEN, IG_BUSINESS_ACCOUNT_ID (siehe README im Repo-Root)
- PUBLIC_BASE_URL: die Dateien muessen bereits unter docs/ im Repo liegen
  und ueber GitHub Pages oeffentlich erreichbar sein (PUBLIC_BASE_URL +
  Pfad relativ zu docs/). Kein Push, kein Publish.

Nutzung:
  python3 quantcode/social/publish_instagram.py image docs/content/daily/2026-09-01/foo.png "Caption text"
  python3 quantcode/social/publish_instagram.py video docs/content/daily/2026-09-01/foo.mp4 "Caption text"
  python3 quantcode/social/publish_instagram.py carousel "Caption text" docs/.../slide1.png docs/.../slide2.png ...
"""

from __future__ import annotations

import os
import sys
import time

import requests

GRAPH_BASE = "https://graph.instagram.com/v21.0"


def _env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} fehlt in .env")
    return value


def _public_url(repo_relative_path: str) -> str:
    base = _env("PUBLIC_BASE_URL").rstrip("/")
    rel = repo_relative_path
    if rel.startswith("docs/"):
        rel = rel[len("docs/") :]
    return f"{base}/{rel}"


def _post(path: str, **params) -> dict:
    token = _env("IG_ACCESS_TOKEN")
    resp = requests.post(f"{GRAPH_BASE}/{path}", data={**params, "access_token": token}, timeout=60)
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"Graph API Fehler bei {path}: {data['error']}")
    return data


def _wait_until_ready(container_id: str, timeout_s: int = 120) -> None:
    """Pollt den Media-Container-Status, bis er FINISHED ist (wichtig fuer Videos)."""
    token = _env("IG_ACCESS_TOKEN")
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        resp = requests.get(
            f"{GRAPH_BASE}/{container_id}",
            params={"fields": "status_code", "access_token": token},
            timeout=30,
        )
        status = resp.json().get("status_code")
        if status == "FINISHED":
            return
        if status == "ERROR":
            raise RuntimeError(f"Media-Container {container_id} fehlgeschlagen (status ERROR)")
        time.sleep(3)
    raise RuntimeError(f"Media-Container {container_id} wurde nicht rechtzeitig fertig (Timeout)")


def publish_image(repo_relative_path: str, caption: str) -> str:
    ig_user_id = _env("IG_BUSINESS_ACCOUNT_ID")
    url = _public_url(repo_relative_path)
    container = _post(f"{ig_user_id}/media", image_url=url, caption=caption)
    container_id = container["id"]
    result = _post(f"{ig_user_id}/media_publish", creation_id=container_id)
    return result["id"]


def publish_video(repo_relative_path: str, caption: str, as_reel: bool = True) -> str:
    ig_user_id = _env("IG_BUSINESS_ACCOUNT_ID")
    url = _public_url(repo_relative_path)
    media_type = "REELS" if as_reel else "VIDEO"
    container = _post(f"{ig_user_id}/media", video_url=url, caption=caption, media_type=media_type)
    container_id = container["id"]
    _wait_until_ready(container_id)
    result = _post(f"{ig_user_id}/media_publish", creation_id=container_id)
    return result["id"]


def publish_carousel(caption: str, repo_relative_paths: list[str]) -> str:
    if not 2 <= len(repo_relative_paths) <= 10:
        raise ValueError("Carousel braucht 2 bis 10 Bilder")
    ig_user_id = _env("IG_BUSINESS_ACCOUNT_ID")
    child_ids = []
    for path in repo_relative_paths:
        url = _public_url(path)
        child = _post(f"{ig_user_id}/media", image_url=url, is_carousel_item="true")
        child_ids.append(child["id"])
    carousel = _post(
        f"{ig_user_id}/media",
        media_type="CAROUSEL",
        caption=caption,
        children=",".join(child_ids),
    )
    result = _post(f"{ig_user_id}/media_publish", creation_id=carousel["id"])
    return result["id"]


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(1)
    kind = sys.argv[1]
    if kind == "image":
        media_id = publish_image(sys.argv[2], sys.argv[3])
    elif kind == "video":
        media_id = publish_video(sys.argv[2], sys.argv[3])
    elif kind == "carousel":
        caption = sys.argv[2]
        media_id = publish_carousel(caption, sys.argv[3:])
    else:
        print(__doc__)
        raise SystemExit(1)
    print(f"veroeffentlicht: media_id={media_id}")


if __name__ == "__main__":
    main()

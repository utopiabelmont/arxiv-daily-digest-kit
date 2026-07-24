#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fetch recent YouTube research videos with YouTube Data API v3.

Reads config.json -> youtube, requires YOUTUBE_API_KEY only when enabled,
deduplicates against links in digests/*.md, and writes youtube.md.
Stdlib only.
"""
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

DIGEST_DIR = "digests"
VIDEO_ID_RE = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{6,})",
    re.IGNORECASE,
)


def load_cfg():
    with open("config.json", encoding="utf-8") as f:
        return json.load(f)


def past_video_ids():
    ids = set()
    if os.path.isdir(DIGEST_DIR):
        for name in os.listdir(DIGEST_DIR):
            if not name.endswith(".md"):
                continue
            try:
                text = open(
                    os.path.join(DIGEST_DIR, name), encoding="utf-8"
                ).read()
                ids.update(VIDEO_ID_RE.findall(text))
            except Exception:
                pass
    return ids


def norm(text):
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", text.lower())


def fetch(query, key, cutoff, cfg):
    max_results = min(50, max(1, int(cfg.get("top_n", 6)) * 2))
    params = {
        "part": "snippet",
        "type": "video",
        "order": "date",
        "q": query,
        "publishedAfter": cutoff.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "maxResults": str(max_results),
        "safeSearch": "moderate",
        "key": key,
        "fields": (
            "items(id/videoId,snippet(title,description,channelTitle,"
            "publishedAt,thumbnails/medium/url))"
        ),
    }
    if cfg.get("relevance_language"):
        params["relevanceLanguage"] = cfg["relevance_language"]
    if cfg.get("region_code"):
        params["regionCode"] = cfg["region_code"]
    url = "https://www.googleapis.com/youtube/v3/search?" + urllib.parse.urlencode(
        params
    )
    req = urllib.request.Request(
        url, headers={"User-Agent": "arxiv-digest-kit/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response).get("items", [])


def parse_item(item):
    video_id = item.get("id", {}).get("videoId", "").strip()
    snippet = item.get("snippet", {})
    try:
        published = datetime.fromisoformat(
            snippet.get("publishedAt", "").replace("Z", "+00:00")
        )
    except ValueError:
        published = None
    thumbnails = snippet.get("thumbnails", {})
    thumbnail = (thumbnails.get("medium") or {}).get("url", "")
    if not thumbnail.startswith("https://i.ytimg.com/"):
        thumbnail = ""
    return {
        "id": video_id,
        "title": html.unescape(snippet.get("title", "")).strip(),
        "channel": html.unescape(snippet.get("channelTitle", "")).strip(),
        "published": published,
        "link": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
        "thumbnail": thumbnail,
        "snippet": " ".join(
            html.unescape(snippet.get("description", "")).split()
        )[:300],
    }


def error_label(exc):
    if isinstance(exc, urllib.error.HTTPError):
        return f"HTTP {exc.code} {exc.reason}"
    if isinstance(exc, urllib.error.URLError):
        return f"network error: {exc.reason}"
    return f"{type(exc).__name__}: {exc}"


def main():
    cfg = load_cfg()
    youtube = cfg.get("youtube", {})
    if not youtube.get("enabled", False):
        open("youtube.md", "w", encoding="utf-8").write("YOUTUBE_DISABLED")
        print("youtube disabled")
        return

    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        sys.exit(
            "Missing env YOUTUBE_API_KEY (set it as a protected secret; "
            "never write it to config.json)."
        )

    tz = timezone(timedelta(hours=cfg.get("timezone_utc_offset", 0)))
    hours = int(youtube.get("window_hours", 168))
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    old_ids = past_video_ids()
    seen_ids, seen_titles, videos, errors = set(), set(), [], 0
    queries = youtube.get("queries", [])

    for query in queries:
        try:
            for raw in fetch(query, key, cutoff, youtube):
                item = parse_item(raw)
                title_key = norm(item["title"])
                if (
                    not item["id"]
                    or not item["title"]
                    or item["published"] is None
                    or item["published"] < cutoff
                    or item["id"] in old_ids
                    or item["id"] in seen_ids
                    or title_key in seen_titles
                ):
                    continue
                seen_ids.add(item["id"])
                seen_titles.add(title_key)
                videos.append(item)
        except Exception as exc:
            errors += 1
            sys.stderr.write(
                f"[warn] YouTube query {query!r} failed: {error_label(exc)}\n"
            )

    videos.sort(key=lambda item: item["published"], reverse=True)
    top = videos[: int(youtube.get("top_n", 6))]
    today = datetime.now(tz).strftime("%Y-%m-%d")
    lines = [
        f"# YouTube candidates {today} "
        f"({len(top)} videos, window {hours}h)\n"
    ]
    if queries and errors == len(queries):
        lines.append("ALL_YOUTUBE_QUERIES_FAILED")
    elif not top:
        lines.append("NO_NEW_VIDEOS")
    for index, item in enumerate(top, 1):
        date = item["published"].astimezone(tz).strftime("%Y-%m-%d")
        lines += [
            f"## {index}. {item['title']}",
            f"- channel: {item['channel'] or '?'} | date: {date}",
            f"- link: {item['link']}",
            f"- thumbnail: {item['thumbnail'] or '?'}",
            f"- description snippet: {item['snippet'] or '(empty)'}\n",
        ]
    open("youtube.md", "w", encoding="utf-8").write("\n".join(lines))
    print(f"done: {len(top)} YouTube videos (failed queries {errors})")


if __name__ == "__main__":
    main()

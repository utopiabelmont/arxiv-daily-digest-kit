#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Config-driven industry-news fetcher via Google News RSS (no API key, stdlib only).
Reads config.json -> news.queries; dedups against digests/*.md links; outputs news.md."""
import email.utils, json, os, re, sys, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

TAG_RE = re.compile(r"<[^>]+>")
URL_RE = re.compile(r"https?://\S+")
DIGEST_DIR = "digests"

def load_cfg():
    with open("config.json", encoding="utf-8") as f:
        return json.load(f)

def past_links():
    links = set()
    if os.path.isdir(DIGEST_DIR):
        for fn in os.listdir(DIGEST_DIR):
            if fn.endswith(".md"):
                try:
                    links |= set(URL_RE.findall(open(os.path.join(DIGEST_DIR, fn), encoding="utf-8").read()))
                except Exception:
                    pass
    return links

def fetch(q, hl, gl, ceid):
    url = ("https://news.google.com/rss/search?q=" + urllib.parse.quote_plus(q)
           + f"&hl={hl}&gl={gl}&ceid={ceid}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 arxiv-digest-kit/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def items(xml_bytes):
    ch = ET.fromstring(xml_bytes).find("channel")
    if ch is None:
        return
    for it in ch.findall("item"):
        try:
            dt = email.utils.parsedate_to_datetime(it.findtext("pubDate") or "")
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except Exception:
            dt = None
        yield {"title": (it.findtext("title") or "").strip(),
               "link": (it.findtext("link") or "").strip(),
               "source": (it.findtext("source") or "").strip(),
               "dt": dt,
               "snippet": " ".join(TAG_RE.sub(" ", it.findtext("description") or "").split())[:200]}

def norm(t):
    return re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", t.lower())

def main():
    cfg = load_cfg(); n = cfg.get("news", {})
    if not n.get("enabled", False):
        open("news.md", "w", encoding="utf-8").write("NEWS_DISABLED")
        print("news disabled"); return
    tz = timezone(timedelta(hours=cfg.get("timezone_utc_offset", 0)))
    cutoff = datetime.now(timezone.utc) - timedelta(hours=n.get("window_hours", 168))
    old, seen_l, seen_t, got, errs = past_links(), set(), set(), [], 0
    for q in n.get("queries", []):
        try:
            for it in items(fetch(q["q"], q.get("hl", "en-US"), q.get("gl", "US"), q.get("ceid", "US:en"))):
                if not it["title"] or not it["link"] or it["dt"] is None or it["dt"] < cutoff:
                    continue
                k = norm(it["title"])
                if it["link"] in seen_l or k in seen_t or it["link"] in old:
                    continue
                seen_l.add(it["link"]); seen_t.add(k); got.append(it)
        except Exception as ex:
            errs += 1; sys.stderr.write(f"[warn] query failed {q.get('q')!r}: {ex}\n")
    got.sort(key=lambda x: x["dt"], reverse=True)
    top = got[:n.get("top_n", 10)]
    today = datetime.now(tz).strftime("%Y-%m-%d")
    L = [f"# News candidates {today} ({len(top)} items, window {n.get('window_hours',168)}h)\n"]
    if errs and errs == len(n.get("queries", [])):
        L.append("ALL_QUERIES_FAILED (network blocked? allow news.google.com)")
    elif not top:
        L.append("NO_NEW_ITEMS")
    for i, it in enumerate(top, 1):
        d = it["dt"].astimezone(tz).strftime("%Y-%m-%d") if it["dt"] else "?"
        L += [f"## {i}. {it['title']}",
              f"- source: {it['source'] or '?'} | date: {d}",
              f"- link: {it['link']}",
              f"- snippet: {it['snippet']}\n"]
    open("news.md", "w", encoding="utf-8").write("\n".join(L))
    print(f"done: {len(top)} news items (failed queries {errs})")

if __name__ == "__main__":
    main()

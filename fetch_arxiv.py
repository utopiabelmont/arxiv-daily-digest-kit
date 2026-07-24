#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Config-driven daily arXiv fetcher. Reads config.json; outputs candidates.md + papers.json.
Cross-day dedup scans digests/*.md for arXiv IDs already reported. Stdlib only."""
import json, os, re, sys, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

API = "http://export.arxiv.org/api/query"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"
ID_RE = re.compile(r"\b(\d{4}\.\d{4,5})\b")
PER_PAGE = 100
DIGEST_DIR = "digests"

def load_cfg():
    with open("config.json", encoding="utf-8") as f:
        return json.load(f)

def past_ids():
    ids = set()
    if os.path.isdir(DIGEST_DIR):
        for fn in os.listdir(DIGEST_DIR):
            if fn.endswith(".md"):
                try:
                    ids |= set(ID_RE.findall(open(os.path.join(DIGEST_DIR, fn), encoding="utf-8").read()))
                except Exception:
                    pass
    return ids

def fetch_page(a, start):
    q = "(" + " OR ".join(f"cat:{c}" for c in a["categories"]) + ") AND (" \
        + " OR ".join(a["server_terms"]) + ")"
    url = API + "?" + urllib.parse.urlencode({
        "search_query": q, "sortBy": "submittedDate", "sortOrder": "descending",
        "start": start, "max_results": PER_PAGE})
    req = urllib.request.Request(url, headers={"User-Agent": "arxiv-digest-kit/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def parse(xml_bytes):
    out = []
    for e in ET.fromstring(xml_bytes).findall(f"{ATOM}entry"):
        raw = e.findtext(f"{ATOM}id", "")
        prim = e.find(f"{ARXIV}primary_category")
        out.append({
            "arxiv_id": raw.split("/abs/")[-1].split("v")[0],
            "title": " ".join((e.findtext(f"{ATOM}title") or "").split()),
            "summary": " ".join((e.findtext(f"{ATOM}summary") or "").split()),
            "published": e.findtext(f"{ATOM}published", ""),
            "authors": [a.findtext(f"{ATOM}name", "") for a in e.findall(f"{ATOM}author")][:6],
            "primary_category": prim.get("term") if prim is not None else "",
            "link": raw})
    return out

def fresh(published, hours):
    try:
        dt = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return False
    return dt >= datetime.now(timezone.utc) - timedelta(hours=hours)

def score(p, kws):
    t, s = p["title"].lower(), p["summary"].lower()
    return sum((3 if k in t else 0) + (1 if k in s else 0) for k in kws)

def main():
    cfg = load_cfg(); a = cfg["arxiv"]
    tz = timezone(timedelta(hours=cfg.get("timezone_utc_offset", 0)))
    past, seen, got, skipped = past_ids(), set(), [], 0
    for pg in range(a.get("max_pages", 3)):
        try:
            entries = parse(fetch_page(a, pg * PER_PAGE))
        except Exception as ex:
            sys.stderr.write(f"[warn] page {pg} failed: {ex}\n"); continue
        if not entries:
            break
        for p in entries:
            if p["arxiv_id"] in seen or not fresh(p["published"], a.get("window_hours", 72)):
                continue
            seen.add(p["arxiv_id"])
            if p["arxiv_id"] in past:
                skipped += 1; continue
            p["score"] = score(p, [k.lower() for k in a["keywords"]])
            if p["score"] > 0:
                got.append(p)
    got.sort(key=lambda x: (x["score"], x["published"]), reverse=True)
    top = got[:a.get("top_n", 12)]
    today = datetime.now(tz).strftime("%Y-%m-%d")
    json.dump({"date": today, "count": len(top), "papers": top},
              open("papers.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    L = [f"# arXiv candidates {today} ({len(top)} papers, {skipped} past duplicates skipped)\n"]
    if not top:
        L.append("NO_NEW_PAPERS_TODAY")
    for i, p in enumerate(top, 1):
        L += [f"## {i}. {p['title']}",
              f"- arXiv: {p['arxiv_id']} | cat: {p['primary_category']} | score: {p['score']}",
              f"- authors: {', '.join(p['authors'])}",
              f"- link: {p['link']}",
              f"- abstract: {p['summary']}\n"]
    open("candidates.md", "w", encoding="utf-8").write("\n".join(L))
    print(f"done: {len(top)} candidates ({today}, window {a.get('window_hours',72)}h, skipped {skipped})")

if __name__ == "__main__":
    main()

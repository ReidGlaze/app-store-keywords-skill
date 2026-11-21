#!/usr/bin/env python3
"""Collect keyword candidates from public App Store data: search autocomplete hints and the names of apps ranking for seed terms (US storefront). No account needed; sends only the seed terms.
usage: collect_candidates.py seed1 "seed two" ...  -> writes candidates-autocomplete.csv, candidates-competitors.csv"""
import csv, json, re, sys, time, urllib.parse, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15"}
def get(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r: return r.read().decode("utf-8", "replace")
def hints(term):
    url = "https://search.itunes.apple.com/WebObjects/MZSearchHints.woa/wa/hints?clientApplication=Software&term=" + urllib.parse.quote(term)
    try: body = get(url, {"X-Apple-Store-Front": "143441-1,29"})
    except Exception as e: return [], str(e)
    out = re.findall(r"<key>term</key>\s*<string>([^<]+)</string>", body)
    if not out:
        try: out = [h.get("term") for h in json.loads(body).get("hints", [])]
        except Exception: pass
    return [o for o in out if o], ""
def top_apps(term, n=10):
    url = "https://itunes.apple.com/search?" + urllib.parse.urlencode({"term": term, "entity": "software", "country": "us", "limit": n})
    try: return json.loads(get(url)).get("results", [])
    except Exception: return []
seeds = sys.argv[1:]
with open("candidates-autocomplete.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["seed", "position", "suggestion"])
    for s in seeds:
        hs, err = hints(s)
        for i, h in enumerate(hs, 1): w.writerow([s, i, h])
        if err: w.writerow([s, "", "ERROR " + err])
        time.sleep(0.4)
seen = {}
for s in seeds:
    for rank, a in enumerate(top_apps(s), 1):
        i = a.get("trackId")
        if i and i not in seen: seen[i] = {"seed": s, "rank": rank, "name": a.get("trackName", ""), "genre": a.get("primaryGenreName", ""), "ratings": a.get("userRatingCount", 0)}
    time.sleep(0.4)
top = sorted(seen.items(), key=lambda x: -x[1]["ratings"])[:40]
with open("candidates-competitors.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["app_id", "found_for_seed", "search_rank", "name", "genre", "rating_count"])
    for i, a in top:
        w.writerow([i, a["seed"], a["rank"], a["name"], a["genre"], a["ratings"]])
print("autocomplete rows:", sum(1 for _ in open("candidates-autocomplete.csv")) - 1, "| competitor apps:", len(top))

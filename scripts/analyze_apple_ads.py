#!/usr/bin/env python3
"""Filter an Apple Ads 'Monthly Search Term Popularity' CSV for terms matching a regex.
usage: analyze_apple_ads.py <report.csv> '<regex>' [min_popularity]"""
import csv, sys, re, collections
path, pat = sys.argv[1], re.compile(sys.argv[2], re.I)
minpop = int(sys.argv[3]) if len(sys.argv) > 3 else 0
lines = open(path, encoding="utf-8-sig").read().splitlines()
start = next(i for i, l in enumerate(lines) if l.startswith("Month,"))
rows = list(csv.DictReader(lines[start:]))
col = lambda name: next(k for k in rows[0] if k.strip().lower() == name.lower())
T, P, G, R = col("Search Term"), col("Search Popularity (1-100)"), col("Genre"), col("Rank in Genre")
best = {}
for r in rows:
    try: p = int(float(r[P]))
    except ValueError: continue
    t = r[T].strip().lower()
    if pat.search(t) and p >= minpop:
        if t not in best or p > best[t][0]: best[t] = (p, r[G], r[R])
print(f"{len(rows)} rows, {len(set(r[G] for r in rows))} genres, popularity {min(int(float(r[P])) for r in rows if r[P])}-{max(int(float(r[P])) for r in rows if r[P])}; {len(best)} matching terms")
for t, (p, g, rk) in sorted(best.items(), key=lambda x: -x[1][0]): print(f"{p:3d}  {t:40s} {g} #{rk}")

"""
Scrape the English-language feature-film index at IMDb
and save it to imdb_movies.xlsx
------------------------------------------------------
Requires:  pandas, beautifulsoup4, soupsieve, requests
           (all pip-installable)
Python ≥3.10 recommended.
"""

from __future__ import annotations
import re, time, random, requests, pandas as pd
from bs4 import BeautifulSoup

BASE = (
    "https://www.imdb.com/search/title/"
    "?title_type=feature&primary_language=en&start={start}&ref_=adv_nxt"
)

HEADERS = {
    # <- modern desktop Chrome UA (April 2025)
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.imdb.com/",
}

# -- Grab a fresh “session-id” cookie so Cloudflare is happy
s = requests.Session()
home = s.get("https://www.imdb.com/", headers=HEADERS, timeout=15)
if home.status_code != 200:
    raise SystemExit("IMDb home page not reachable – aborting.")

# ───────────────────────────────────────────────────────────────

records: list[dict[str, str]] = []

for start in range(1, 1000, 50):        # pages 1, 51, 101 … 951
    url = BASE.format(start=start)
    r = s.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        print(f"[{start:>4}] gave status {r.status_code} – stop scraping.")
        break

    soup = BeautifulSoup(r.text, "html.parser")

    # Every movie block carries both classes.
    for card in soup.select('div.lister-item.mode-advanced'):
        rec: dict[str, str] = {}

        # title
        rec["Title"] = card.h3.a.get_text(strip=True)

        # year – strip everything that isn't a digit or the NDASH between ranges
        y_tag = card.h3.select_one("span.lister-item-year")
        rec["Year"] = re.sub(r"[^\d–-]", "", y_tag.text) if y_tag else "NA"

        # runtime
        rt = card.select_one("p span.runtime")
        rec["Runtime"] = rt.text if rt else "NA"

        # genre
        gn = card.select_one("p span.genre")
        rec["Genre"] = gn.text.strip() if gn else "NA"

        # IMDb rating
        imdb = card.select_one("div.inline-block.ratings-imdb-rating > strong")
        rec["IMDb Rating"] = imdb.text if imdb else "NA"

        # metascore
        meta = card.select_one("span.metascore")
        rec["Metascore"] = meta.text.strip() if meta else "NA"

        # director – first <a> in the credits paragraph
        dir_a = card.select_one("p:has(a) a")
        rec["Director"] = dir_a.text if dir_a else "NA"

        # cast – remaining <a> tags in the same paragraph
        cast_as = card.select("p:has(a) a")[1:]
        rec["Cast"] = ", ".join(a.text for a in cast_as) or "NA"

        # votes
        nv = card.select_one('span[name="nv"]')
        rec["Votes"] = nv.text if nv else "NA"

        # description – second muted <p> block
        descs = card.select("p.text-muted")
        rec["Description"] = descs[1].get_text(strip=True) if len(descs) > 1 else "NA"

        records.append(rec)

    # polite, randomised delay (1.5–3 s)
    time.sleep(random.uniform(1.5, 3.0))

# ───────────────────────────────────────────────────────────────

if records:
    df = pd.DataFrame.from_records(records)
    df.to_excel("imdb_movies2.xlsx", index=False)
    print(f"Saved {len(df):,} rows to imdb_movies.xlsx")
else:
    print("No movie blocks found – check the selectors or your connection.")

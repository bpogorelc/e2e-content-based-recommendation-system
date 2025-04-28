import time                   # polite delay between requests
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup

# Pretend to be a real browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Storage lists
movie_name, year, runtime, genre = [], [], [], []
rating, metascore, director, cast = [], [], [], []
votes, description = [], []

# Page numbers 1, 51, 101, … 951   (IMDb shows 50 titles per page)
for start in range(1, 1000, 50):
    url = (
        "https://www.imdb.com/search/title/?"
        "title_type=feature&primary_language=en"
        f"&start={start}&ref_=adv_nxt"
    )
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        print(f"Stopped at start={start}, status={r.status_code}")
        break

    soup = BeautifulSoup(r.text, "html.parser")
    for item in soup.select("div.lister-item.mode-advanced"):
        #-- title
        movie_name.append(item.h3.a.get_text(strip=True))

        #-- year  (keep only digits & minus sign)
        y = item.h3.select_one("span.lister-item-year")
        year.append(re.sub(r"[^\d–-]", "", y.get_text()) if y else "NA")

        #-- runtime
        rt = item.p.select_one("span.runtime")
        runtime.append(rt.get_text(strip=True) if rt else "NA")

        #-- genre
        g = item.p.select_one("span.genre")
        genre.append(g.get_text(strip=True) if g else "NA")

        #-- IMDb rating
        rdiv = item.select_one("div.inline-block.ratings-imdb-rating > strong")
        rating.append(rdiv.get_text(strip=True) if rdiv else "NA")

        #-- metascore
        ms = item.select_one("span.metascore")
        metascore.append(ms.get_text(strip=True) if ms else "NA")

        #-- director
        dir_tag = item.select_one("p:has(a) a")
        director.append(dir_tag.get_text(strip=True) if dir_tag else "NA")

        #-- cast (second-plus <a> tags in the same <p>)
        cast_links = item.select("p:has(a) a")[1:]
        cast.append(", ".join(a.get_text(strip=True) for a in cast_links) or "NA")

        #-- votes / gross
        nv = item.select("span[name=nv]")
        votes.append(nv[0].get_text(strip=True) if nv else "NA")

        #-- description (second muted <p>)
        desc_p = item.select("p.text-muted")
        description.append(desc_p[1].get_text(strip=True) if len(desc_p) > 1 else "NA")

    # be polite – IMDb will throttle if you hammer it
    time.sleep(1.5)

# Assemble the dataframe
df = pd.DataFrame(
    {
        "Movie Name": movie_name,
        "Year": year,
        "Runtime": runtime,
        "Genre": genre,
        "IMDb Rating": rating,
        "Metascore": metascore,
        "Director": director,
        "Cast": cast,
        "Votes": votes,
        "Description": description,
    }
)

# Save to Excel
out_path = "imdb_movies.xlsx"
df.to_excel(out_path, index=False)
print(f"Saved {len(df)} rows to {out_path}")

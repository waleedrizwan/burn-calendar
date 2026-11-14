"""Download FIRMS yearly per-country hotspot CSVs for the pilot regions.

Run: uv run python -m burn.fetch_country
Files land in data/raw/country/<source>/<source>_<year>_<Country>.csv (not in git).
Re-running skips files whose size matches the server's.
"""
import sys
from concurrent.futures import ThreadPoolExecutor

import httpx

from burn.config import COUNTRY_SOURCES, LAST_COUNTRY_YEAR, RAW, REGIONS

BASE = "https://firms.modaps.eosdis.nasa.gov/data/country"
HEADERS = {"User-Agent": "burn-calendar/0.1 (NASA Space Apps hackathon project)"}


def jobs():
    for region in REGIONS.values():
        country = region["firms_country"]
        for source, (_, first) in COUNTRY_SOURCES.items():
            for year in range(first, LAST_COUNTRY_YEAR + 1):
                name = f"{source}_{year}_{country}.csv"
                yield f"{BASE}/{source}/{year}/{name}", RAW / "country" / source / name


def fetch(job):
    url, path = job
    path.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(headers=HEADERS, timeout=120, follow_redirects=True) as client:
        head = client.head(url)
        if head.status_code != 200:
            return f"MISSING {head.status_code} {path.name}"
        size = int(head.headers.get("content-length", -1))
        if path.exists() and path.stat().st_size == size:
            return f"have    {path.name}"
        tmp = path.with_suffix(".part")
        with client.stream("GET", url) as r, open(tmp, "wb") as f:
            r.raise_for_status()
            for chunk in r.iter_bytes(1 << 20):
                f.write(chunk)
        if size >= 0 and tmp.stat().st_size != size:
            return f"SHORT   {path.name}"
        tmp.rename(path)
        return f"got     {path.name} {size/1e6:.1f} MB"


def main():
    with ThreadPoolExecutor(4) as pool:
        bad = 0
        for line in pool.map(fetch, list(jobs())):
            print(line, flush=True)
            bad += line.startswith(("MISSING", "SHORT"))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

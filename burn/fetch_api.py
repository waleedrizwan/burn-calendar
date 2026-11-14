"""Download the current year's hotspots from the FIRMS Area API, in 5-day windows.

Run: uv run python -m burn.fetch_api
Needs FIRMS_MAP_KEY in the environment, ./.env or ~/.config/nasa-burn/.env.
Standard-processing (_SP) data are used up to their last date and near real-time (_NRT) after.
Files land in data/raw/api/<region>/<SOURCE>/<start>_<days>.csv. Finished windows are not
re-fetched; windows touching the last 7 days are always refreshed.
"""
import datetime as dt
import io
import os
import sys
import time
from pathlib import Path

import httpx
import pandas as pd
from dotenv import load_dotenv

from burn.config import API_SOURCES, CURRENT_YEAR, RAW, REGIONS, ROOT

API = "https://firms.modaps.eosdis.nasa.gov/api"


def map_key() -> str:
    load_dotenv(ROOT / ".env")
    load_dotenv(Path.home() / ".config" / "nasa-burn" / ".env")
    key = os.environ.get("FIRMS_MAP_KEY", "").strip()
    if not key:
        sys.exit("FIRMS_MAP_KEY is not set (see .env.example)")
    return key


def availability(client, key):
    r = client.get(f"{API}/data_availability/csv/{key}/ALL")
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    return {row.data_id: (dt.date.fromisoformat(row.min_date), dt.date.fromisoformat(row.max_date))
            for row in df.itertuples()}


def wait_for_quota(client, key, need=30):
    while True:
        s = client.get("https://firms.modaps.eosdis.nasa.gov/mapserver/mapkey_status/",
                       params={"MAP_KEY": key}).json()
        if s["transaction_limit"] - s["current_transactions"] > need:
            return
        print("  quota nearly used, waiting 60 s", flush=True)
        time.sleep(60)


def windows(start, end, days=5):
    d = start
    while d <= end:
        n = min(days, (end - d).days + 1)
        yield d, n
        d += dt.timedelta(days=n)


def main():
    key = map_key()
    today = dt.datetime.now(dt.timezone.utc).date()
    with httpx.Client(timeout=180) as client:
        avail = availability(client, key)
        for rid, region in REGIONS.items():
            bbox = ",".join(str(v) for v in region["bbox"])
            for prefix in API_SOURCES:
                sp_end = avail[f"{prefix}_SP"][1]
                nrt_end = min(avail[f"{prefix}_NRT"][1], today)
                spans = [(f"{prefix}_SP", dt.date(CURRENT_YEAR, 1, 1), sp_end),
                         (f"{prefix}_NRT", max(sp_end + dt.timedelta(days=1), dt.date(CURRENT_YEAR, 1, 1)), nrt_end)]
                for source, start, end in spans:
                    out = RAW / "api" / rid / source
                    out.mkdir(parents=True, exist_ok=True)
                    rows = 0
                    for i, (d, n) in enumerate(windows(start, end)):
                        path = out / f"{d}_{n}.csv"
                        fresh = (today - (d + dt.timedelta(days=n - 1))).days <= 7
                        if path.exists() and not fresh:
                            continue
                        if i % 3 == 0:
                            wait_for_quota(client, key)
                        for attempt in range(4):
                            r = client.get(f"{API}/area/csv/{key}/{source}/{bbox}/{n}/{d}")
                            if r.status_code == 200 and r.text.startswith("latitude"):
                                break
                            time.sleep(15 * (attempt + 1))
                        else:
                            sys.exit(f"failed {rid} {source} {d}: {r.status_code} {r.text[:80]}")
                        path.write_text(r.text)
                        rows += r.text.count("\n") - 1
                    print(f"{rid} {source} {start}..{end}: fetched {rows} new rows", flush=True)


if __name__ == "__main__":
    main()

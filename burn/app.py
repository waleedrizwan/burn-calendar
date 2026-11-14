"""Web app entry point. Run: uv run uvicorn burn.app:app --reload

The API contract is documented in docs/api.md.
"""
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles

from burn.config import REGIONS, ROOT
from burn.db import con

app = FastAPI(title="Harmonized Burning Activity Calendar")

SERIES = {
    "modis_raw": {
        "harmonized": False,
        "unit": {
            "id": "modis_detections",
            "label": "MODIS hotspot detections (unharmonized)",
            "description": "Count of MODIS Collection 6.1 active fire detections (Terra and Aqua, "
                           "all confidence levels, presumed vegetation fires and unclassified). "
                           "Raw counts from one sensor: not yet harmonized with VIIRS.",
        },
    },
}


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/regions")
def regions() -> dict:
    return {"regions": [{"id": rid, "name": r["name"], "regime": r["regime"],
                         "bbox": list(r["bbox"])} for rid, r in REGIONS.items()]}


@lru_cache(maxsize=64)
def _calendar(region: str, series: str) -> dict:
    rows = con().execute(
        """
        select year(acq_datetime) y, month(acq_datetime) m, count(*) n,
               max(cast(acq_datetime as date)) last_day, bool_or(quality = 'NRT') nrt
        from hotspots
        where region = ? and sensor = 'MODIS' and (type is null or type = 0)
        group by 1, 2 order by 1, 2
        """, [region]).fetchall()
    if not rows:
        raise HTTPException(503, "no data loaded for this region")
    last = max(r[3] for r in rows)
    have = {(y, m): (n, nrt) for y, m, n, _, nrt in rows}
    cells = []
    y, m = rows[0][0], rows[0][1]
    while (y, m) <= (last.year, last.month):
        n, nrt = have.get((y, m), (0, False))
        cells.append({"year": y, "month": m, "value": n,
                      "partial": (y, m) == (last.year, last.month), "provisional": bool(nrt)})
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    spec = SERIES[series]
    return {
        "region": region,
        "area": {"type": "region", "name": REGIONS[region]["name"], "bbox": list(REGIONS[region]["bbox"])},
        "series": series,
        "harmonized": spec["harmonized"],
        "unit": spec["unit"],
        "period": {"start": f"{cells[0]['year']}-{cells[0]['month']:02d}",
                   "end": f"{last.year}-{last.month:02d}", "last_data_date": str(last)},
        "time_basis": "UTC",
        "cells": cells,
    }


@app.get("/api/calendar")
def calendar(region: str = Query("canada"), series: str = Query("modis_raw")) -> dict:
    if region not in REGIONS:
        raise HTTPException(404, f"unknown region '{region}'")
    if series not in SERIES:
        raise HTTPException(404, f"unknown series '{series}'")
    return _calendar(region, series)


app.mount("/", StaticFiles(directory=ROOT / "web", html=True), name="web")

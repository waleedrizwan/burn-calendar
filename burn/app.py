"""Web app entry point. Run: uv run uvicorn burn.app:app --reload

The API contract is documented in docs/api.md.
"""
import csv
import datetime as dt
import io
import re
from functools import lru_cache

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from burn import analytics
from burn.config import GRID_DEG, HOTSPOTS, REGIONS, ROOT
from burn.db import con

app = FastAPI(title="Harmonized Burning Activity Calendar")

MAX_EXPORT_ROWS = 500_000
MODIS_RAW_UNIT = {
    "id": "modis_detections",
    "label": "MODIS hotspot detections (unharmonized)",
    "short": "detections",
    "description": "Count of MODIS Collection 6.1 active fire detections (Terra and Aqua, all confidence "
                   "levels, presumed vegetation fires). Raw counts from one sensor family: not harmonized with VIIRS.",
}
YM = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
YMD = re.compile(r"^\d{4}-\d{2}-\d{2}$")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/regions")
def regions() -> dict:
    return {"regions": [{"id": rid, "name": r["name"], "regime": r["regime"],
                         "bbox": list(r["bbox"])} for rid, r in REGIONS.items()]}


def _area(region, bbox, lat, lon, radius_km) -> dict:
    try:
        return analytics.parse_area(region, bbox, lat, lon, radius_km)
    except analytics.AreaError as e:
        raise HTTPException(404 if "unknown region" in str(e) else 422, str(e)) from None


@lru_cache(maxsize=16)
def _modis_raw(region: str) -> dict:
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
    return {
        "region": region,
        "area": {"type": "region", "name": REGIONS[region]["name"], "bbox": list(REGIONS[region]["bbox"])},
        "series": "modis_raw", "harmonized": False, "unit": MODIS_RAW_UNIT,
        "period": {"start": f"{cells[0]['year']}-{cells[0]['month']:02d}",
                   "end": f"{last.year}-{last.month:02d}", "last_data_date": str(last)},
        "time_basis": "UTC", "warnings": [], "cells": cells,
    }


@lru_cache(maxsize=256)
def _calendar(region, bbox, lat, lon, radius_km, start, end) -> dict:
    area = _area(region, bbox, lat, lon, radius_km)
    try:
        return analytics.calendar(region, area, start, end)
    except LookupError as e:
        raise HTTPException(503, str(e)) from None


@app.get("/api/calendar")
def calendar(region: str = Query("canada"), series: str = Query("harmonized"),
             bbox: str | None = None, lat: float | None = None, lon: float | None = None,
             radius_km: float | None = None, start: str | None = None, end: str | None = None) -> dict:
    for name, v in (("start", start), ("end", end)):
        if v and not YM.match(v):
            raise HTTPException(422, f"{name} must be YYYY-MM")
    if start and end and start > end:
        raise HTTPException(422, "start must not be after end")
    if series == "modis_raw":
        if region not in REGIONS:
            raise HTTPException(404, f"unknown region '{region}'")
        if bbox or lat is not None or lon is not None or radius_km is not None:
            raise HTTPException(422, "series=modis_raw is available for whole regions only")
        return _modis_raw(region)
    if series != "harmonized":
        raise HTTPException(404, f"unknown series '{series}'; use harmonized or modis_raw")
    if not analytics.data_available():
        raise HTTPException(503, "harmonized data are not loaded")
    return _calendar(region, bbox, lat, lon, radius_km, start, end)


def _csv_response(header_lines, columns, rows_iter, filename):
    def gen():
        buf = io.StringIO()
        for line in header_lines:
            buf.write(f"# {line}\n")
        w = csv.writer(buf)
        w.writerow(columns)
        for chunk in rows_iter:
            w.writerows(chunk)
            yield buf.getvalue()
            buf.seek(0); buf.truncate()
        yield buf.getvalue()
    return StreamingResponse(gen(), media_type="text/csv",
                             headers={"Content-Disposition": f'attachment; filename="{filename}"'})


def _area_text(area: dict) -> str:
    if area["type"] == "bbox":
        return "bbox west,south,east,north = " + ",".join(str(v) for v in area["bbox"])
    if area["type"] == "circle":
        return f"circle lat {area['lat']}, lon {area['lon']}, radius {area['radius_km']} km"
    return f"whole region {area['name']}"


@app.get("/api/calendar.csv")
def calendar_csv(region: str = Query("canada"), bbox: str | None = None, lat: float | None = None,
                 lon: float | None = None, radius_km: float | None = None,
                 start: str | None = None, end: str | None = None):
    d = calendar(region, "harmonized", bbox, lat, lon, radius_km, start, end)
    base = {b["month"]: b for b in d["baseline"]}
    cols = ["year", "month", "burning_activity_cell_days", "baseline_median", "baseline_p25", "baseline_p75",
            "percentile", "ratio_to_median", "category", "partial", "provisional", "sources",
            "lower_confidence", "gap_days"]
    rows = [[c["year"], c["month"], c["value"], base.get(c["month"], {}).get("median"),
             base.get(c["month"], {}).get("p25"), base.get(c["month"], {}).get("p75"),
             c["percentile"], c["ratio_to_median"], c["category"], c["partial"], c["provisional"],
             "+".join(c["sources"]), c["lower_confidence"], c["gap_days"]] for c in d["cells"]]
    head = ["Harmonized Burning Activity Calendar: monthly table",
            f"Region: {REGIONS[region]['name']}; area: {_area_text(d['area'])}",
            f"Unit: {d['unit']['description']}",
            f"Months are UTC. Data through {d['period']['last_data_date']}. Harmonization version {d['harmonization_version']}.",
            "Baseline: the same calendar month in every complete year from 2001 to last year.",
            "Source: NASA FIRMS, MODIS Collection 6.1 and VIIRS 375 m active fire detections."]
    return _csv_response(head, cols, [rows], f"burning_activity_{region}.csv")


@app.get("/api/hotspots.csv")
def hotspots_csv(region: str = Query("canada"), bbox: str | None = None, lat: float | None = None,
                 lon: float | None = None, radius_km: float | None = None,
                 start: str = Query(..., description="YYYY-MM-DD"), end: str = Query(..., description="YYYY-MM-DD")):
    if not (YMD.match(start) and YMD.match(end)):
        raise HTTPException(422, "start and end must be YYYY-MM-DD")
    try:
        d0, d1 = dt.date.fromisoformat(start), dt.date.fromisoformat(end)
    except ValueError:
        raise HTTPException(422, "start and end must be valid dates") from None
    if d0 > d1:
        raise HTTPException(422, "start must not be after end")
    area = _area(region, bbox, lat, lon, radius_km)
    pred, args, _ = analytics.cell_filter(area)
    g = GRID_DEG
    where = (f"region = ? and year between ? and ? and acq_datetime >= ? and acq_datetime < ? and {pred}")
    params = [region, d0.year, d1.year, d0, d1 + dt.timedelta(days=1)] + args
    src = (f"(select *, cast(floor(longitude / {g}) as integer) ix, cast(floor(latitude / {g}) as integer) iy "
           f"from hotspots)")
    c = con()
    n = c.execute(f"select count(*) from {src} where {where}", params).fetchone()[0]
    if n > MAX_EXPORT_ROWS:
        raise HTTPException(413, f"the search matches {n:,} hotspot detections; the limit for one download is "
                                 f"{MAX_EXPORT_ROWS:,}. Choose a smaller area or a shorter period.")
    cols = ["latitude", "longitude", "acq_datetime_utc", "sensor", "satellite", "confidence", "confidence_pct",
            "frp_mw", "daynight", "type", "brightness_k", "scan_km", "track_km", "quality", "version"]
    res = c.execute(
        f"select latitude, longitude, strftime(acq_datetime, '%Y-%m-%d %H:%M'), sensor, satellite, confidence, "
        f"confidence_pct, round(cast(frp as double), 2), daynight, type, round(cast(brightness as double), 2), "
        f"round(cast(scan as double), 2), round(cast(track as double), 2), quality, version "
        f"from {src} where {where} order by acq_datetime", params)

    def chunks():
        while True:
            rows = res.fetchmany(20000)
            if not rows:
                return
            yield rows
    head = ["Harmonized Burning Activity Calendar: hotspot detections in the search (all sensors, unfiltered)",
            f"Region: {REGIONS[region]['name']}; area: {_area_text(area)}; grid cells whose centre is in the area",
            f"Period: {start} to {end} (UTC); {n} rows",
            "type: 0 presumed vegetation fire, 1 volcano, 2 other static land source, 3 offshore, empty for near real-time data.",
            "The calendar counts only type 0 (and near real-time rows outside known static sources). A detection is not a fire.",
            "Source: NASA FIRMS, MODIS Collection 6.1 and VIIRS 375 m (S-NPP, NOAA-20) active fire detections."]
    return _csv_response(head, cols, chunks(), f"hotspots_{region}_{start}_{end}.csv")


app.mount("/", StaticFiles(directory=ROOT / "web", html=True), name="web")

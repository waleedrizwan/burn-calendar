"""Area queries and calendar statistics. Definitions: docs/metrics.md. Contract: docs/api.md."""
import datetime as dt
import json
import math
import threading

import duckdb
import numpy as np
import pandas as pd

from burn.config import GRID_DEG, HARMONIZED, PARAMS_FILE, REGIONS

LOW_ACTIVITY = 5.0          # baseline median below this: no ratio, no category
MAX_RADIUS_KM = 2000.0
UNIT = {
    "id": "viirs_equivalent_active_cell_days",
    "label": "Burning activity (VIIRS-equivalent active cell-days)",
    "short": "active cell-days",
    "description": "Number of 0.1 degree grid cells (about 11 km) times days with at least one "
                   "vegetation-fire hotspot detection, on the scale of the VIIRS S-NPP sensor. "
                   "Years before 2012 are converted from MODIS with factors measured while both sensors flew.",
}
SOURCE_LABEL = {"SNPP": "VIIRS S-NPP", "NOAA20": "VIIRS NOAA-20", "MODIS_TA": "MODIS Terra+Aqua",
                "MODIS_T": "MODIS Terra only", "MODIS_A": "MODIS Aqua only", "NONE": "no data"}

_lock = threading.Lock()
_db = None


class AreaError(ValueError):
    pass


def db() -> duckdb.DuckDBPyConnection:
    """One in-memory database holding the harmonized grid; a cursor per call is thread-safe."""
    global _db
    with _lock:
        if _db is None:
            con = duckdb.connect()
            con.execute(f"create table harm as select region, date, ix, iy, value, nrt from "
                        f"read_parquet('{HARMONIZED}/*/*/data.parquet', hive_partitioning=true)")
            con.execute(f"create table day_source as select * from read_parquet('{HARMONIZED}/day_source.parquet')")
            _db = con
    return _db.cursor()


def data_available() -> bool:
    return (HARMONIZED / "day_source.parquet").exists()


def params_version() -> str:
    return json.loads(PARAMS_FILE.read_text())["harmonization"]["version"]


# ---------- area ----------

def parse_area(region: str, bbox: str | None, lat: float | None, lon: float | None, radius_km: float | None) -> dict:
    if region not in REGIONS:
        raise AreaError(f"unknown region '{region}'; choose one of {', '.join(REGIONS)}")
    rw, rs, re_, rn = REGIONS[region]["bbox"]
    if bbox and (lat is not None or lon is not None or radius_km is not None):
        raise AreaError("give either bbox or lat, lon and radius_km, not both")
    if bbox:
        try:
            w, s, e, n = (float(v) for v in bbox.split(","))
        except ValueError:
            raise AreaError("bbox must be four numbers: west,south,east,north") from None
        if not (-180 <= w < e <= 180 and -90 <= s < n <= 90):
            raise AreaError("bbox must satisfy -180 <= west < east <= 180 and -90 <= south < north <= 90")
        if e < rw or w > re_ or n < rs or s > rn:
            raise AreaError(f"the area is outside {REGIONS[region]['name']}; data are loaded for the pilot regions only")
        return {"type": "bbox", "bbox": [w, s, e, n]}
    if lat is not None or lon is not None or radius_km is not None:
        if lat is None or lon is None or radius_km is None:
            raise AreaError("a circle needs lat, lon and radius_km")
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise AreaError("lat must be between -90 and 90 and lon between -180 and 180")
        if not (0 < radius_km <= MAX_RADIUS_KM):
            raise AreaError(f"radius_km must be above 0 and at most {MAX_RADIUS_KM:.0f}")
        if not (rw <= lon <= re_ and rs <= lat <= rn):
            raise AreaError(f"the point is outside {REGIONS[region]['name']}; data are loaded for the pilot regions only")
        return {"type": "circle", "lat": lat, "lon": lon, "radius_km": radius_km}
    return {"type": "region", "name": REGIONS[region]["name"], "bbox": list(REGIONS[region]["bbox"])}


def cell_filter(area: dict) -> tuple[str, list, list[str]]:
    """SQL predicate on (ix, iy) selecting the cells whose centre lies in the area."""
    g, warnings = GRID_DEG, []
    if area["type"] == "region":
        return "true", [], warnings
    if area["type"] == "bbox":
        w, s, e, n = area["bbox"]
        x0, x1 = math.ceil(w / g - 0.5), math.floor(e / g - 0.5)
        y0, y1 = math.ceil(s / g - 0.5), math.floor(n / g - 0.5)
        if x1 < x0 or y1 < y0 or (e - w) < g or (n - s) < g:
            cx, cy = math.floor((w + e) / 2 / g), math.floor((s + n) / 2 / g)
            x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
            warnings.append("The area is smaller than one 0.1 degree grid cell (about 11 km) in at least one "
                            "direction. Results are for the whole grid cell(s) that contain it.")
        area["cells"] = (x1 - x0 + 1) * (y1 - y0 + 1)
        return "ix between ? and ? and iy between ? and ?", [x0, x1, y0, y1], warnings
    lat, lon, r = area["lat"], area["lon"], area["radius_km"]
    dlat = r / 111.2
    dlon = r / (111.2 * max(0.05, math.cos(math.radians(lat))))
    pred = ("iy between ? and ? and ix between ? and ? and "
            "2 * 6371.0 * asin(sqrt(pow(sin(radians((iy + 0.5) * ? - ?) / 2), 2) + cos(radians(?)) * "
            "cos(radians((iy + 0.5) * ?)) * pow(sin(radians((ix + 0.5) * ? - ?) / 2), 2))) <= ?")
    args = [math.floor((lat - dlat) / g), math.floor((lat + dlat) / g), math.floor((lon - dlon) / g),
            math.floor((lon + dlon) / g), g, lat, lat, g, g, lon, r]
    if r < 111.2 * g * 0.71:  # circle may contain no cell centre
        cx, cy = math.floor(lon / g), math.floor(lat / g)
        pred, args = f"(({pred}) or (ix = ? and iy = ?))", args + [cx, cy]
        warnings.append("The radius is smaller than one 0.1 degree grid cell (about 11 km). Results are for "
                        "the whole grid cell that contains the point.")
    return pred, args, warnings


def daily_series(region: str, area: dict) -> tuple[pd.DataFrame, list[str]]:
    """Daily harmonized value for the area on a complete day index, plus the region's day sources."""
    pred, args, warnings = cell_filter(area)
    cur = db()
    src = cur.execute("select date, source from day_source where region = ? order by date", [region]).df()
    if src.empty:
        raise LookupError("no data loaded for this region")
    val = cur.execute(f"select date, sum(value) v, bool_or(nrt) nrt from harm where region = ? and {pred} "
                      "group by date", [region] + args).df()
    df = src.merge(val, on="date", how="left")
    df["v"] = df["v"].fillna(0.0)
    df["nrt"] = df["nrt"].fillna(False).astype(bool)
    df["date"] = pd.to_datetime(df["date"])
    df["y"], df["m"], df["d"] = df["date"].dt.year, df["date"].dt.month, df["date"].dt.day
    return df, warnings


# ---------- statistics ----------

def percentile_rank(value: float, base: np.ndarray) -> float:
    return float(100.0 * ((base < value).sum() + 0.5 * (base == value).sum()) / len(base))


def categorize(value: float, base: np.ndarray) -> dict:
    """Anomaly of one value against its baseline sample (docs/metrics.md)."""
    if len(base) < 5:
        return {"percentile": None, "ratio_to_median": None, "category": "no_baseline"}
    med = float(np.median(base))
    record = value > base.max()
    if med < LOW_ACTIVITY:
        cat = "record_high" if (record and value >= LOW_ACTIVITY) else "low_activity"
        return {"percentile": None, "ratio_to_median": None, "category": cat}
    p = percentile_rank(value, base)
    if record:
        cat = "record_high"
    elif p >= 90:
        cat = "well_above"
    elif p >= 75:
        cat = "above"
    elif p > 25:
        cat = "near_normal"
    elif p > 10:
        cat = "below"
    else:
        cat = "well_below"
    return {"percentile": round(p, 1), "ratio_to_median": round(value / med, 2), "category": cat}


def mann_kendall_theil_sen(years: np.ndarray, values: np.ndarray) -> dict:
    n = len(values)
    if n < 8:
        return {"available": False}
    s, slopes = 0, []
    for i in range(n - 1):
        diff = values[i + 1:] - values[i]
        s += int(np.sign(diff).sum())
        slopes.extend(diff / (years[i + 1:] - years[i]))
    _, counts = np.unique(values, return_counts=True)
    var = (n * (n - 1) * (2 * n + 5) - sum(c * (c - 1) * (2 * c + 5) for c in counts)) / 18
    z = 0.0 if s == 0 or var == 0 else (s - np.sign(s)) / math.sqrt(var)
    p = math.erfc(abs(z) / math.sqrt(2))
    slope, med = float(np.median(slopes)), float(np.median(values))
    return {"available": True, "start_year": int(years[0]), "end_year": int(years[-1]),
            "slope_per_year": round(slope, 2),
            "percent_per_decade": round(1000 * slope / med, 1) if med >= LOW_ACTIVITY else None,
            "p_value": round(p, 4), "significant": bool(p <= 0.05),
            "direction": "none" if p > 0.05 else ("up" if slope > 0 else "down")}


def calendar(region: str, area: dict, start: str | None = None, end: str | None = None) -> dict:
    df, warnings = daily_series(region, area)
    last = df["date"].max()
    cur_y, cur_m, cur_d = last.year, last.month, last.day
    month_end = (last + pd.offsets.MonthEnd(0)).day
    partial_now = cur_d < month_end
    base_years = [y for y in range(2001, cur_y)]

    g = df.groupby(["y", "m"])
    monthly = g["v"].sum()
    flags = pd.DataFrame({
        "provisional": g["nrt"].any(),
        "gap_days": g["source"].apply(lambda s: int((s == "NONE").sum())),
        "lower_confidence": g["source"].apply(lambda s: bool(s.isin(["MODIS_T", "MODIS_A"]).any())),
        "sources": g["source"].apply(lambda s: [x for x in ("MODIS_T", "MODIS_A", "MODIS_TA", "SNPP", "NOAA20") if (s == x).any()]),
    })
    if monthly.sum() == 0:
        warnings.append("No hotspot detections were recorded in this area in the whole record.")

    # baseline per calendar month (full months, complete years)
    baseline, base_by_month = [], {}
    for m in range(1, 13):
        ys = [y for y in base_years if (y, m) in monthly.index]
        vals = np.array([monthly[(y, m)] for y in ys], dtype=float)
        base_by_month[m] = (ys, vals)
        if len(vals):
            p10, p25, p50, p75, p90 = np.percentile(vals, [10, 25, 50, 75, 90])
            baseline.append({"month": m, "n_years": len(vals), "median": round(float(p50), 1),
                             "p10": round(float(p10), 1), "p25": round(float(p25), 1), "p75": round(float(p75), 1),
                             "p90": round(float(p90), 1), "min": round(float(vals.min()), 1),
                             "max": round(float(vals.max()), 1), "mean": round(float(vals.mean()), 1)})

    lo = tuple(int(x) for x in start.split("-")) if start else (0, 0)
    hi = tuple(int(x) for x in end.split("-")) if end else (9999, 12)
    cells = []
    for (y, m), v in monthly.items():
        if not (lo <= (y, m) <= hi):
            continue
        is_partial = partial_now and (y, m) == (cur_y, cur_m)
        f = flags.loc[(y, m)]
        cell = {"year": int(y), "month": int(m), "value": round(float(v), 1), "partial": bool(is_partial),
                "provisional": bool(f["provisional"]), "sources": f["sources"],
                "lower_confidence": bool(f["lower_confidence"]), "gap_days": int(f["gap_days"])}
        if is_partial:
            cell.update({"percentile": None, "ratio_to_median": None, "category": "partial"})
        else:
            ys, vals = base_by_month[m]
            cell.update(categorize(float(v), vals[np.array(ys) != y] if len(ys) else vals))
        cells.append(cell)

    # current month, like for like: days 1..d in every baseline year
    to_date = df[(df["m"] == cur_m) & (df["d"] <= cur_d)].groupby("y")["v"].sum()
    base_td = np.array([to_date.get(y, 0.0) for y in base_years], dtype=float)
    now_v = float(to_date.get(cur_y, 0.0))
    current = {"year": cur_y, "month": cur_m, "through_day": cur_d, "complete": not partial_now,
               "value": round(now_v, 1),
               "baseline_years": [base_years[0], base_years[-1]],
               "baseline_median_to_date": round(float(np.median(base_td)), 1),
               "baseline_p25_to_date": round(float(np.percentile(base_td, 25)), 1),
               "baseline_p75_to_date": round(float(np.percentile(base_td, 75)), 1),
               "baseline_max_to_date": round(float(base_td.max()), 1),
               "rank": int((base_td > now_v).sum()) + 1, "of": len(base_td) + 1,
               "provisional": bool(df[(df["y"] == cur_y) & (df["m"] == cur_m)]["nrt"].any()),
               **categorize(now_v, base_td)}

    annual = df.groupby("y")["v"].sum()
    years = [{"year": int(y), "total": round(float(v), 1),
              "partial": bool(y == cur_y and (cur_m, cur_d) != (12, 31)) or y == 2000} for y, v in annual.items()]
    ty = np.array([y for y in annual.index if 2003 <= y < cur_y])
    trend = mann_kendall_theil_sen(ty.astype(float), annual.loc[ty].to_numpy(float))

    first = df["date"].min()
    return {
        "region": region, "area": area, "series": "harmonized", "harmonized": True, "unit": UNIT,
        "harmonization_version": params_version(),
        "period": {"start": f"{first.year}-{first.month:02d}", "end": f"{cur_y}-{cur_m:02d}",
                   "last_data_date": str(last.date())},
        "time_basis": "UTC", "warnings": warnings, "cells": cells, "baseline": baseline,
        "current": current, "years": years, "trend": trend, "source_labels": SOURCE_LABEL,
    }

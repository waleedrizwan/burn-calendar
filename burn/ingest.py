"""Normalize raw FIRMS files to one schema and store them as Parquet.

Run: uv run python -m burn.ingest            (all regions, all sources)
Input:  data/raw/country/...  (burn.fetch_country)  and  data/raw/api/...  (burn.fetch_api)
Output: data/processed/hotspots/region=<id>/source=<src>/year=<yyyy>/data.parquet
Each run rewrites the partitions it touches, so re-running creates no duplicates.
The schema is documented in docs/schema.md.
"""
import shutil

import duckdb

from burn.config import (API_SOURCES, BOUNDARIES, COUNTRY_SOURCES, CURRENT_YEAR, HOTSPOTS,
                         RAW, REGIONS)

CSV_TYPES = ("types={'confidence':'VARCHAR','version':'VARCHAR','satellite':'VARCHAR',"
             "'acq_time':'VARCHAR','acq_date':'DATE'}")

# One SELECT turns either sensor's raw columns into the common schema.
NORMALIZE = """
select
    cast(latitude as double)  as latitude,
    cast(longitude as double) as longitude,
    cast(acq_date as timestamp)
        + to_minutes(cast(lpad(acq_time, 4, '0')[1:2] as int) * 60 + cast(lpad(acq_time, 4, '0')[3:4] as int))
        as acq_datetime,
    instrument as sensor,
    case satellite when 'T' then 'Terra' when 'A' then 'Aqua' when 'N' then 'SNPP'
                   when 'N20' then 'NOAA20' when 'N21' then 'NOAA21' else satellite end as satellite,
    case when instrument = 'MODIS' then
              case when try_cast(confidence as int) < 30 then 'l'
                   when try_cast(confidence as int) < 80 then 'n' else 'h' end
         else lower(confidence[1:1]) end as confidence,
    case when instrument = 'MODIS' then try_cast(confidence as utinyint) end as confidence_pct,
    cast(frp as float) as frp,
    daynight,
    {type_expr} as type,
    cast({bright} as float) as brightness,
    cast(scan as float) as scan,
    cast(track as float) as track,
    case when version ilike '%RT' then 'NRT' else 'SP' end as quality,
    version
from {src}
"""


def write(con, select_sql, region, source, label):
    out = HOTSPOTS / f"region={region}" / f"source={source}"
    con.execute(f"create or replace temp table t as {select_sql}")
    years = [r[0] for r in con.execute("select distinct year(acq_datetime) from t order by 1").fetchall()]
    for y in years:
        d = out / f"year={y}"
        d.mkdir(parents=True, exist_ok=True)
        con.execute(f"copy (select * from t where year(acq_datetime) = {y} order by acq_datetime) "
                    f"to '{d}/data.parquet' (format parquet, compression zstd)")
    for (y, n) in con.execute("select year(acq_datetime), count(*) from t group by 1 order by 1").fetchall():
        print(f"{region:8s} {source:12s} {y} {n:>9,d}  ({label})", flush=True)


def main():
    con = duckdb.connect()
    con.execute("install spatial; load spatial;")
    for rid, region in REGIONS.items():
        country = region["firms_country"]
        for source in COUNTRY_SOURCES:
            bright = "brightness" if source == "modis" else "bright_ti4"
            # 1. history from the yearly per-country files
            files = RAW / "country" / source / f"{source}_*_{country}.csv"
            src = f"read_csv('{files}', union_by_name=true, {CSV_TYPES})"
            n_src = con.execute(f"select count(*) from {src}").fetchone()[0]
            hist = HOTSPOTS / f"region={rid}" / f"source={source}"
            if hist.exists():
                shutil.rmtree(hist)
            write(con, NORMALIZE.format(src=src, bright=bright, type_expr="cast(type as utinyint)"),
                  rid, source, "country file")
            n_out = con.execute(
                f"select count(*) from read_parquet('{hist}/*/data.parquet')").fetchone()[0]
            assert n_src == n_out, (rid, source, n_src, n_out)
            print(f"{rid:8s} {source:12s} total {n_out:,d} rows = source rows", flush=True)

            # 2. current year from the Area API, clipped to the country polygon
            prefix = next(p for p, s in API_SOURCES.items() if s == source)
            api_files = list((RAW / "api" / rid).glob(f"{prefix}_*/*.csv"))
            if not api_files:
                print(f"{rid:8s} {source:12s} no API files for {CURRENT_YEAR}", flush=True)
                continue
            glob = RAW / "api" / rid / f"{prefix}_*" / "*.csv"
            src = (f"(select h.* from read_csv('{glob}', union_by_name=true, {CSV_TYPES}) h, "
                   f"(select geom from st_read('{BOUNDARIES}') where ADMIN = '{country}') b "
                   f"where st_contains(b.geom, st_point(h.longitude, h.latitude)))")
            cols = [r[0] for r in con.execute(
                f"describe select * from read_csv('{glob}', union_by_name=true, {CSV_TYPES})").fetchall()]
            type_expr = "try_cast(type as utinyint)" if "type" in cols else "cast(null as utinyint)"
            write(con, NORMALIZE.format(src=src, bright=bright, type_expr=type_expr)
                  + f" where year(acq_date) = {CURRENT_YEAR}", rid, source, "area API, clipped")


if __name__ == "__main__":
    main()

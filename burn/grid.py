"""Filter hotspots and aggregate them to (grid cell, UTC day, satellite, day/night).

Run: uv run python -m burn.grid
Output: data/processed/cellday/region=<id>/year=<yyyy>/data.parquet with columns
    date, ix, iy, satellite, daynight, n (detections), frp (sum, MW), nrt (any near real-time row)

Filters (docs/sensor-differences.md):
  - standard-quality rows: keep type = 0 (presumed vegetation fire) only;
  - near real-time rows (no type): drop rows inside a static-source cell, i.e. a 0.01 degree cell
    with at least STATIC_MIN type 2/3 detections anywhere in the standard record.
"""
import shutil

from burn.config import CELLDAY, GRID_DEG, REGIONS, STATIC_DEG, STATIC_MIN
from burn.db import con

FILTERED = f"""
select h.* from hotspots h
left join static s
  on s.region = h.region and s.sx = floor(h.longitude / {STATIC_DEG}) and s.sy = floor(h.latitude / {STATIC_DEG})
where h.type = 0 or (h.type is null and s.sx is null)
"""


def build_static(c):
    c.execute(f"""
        create or replace temp table static as
        select region, floor(longitude / {STATIC_DEG}) sx, floor(latitude / {STATIC_DEG}) sy
        from hotspots where type in (1, 2, 3)
        group by all having count(*) >= {STATIC_MIN}""")


def main():
    c = con()
    build_static(c)
    c.execute(f"create or replace temp view filtered as {FILTERED}")
    for rid in REGIONS:
        out = CELLDAY / f"region={rid}"
        if out.exists():
            shutil.rmtree(out)
        years = [r[0] for r in c.execute(
            "select distinct year from hotspots where region = ? order by 1", [rid]).fetchall()]
        total = 0
        for y in years:
            (out / f"year={y}").mkdir(parents=True)
            c.execute(f"""
                copy (
                  select cast(acq_datetime as date) as date,
                         cast(floor(longitude / {GRID_DEG}) as integer) as ix,
                         cast(floor(latitude / {GRID_DEG}) as integer) as iy,
                         satellite, daynight,
                         cast(count(*) as integer) as n, cast(sum(frp) as float) as frp,
                         bool_or(quality = 'NRT') as nrt
                  from filtered where region = '{rid}' and year = {y}
                  group by all order by date, ix, iy
                ) to '{out}/year={y}/data.parquet' (format parquet, compression zstd)""")
        points, cells = c.execute(
            f"select (select count(*) from filtered where region = '{rid}'), "
            f"(select sum(n) from read_parquet('{out}/*/data.parquet'))").fetchone()
        rows = c.execute(f"select count(*) from read_parquet('{out}/*/data.parquet')").fetchone()[0]
        assert points == cells, (rid, points, cells)
        print(f"{rid}: {points:,d} filtered detections -> {rows:,d} cell-day rows (sums match)", flush=True)


if __name__ == "__main__":
    main()

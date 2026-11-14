"""Harmonize MODIS and VIIRS into VIIRS-equivalent active cell-days (docs/unit-decision.md).

Run: uv run python -m burn.harmonize            fit on the overlap, apply to the full record, write Parquet
Input:  data/processed/cellday (burn.grid)
Output: data/processed/harmonized/region=<id>/year=<yyyy>/data.parquet
            date, ix, iy, value (VIIRS-equivalent active cell-days), source, nrt
        burn/harmonization_params.json  (the fitted factors, versioned in git)

One source per region and day, in this order: SNPP, NOAA20, MODIS_TA (Terra+Aqua), MODIS_T, MODIS_A.
value = factor[region][source][calendar month] for every cell the source saw burning that day.
"""
import json
import shutil

import duckdb
import pandas as pd

from burn.config import CELLDAY, HARMONIZATION as H, HARMONIZED, PARAMS_FILE, REGIONS

SOURCES = ["SNPP", "NOAA20", "MODIS_TA", "MODIS_T", "MODIS_A"]
COUNT_COL = {"SNPP": "c_s", "NOAA20": "c_j", "MODIS_TA": "c_ta", "MODIS_T": "c_t", "MODIS_A": "c_a"}


def connect():
    con = duckdb.connect()
    con.execute(f"create view cd as select * from read_parquet('{CELLDAY}/*/*/data.parquet', hive_partitioning=true)")
    # one row per region, day and cell: which satellites saw it
    con.execute("""
        create temp table cell as
        select region, date, ix, iy,
               bool_or(satellite = 'Terra') t, bool_or(satellite = 'Aqua') a,
               bool_or(satellite = 'SNPP') s, bool_or(satellite = 'NOAA20') j,
               bool_or(satellite in ('Terra', 'Aqua') and daynight = 'D') modis_day,
               bool_or(nrt) nrt
        from cd group by all""")
    return con


def day_table(con) -> pd.DataFrame:
    """Per region and day: active cell-days per satellite, and the source chosen for that day."""
    m = H["missing_rule_min_cells"]
    s0, s1 = H["snpp_period"]
    df = con.execute(f"""
        with d as (
            select region, date,
                   count(*) filter (t) c_t, count(*) filter (a) c_a, count(*) filter (t or a) c_ta,
                   count(*) filter (s) c_s, count(*) filter (j) c_j,
                   count(*) filter ((t or a) and modis_day) c_ta_day,
                   count(*) filter ((t or a) and not modis_day) c_ta_night
            from cell group by all),
        cal as (
            select r.region, g.date::date as date
            from (select region, min(date) d0, max(date) d1 from d group by 1) r,
                 generate_series(r.d0, r.d1, interval 1 day) g(date)),
        f as (
            select cal.region, cal.date,
                   coalesce(c_t, 0) c_t, coalesce(c_a, 0) c_a, coalesce(c_ta, 0) c_ta, coalesce(c_s, 0) c_s,
                   coalesce(c_j, 0) c_j, coalesce(c_ta_day, 0) c_ta_day, coalesce(c_ta_night, 0) c_ta_night
            from cal left join d using (region, date)),
        op as (
            select *, greatest(c_t, c_a, c_s, c_j) as mx,
                   cal_s and not (c_s = 0 and greatest(c_t, c_a, c_j) >= {m}) as op_s,
                   cal_j and not (c_j = 0 and greatest(c_t, c_a, c_s) >= {m}) as op_j,
                   not (c_t = 0 and greatest(c_a, c_s, c_j) >= {m}) as op_t,
                   cal_a and not (c_a = 0 and greatest(c_t, c_s, c_j) >= {m}) as op_a
            from (select *, date between date '{s0}' and date '{s1}' as cal_s,
                         date >= date '{H["noaa20_start"]}' as cal_j,
                         date >= date '{H["aqua_start"]}' as cal_a from f))
        select *, case when op_s then 'SNPP' when op_j then 'NOAA20'
                       when date >= date '{s0}' then 'NONE'  -- MODIS is never used once VIIRS has started
                       when op_t and op_a then 'MODIS_TA' when op_t then 'MODIS_T'
                       when op_a then 'MODIS_A' else 'NONE' end as source
        from op order by region, date""").df()
    df["date"] = pd.to_datetime(df["date"])
    df["y"], df["m"] = df["date"].dt.year, df["date"].dt.month
    gap = pd.Series(False, index=df.index)
    for a, b in H["known_gaps"]:
        gap |= df["date"].between(a, b)
    df.loc[gap & df["source"].str.startswith("MODIS"), "source"] = "NONE"
    return df


def fit_factors(days: pd.DataFrame, years, structure="month") -> dict:
    """factor[region][source][month 1..12] so that factor * source cell-days ~ S-NPP cell-days."""
    out = {}
    for rid, d in days.groupby("region"):
        out[rid] = {"SNPP": {m: 1.0 for m in range(1, 13)}}
        fit = d[d["y"].between(*years) & d["op_s"]]
        for src, need in (("MODIS_TA", ["op_t", "op_a"]), ("MODIS_T", ["op_t"]), ("MODIS_A", ["op_a"])):
            f = fit[fit[need].all(axis=1)]
            col = COUNT_COL[src]
            k_all = f["c_s"].sum() / f[col].sum()
            g = f.groupby("m")[["c_s", col]].sum().reindex(range(1, 13), fill_value=0)
            k = {}
            for mth, row in g.iterrows():
                enough = structure == "month" and row[col] >= H["min_fit_cells_per_month"]
                k[mth] = float(row["c_s"] / row[col]) if enough else float(k_all)
            out[rid][src] = k
        n = d[d["y"].between(*H["n20_fit_years"]) & d["op_s"] & d["op_j"]]
        out[rid]["NOAA20"] = {m: float(n["c_s"].sum() / n["c_j"].sum()) for m in range(1, 13)}
    return out


def apply_days(days: pd.DataFrame, factors: dict) -> pd.Series:
    """Harmonized regional value per day (for validation; the gridded output uses the same factors)."""
    val = pd.Series(0.0, index=days.index)
    for src in SOURCES:
        sel = days["source"] == src
        k = [factors[r][src][m] for r, m in zip(days.loc[sel, "region"], days.loc[sel, "m"])]
        val[sel] = days.loc[sel, COUNT_COL[src]].to_numpy() * k
    return val


def write_grid(con, days: pd.DataFrame, factors: dict):
    con.register("days_df", days[["region", "date", "source"]])
    rows = [(r, s, m, k) for r, by in factors.items() for s, km in by.items() for m, k in km.items()]
    con.register("fac_df", pd.DataFrame(rows, columns=["region", "source", "m", "k"]))
    con.execute("""
        create or replace temp table harm as
        select c.region, c.date, c.ix, c.iy, cast(f.k as float) as value, d.source, c.nrt
        from cell c
        join days_df d on d.region = c.region and d.date = c.date
        join fac_df f on f.region = c.region and f.source = d.source and f.m = month(c.date)
        where (d.source = 'SNPP' and c.s) or (d.source = 'NOAA20' and c.j)
           or (d.source = 'MODIS_TA' and (c.t or c.a)) or (d.source = 'MODIS_T' and c.t)
           or (d.source = 'MODIS_A' and c.a)""")
    if HARMONIZED.exists():
        shutil.rmtree(HARMONIZED)
    for rid in REGIONS:
        for (y,) in con.execute("select distinct year(date) from harm where region = ? order by 1", [rid]).fetchall():
            d = HARMONIZED / f"region={rid}" / f"year={y}"
            d.mkdir(parents=True)
            con.execute(f"copy (select date, ix, iy, value, source, nrt from harm where region = '{rid}' "
                        f"and year(date) = {y} order by date, ix, iy) to '{d}/data.parquet' (format parquet, compression zstd)")
    # day-level provenance, including days with no detections and gap days
    out = days[["region", "date", "source"]].copy()
    con.register("prov_df", out)
    con.execute(f"copy (select region, cast(date as date) date, source from prov_df order by 1, 2) "
                f"to '{HARMONIZED}/day_source.parquet' (format parquet)")


def main():
    con = connect()
    days = day_table(con)
    factors = fit_factors(days, H["fit_years"])
    params = {"harmonization": H, "unit": "VIIRS S-NPP-equivalent active cell-days, 0.1 degree, UTC day",
              "factors": {r: {s: {str(m): round(k, 4) for m, k in km.items()} for s, km in by.items()}
                          for r, by in factors.items()}}
    PARAMS_FILE.write_text(json.dumps(params, indent=1) + "\n")
    write_grid(con, days, factors)
    # check: gridded sum equals the day-level sum
    grid = con.execute("select region, sum(value) v, count(*) n from harm group by 1 order by 1").df()
    days["value"] = apply_days(days, factors)
    for r in grid.itertuples():
        day_sum = days.loc[days["region"] == r.region, "value"].sum()
        assert abs(r.v - day_sum) / day_sum < 1e-4, (r.region, r.v, day_sum)
        print(f"{r.region}: {r.n:,d} harmonized cell-day rows, total {r.v:,.0f} VIIRS-equivalent cell-days")
    print(days.groupby(["region", "source"]).agg(days=("date", "count"), first=("date", "min"), last=("date", "max")))
    for rid, by in factors.items():
        print(rid, {s: [round(by[s][m], 2) for m in range(1, 13)] for s in ("MODIS_TA", "MODIS_T", "MODIS_A")},
              "NOAA20", round(by["NOAA20"][1], 3))


if __name__ == "__main__":
    main()

"""BURN-025: compare MODIS with VIIRS over the overlap years under each candidate unit.

Run: uv run python analysis/explore_overlap.py
Reads data/processed/cellday (burn.grid). Writes plots to docs/figures/ and prints the tables
that docs/overlap-exploration.md quotes.

Candidate units, each computed per month for the whole region:
  count      raw detections
  cd010      active cell-days on the 0.1 degree grid (cell-days with >= 1 detection)
  cd025/050/100  the same on 0.2, 0.5 and 1.0 degree grids
  frp        sum of fire radiative power
MODIS = Terra + Aqua together (a cell-day is active if either saw it). VIIRS = S-NPP alone.
Fit years: 2012 to 2021 (MODIS orbits stable; see docs/sensor-differences.md).
"""
import sys
from pathlib import Path

import duckdb
import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from burn.config import CELLDAY, REGIONS  # noqa: E402

FIG = ROOT / "docs" / "figures"
GROUPS = {"MODIS": "('Terra','Aqua')", "Terra": "('Terra')", "Aqua": "('Aqua')",
          "SNPP": "('SNPP')", "NOAA20": "('NOAA20')"}
GRIDS = {"cd010": 1, "cd020": 2, "cd050": 5, "cd100": 10}
UNIT_LABEL = {"count": "raw detections", "cd010": "active cell-days, 0.1°", "cd020": "active cell-days, 0.2°",
              "cd050": "active cell-days, 0.5°", "cd100": "active cell-days, 1.0°", "frp": "FRP sum (MW)"}


def monthly(con, region, where="true"):
    """Monthly value of every unit for every satellite group."""
    frames = []
    for g, sats in GROUPS.items():
        base = f"from cd where region = '{region}' and satellite in {sats} and {where}"
        df = con.execute(f"select year(date) y, month(date) m, sum(n) count, sum(frp) frp {base} group by all").df()
        for unit, k in GRIDS.items():
            cd = con.execute(
                f"select y, m, count(*) {unit} from (select distinct year(date) y, month(date) m, date, "
                f"floor(ix / {k}) cx, floor(iy / {k}) cy {base}) group by all").df()
            df = df.merge(cd, on=["y", "m"], how="outer")
        df["group"] = g
        frames.append(df)
    return pd.concat(frames).fillna(0)


def stability(wide_num, wide_den, years):
    """How stable is num/den? Returns overall ratio and spread statistics."""
    num, den = wide_num.loc[years], wide_den.loc[years]
    annual = num.groupby("y").sum() / den.groupby("y").sum()
    # season months: the months that together hold 95% of the denominator's activity
    clim = den.groupby("m").sum().sort_values(ascending=False)
    season = clim.index[: int((clim.cumsum() / clim.sum() < 0.95).sum()) + 1]
    seasonal = num[num.index.get_level_values("m").isin(season)].groupby("m").sum() / \
        den[den.index.get_level_values("m").isin(season)].groupby("m").sum()
    ok = (num > 0) & (den > 0) & num.index.get_level_values("m").isin(season)
    logr = np.log(num[ok] / den[ok])
    k = num.sum() / den.sum()
    pred = k * den[ok]
    return {
        "ratio": k,
        "cv_years_%": 100 * annual.std() / annual.mean(),
        "cv_season_months_%": 100 * seasonal.std() / seasonal.mean(),
        "sd_log_monthly": logr.std(),
        "r_log": np.corrcoef(np.log(num[ok]), np.log(den[ok]))[0, 1],
        "mape_const_factor_%": 100 * float(np.median(np.abs(pred - num[ok]) / num[ok])),
    }


def main():
    con = duckdb.connect()
    con.execute(f"create view cd as select * from read_parquet('{CELLDAY}/*/*/data.parquet', hive_partitioning=true)")
    fit = list(range(2012, 2022))
    pd.set_option("display.width", 250, "display.max_columns", 20, "display.float_format", "{:.3f}".format)
    for rid, region in REGIONS.items():
        mon = monthly(con, rid).set_index(["group", "y", "m"]).sort_index()
        units = ["count", "cd010", "cd020", "cd050", "cd100", "frp"]
        print(f"\n===== {region['name']}: S-NPP VIIRS / MODIS (Terra+Aqua), 2012-2021 =====")
        print(pd.DataFrame({u: stability(mon.loc["SNPP"][u], mon.loc["MODIS"][u], fit) for u in units}).T)
        print(f"\n--- {region['name']}: other pairs, units count and cd010 ---")
        pairs = [("SNPP", "Aqua", fit), ("SNPP", "Terra", fit), ("NOAA20", "SNPP", list(range(2019, 2026))),
                 ("MODIS", "Terra", list(range(2003, 2022))), ("SNPP", "MODIS", list(range(2022, 2026)))]
        rows = {}
        for a, b, yrs in pairs:
            for u in ("count", "cd010"):
                rows[f"{a}/{b} {yrs[0]}-{yrs[-1]} {u}"] = stability(mon.loc[a][u], mon.loc[b][u], yrs)
        print(pd.DataFrame(rows).T)

        # day and night separately
        for dn in ("D", "N"):
            m2 = monthly(con, rid, f"daynight = '{dn}'").set_index(["group", "y", "m"]).sort_index()
            print(f"\n--- {region['name']}: S-NPP / MODIS, daynight = {dn} ---")
            print(pd.DataFrame({u: stability(m2.loc["SNPP"][u], m2.loc["MODIS"][u], fit) for u in ("count", "cd010")}).T)

        # annual ratio table (to see drift after 2021)
        ann = mon.groupby(["group", "y"]).sum()
        tab = pd.DataFrame({u: ann.loc["SNPP"][u] / ann.loc["MODIS"][u] for u in ("count", "cd010", "cd050", "frp")}).loc[2012:2025]
        tab["N20/SNPP count"] = ann.loc["NOAA20"]["count"] / ann.loc["SNPP"]["count"]
        tab["N20/SNPP cd010"] = ann.loc["NOAA20"]["cd010"] / ann.loc["SNPP"]["cd010"]
        print(f"\n--- {region['name']}: annual ratio S-NPP / MODIS by unit, and NOAA-20 / S-NPP ---")
        print(tab)

        # plots: one figure per unit: monthly scatter (log-log) and annual ratio
        for u in units:
            v, mo = mon.loc["SNPP"][u], mon.loc["MODIS"][u]
            idx = v.index.intersection(mo.index)
            v, mo = v.loc[idx], mo.loc[idx]
            yrs = idx.get_level_values("y")
            fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
            early, late = (yrs <= 2021), (yrs >= 2022)
            ax[0].scatter(mo[early], v[early], s=14, c="#00224e", label="2012 to 2021 (fit years)")
            ax[0].scatter(mo[late], v[late], s=14, c="#e1a100", marker="^", label="2022 to 2025 (MODIS drifting)")
            k = v[early].sum() / mo[early].sum()
            pos = mo[mo > 0]
            xs = np.array([pos.min(), mo.max()])
            ax[0].plot(xs, k * xs, c="#707173", lw=1, label=f"constant factor {k:.2f}")
            ax[0].set_xscale("log"); ax[0].set_yscale("log")
            ax[0].set_xlabel(f"MODIS Terra+Aqua, {UNIT_LABEL[u]} per month")
            ax[0].set_ylabel(f"VIIRS S-NPP, {UNIT_LABEL[u]} per month")
            ax[0].legend(frameon=False, fontsize=8)
            a = (ann.loc["SNPP"][u] / ann.loc["MODIS"][u]).loc[2012:2025]
            ax[1].plot(a.index, a.values, marker="o", c="#00224e")
            ax[1].axvspan(2021.5, 2025.5, color="#e1a100", alpha=0.15)
            ax[1].set_ylim(0, a.max() * 1.15)
            ax[1].set_xlabel("year"); ax[1].set_ylabel("annual ratio VIIRS / MODIS")
            fig.suptitle(f"{region['name']}: VIIRS S-NPP against MODIS, {UNIT_LABEL[u]}")
            fig.tight_layout()
            fig.savefig(FIG / f"overlap_{rid}_{u}.png", dpi=110)
            plt.close(fig)


if __name__ == "__main__":
    main()

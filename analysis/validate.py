"""BURN-008: validate the harmonization on held-out overlap years.

Run: uv run python analysis/validate.py
Fit on 2012-2018, test on 2019-2021: the MODIS-derived series (factor x MODIS cell-days) against the
VIIRS S-NPP series, on days when S-NPP, Terra and Aqua all operated. Thresholds: docs/unit-decision.md.
Writes plots to docs/figures/ and prints the tables quoted in docs/validation.md.
"""
import sys
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from burn import harmonize as hz  # noqa: E402
from burn.config import HARMONIZATION as H, REGIONS  # noqa: E402

FIG = ROOT / "docs" / "figures"
THRESH = {"bias_%": 10, "r_log": 0.95, "medape_%": 20}


def season_months(d):
    clim = d.groupby("m")["c_s"].sum().sort_values(ascending=False)
    return set(clim.index[: int((clim.cumsum() / clim.sum() < 0.95).sum()) + 1])


def metrics(obs, pred, months):
    """obs, pred: monthly totals indexed by (y, m)."""
    keep = obs.index.get_level_values("m").isin(months) & (obs > 0) & (pred > 0)
    o, p = obs[keep], pred[keep]
    co, cp = obs.groupby("m").mean(), pred.groupby("m").mean()
    return {"bias_%": 100 * (p.sum() / o.sum() - 1),
            "r_log": float(np.corrcoef(np.log(o), np.log(p))[0, 1]),
            "medape_%": 100 * float(np.median(np.abs(p - o) / o)),
            "rmse_%_of_mean": 100 * float(np.sqrt(np.mean((p - o) ** 2)) / o.mean()),
            "peak_obs": int(co.idxmax()), "peak_pred": int(cp.idxmax()), "n_months": int(keep.sum())}


def predict(d, factors, src):
    col = hz.COUNT_COL[src]
    k = np.array([factors[r][src][m] for r, m in zip(d["region"], d["m"])])
    return d[col].to_numpy() * k


def daynight_factors(d_fit):
    """Two factors per region: MODIS cell-days seen by day, and seen at night only (least squares on months)."""
    g = d_fit.groupby(["y", "m"])[["c_ta_day", "c_ta_night", "c_s"]].sum()
    k, *_ = np.linalg.lstsq(g[["c_ta_day", "c_ta_night"]].to_numpy(float), g["c_s"].to_numpy(float), rcond=None)
    return np.clip(k, 0, None)


def main():
    pd.set_option("display.width", 250, "display.max_columns", 20, "display.float_format", "{:.2f}".format)
    con = hz.connect()
    days = hz.day_table(con)
    both = days[days["op_s"] & days["op_t"] & days["op_a"] & days["y"].between(2012, 2021)]
    results = {}
    for rid, region in REGIONS.items():
        d = both[both["region"] == rid]
        months = season_months(d)
        print(f"\n===== {region['name']}: season months {sorted(months)} =====")

        # 1. temporal hold-out: fit 2012-2018, test 2019-2021
        test = d[d["y"] >= 2019]
        obs = test.groupby(["y", "m"])["c_s"].sum()
        rows = {}
        for structure in ("const", "month"):
            f = hz.fit_factors(days[days["y"] <= 2018], (2012, 2018), structure)
            for src in ("MODIS_TA", "MODIS_T", "MODIS_A"):
                pred = pd.Series(predict(test, f, src), index=test.index).groupby([test["y"], test["m"]]).sum()
                rows[f"{src} {structure}"] = metrics(obs, pred, months)
        kd = daynight_factors(d[d["y"] <= 2018])
        pred = (test["c_ta_day"] * kd[0] + test["c_ta_night"] * kd[1]).groupby([test["y"], test["m"]]).sum()
        rows["MODIS_TA daynight"] = metrics(obs, pred, months)
        unscaled = test.groupby(["y", "m"])["c_ta"].sum()
        rows["MODIS_TA unscaled cell-days"] = metrics(obs, unscaled, months)
        hold = pd.DataFrame(rows).T
        print("-- hold-out 2019-2021 (fit 2012-2018) --"); print(hold)
        results[rid] = hold

        # 2. leave-one-year-out over 2012-2021
        loyo = {}
        for structure in ("const", "month", "daynight"):
            preds = []
            for y in range(2012, 2022):
                tr, te = d[d["y"] != y], d[d["y"] == y]
                if structure == "daynight":
                    k = daynight_factors(tr)
                    p = te["c_ta_day"] * k[0] + te["c_ta_night"] * k[1]
                else:
                    f = hz.fit_factors(days[days["y"] != y], (2012, 2021), structure)
                    p = pd.Series(predict(te, f, "MODIS_TA"), index=te.index)
                preds.append(p)
            p = pd.concat(preds).groupby([d["y"], d["m"]]).sum()
            o = d.groupby(["y", "m"])["c_s"].sum()
            loyo[structure] = metrics(o, p, months)
            ann_o, ann_p = o.groupby("y").sum(), p.groupby("y").sum()
            loyo[structure]["annual_medape_%"] = 100 * float(np.median(np.abs(ann_p - ann_o) / ann_o))
            loyo[structure]["annual_max_err_%"] = 100 * float(np.max(np.abs(ann_p - ann_o) / ann_o))
        print("-- leave-one-year-out 2012-2021, MODIS Terra+Aqua --"); print(pd.DataFrame(loyo).T)

        # 3. step at the sensor change, in the final record
        fac = hz.fit_factors(days, H["fit_years"])
        dr = days[days["region"] == rid].copy()
        dr["value"] = hz.apply_days(dr, fac)
        ann = dr[dr["y"].between(2001, 2025)].groupby("y")["value"].sum()
        raw_m = dr.groupby("y")["c_ta"].sum().loc[2001:2025]
        raw_s = dr.groupby("y")["c_s"].sum().loc[2012:2025]
        logchg = np.log(ann).diff().dropna()
        pre = logchg.loc[2004:2011]
        print(f"-- transition: change 2011->2012 = {100 * (ann[2012] / ann[2011] - 1):+.0f}%; "
              f"year-to-year changes 2003-2011 range {100 * (np.exp(pre.min()) - 1):+.0f}% to {100 * (np.exp(pre.max()) - 1):+.0f}%; "
              f"mean 2007-2011 = {ann.loc[2007:2011].mean():,.0f}, mean 2012-2016 = {ann.loc[2012:2016].mean():,.0f} "
              f"({100 * (ann.loc[2012:2016].mean() / ann.loc[2007:2011].mean() - 1):+.0f}%); "
              f"unscaled cell-days would step {100 * (raw_s.loc[2012:2016].mean() / raw_m.loc[2007:2011].mean() - 1):+.0f}%")

        # 4. small areas: 2 x 2 degree blocks, annual totals 2019-2021 from the hold-out fit
        f18 = hz.fit_factors(days[days["y"] <= 2018], (2012, 2018), "month")
        con.register("k_df", pd.DataFrame([(m, k) for m, k in f18[rid]["MODIS_TA"].items()], columns=["m", "k"]))
        con.register("ok_df", test[["date"]])
        blk = con.execute(f"""
            select floor(ix / 20) bx, floor(iy / 20) byy, year(c.date) y,
                   count(*) filter (s) obs, sum(k) filter (t or a) pred
            from cell c join ok_df o on o.date = c.date join k_df on k_df.m = month(c.date)
            where region = '{rid}' group by all having count(*) filter (s) >= 200""").df()
        err = (blk["pred"] / blk["obs"] - 1) * 100
        print(f"-- 2 degree blocks x years with >= 200 VIIRS cell-days (n={len(blk)}): median abs error "
              f"{err.abs().median():.0f}%, 90th percentile {err.abs().quantile(0.9):.0f}%, bias {err.median():+.0f}%")

        # plots
        fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
        raw_counts = con.execute(f"""select year(date) y, sum(n) filter (satellite in ('Terra','Aqua')) modis,
            sum(n) filter (satellite = 'SNPP') snpp from cd where region = '{rid}' and year(date) between 2001 and 2025
            group by 1 order by 1""").df().set_index("y")
        ax[0].plot(raw_counts.index, raw_counts["modis"], marker="o", c="#707173", label="MODIS Terra+Aqua detections")
        ax[0].plot(raw_counts.index[raw_counts["snpp"] > 0], raw_counts["snpp"][raw_counts["snpp"] > 0], marker="^", c="#e1a100", label="VIIRS S-NPP detections")
        ax[0].set_title("Before: raw detections per year"); ax[0].legend(frameon=False, fontsize=8); ax[0].set_ylim(0)
        ax[1].plot(ann.index, ann.values, marker="o", c="#00224e", label="harmonized (VIIRS-equivalent cell-days)")
        ax[1].axvline(2011.5, c="#707173", ls=":", lw=1); ax[1].text(2011.6, ann.max() * 0.95, "VIIRS starts", fontsize=8)
        ax[1].set_title("After: harmonized burning activity per year"); ax[1].legend(frameon=False, fontsize=8); ax[1].set_ylim(0)
        fig.suptitle(region["name"]); fig.tight_layout(); fig.savefig(FIG / f"harmonized_before_after_{rid}.png", dpi=110); plt.close(fig)

        f = hz.fit_factors(days[days["y"] <= 2018], (2012, 2018), "month")
        pm = pd.Series(predict(d, f, "MODIS_TA"), index=d.index).groupby([d["y"], d["m"]]).sum()
        om = d.groupby(["y", "m"])["c_s"].sum()
        x = np.array([y + (m - 0.5) / 12 for y, m in om.index])
        fig, ax = plt.subplots(figsize=(12, 3.8))
        ax.plot(x, om.values, c="#e1a100", lw=2, label="VIIRS S-NPP active cell-days (observed)")
        ax.plot(x, pm.values, c="#00224e", lw=1.2, ls="--", label="derived from MODIS with factors fitted on 2012 to 2018")
        ax.axvspan(2019, 2022, color="#707173", alpha=0.12); ax.text(2019.05, om.max() * 0.93, "held out", fontsize=8)
        ax.set_ylabel("active cell-days per month"); ax.legend(frameon=False, fontsize=8)
        ax.set_title(f"{region['name']}: MODIS-derived against VIIRS, monthly")
        fig.tight_layout(); fig.savefig(FIG / f"validation_monthly_{rid}.png", dpi=110); plt.close(fig)

    print("\n===== PASS / FAIL against thresholds (hold-out, MODIS_TA month) =====")
    for rid, hold in results.items():
        r = hold.loc["MODIS_TA month"]
        ok = {"bias": abs(r["bias_%"]) <= THRESH["bias_%"], "r_log": r["r_log"] >= THRESH["r_log"],
              "medape": r["medape_%"] <= THRESH["medape_%"], "peak": r["peak_obs"] == r["peak_pred"]}
        print(rid, ok, "PASS" if all(ok.values()) else "FAIL")


if __name__ == "__main__":
    main()

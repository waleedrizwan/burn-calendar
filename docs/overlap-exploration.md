# MODIS against VIIRS in the overlap period (BURN-025)

Script: [`analysis/explore_overlap.py`](../analysis/explore_overlap.py) (reads the filtered cell-day aggregates from `burn.grid`). Plots: `docs/figures/overlap_<region>_<unit>.png`, one per region and unit. Run on Saturday, November 14, 2026.

Compared: VIIRS S-NPP alone against MODIS Terra+Aqua together, vegetation-fire detections only, monthly totals for the whole region, 2012 to 2021 (the years with stable MODIS orbits).

- **ratio**: total VIIRS divided by total MODIS.
- **CV years**: spread of the annual ratio across the ten years. Low means the relationship does not change from year to year.
- **CV season months**: spread of the ratio across the calendar months that hold 95 percent of activity. Low means it does not change through the season.
- **SD log monthly**: spread of log(VIIRS/MODIS) over individual months.
- **median error**: median absolute percent error of monthly VIIRS predicted from MODIS with one constant factor.

## Canada

| Unit | Ratio | CV years | CV season months | SD log monthly | r (log) | Median error |
|---|---|---|---|---|---|---|
| Raw detections | 4.76 | 16.2% | 21.8% | 0.251 | 0.984 | 23.2% |
| **Active cell-days, 0.1°** | 1.87 | **7.4%** | 15.7% | 0.201 | 0.987 | 13.9% |
| Active cell-days, 0.2° | 1.93 | 8.0% | 15.6% | 0.205 | 0.985 | 14.5% |
| Active cell-days, 0.5° | 1.98 | 7.8% | 25.2% | 0.264 | 0.986 | 16.5% |
| Active cell-days, 1.0° | 1.97 | 7.8% | 23.3% | 0.251 | 0.986 | 15.8% |
| FRP sum | 0.70 | 14.3% | 12.4% | 0.199 | 0.991 | 11.3% |

## Zambia

| Unit | Ratio | CV years | CV season months | SD log monthly | r (log) | Median error |
|---|---|---|---|---|---|---|
| Raw detections | 4.33 | 4.5% | 15.2% | 0.150 | 0.962 | 15.1% |
| **Active cell-days, 0.1°** | 2.56 | 4.6% | 14.8% | 0.152 | **0.987** | 11.8% |
| Active cell-days, 0.2° | 2.10 | 4.6% | 17.2% | 0.180 | 0.985 | 13.7% |
| Active cell-days, 0.5° | 1.54 | 3.6% | 19.6% | 0.207 | 0.984 | 15.3% |
| Active cell-days, 1.0° | 1.35 | 2.3% | 31.0% | 0.273 | 0.991 | 18.7% |
| FRP sum | 1.25 | 4.2% | 7.2% | 0.090 | 0.988 | 5.1% |

## What it shows

1. **Raw counts are the least stable unit in Canada.** The annual ratio ranges from 3.2 (2020) to 6.1 (2014): in a year of large, intense fires VIIRS multiplies each fire into many more pixels than in a quiet year. A single factor on counts would overstate quiet years or understate big ones.
2. **Active cell-days on the 0.1 degree grid are the most stable count-like unit in both regions**: half the year-to-year spread of raw counts in Canada (7.4 against 16.2 percent), and the best monthly correlation in Zambia. Coarser grids do not help: they saturate in the peak season (worse within-season stability).
3. **A residual remains**: VIIRS still records about 1.9 times (Canada) and 2.6 times (Zambia) as many active cell-days as MODIS, because it sees small fires MODIS misses. So gridding alone does not harmonize; a scaling step is needed.
4. **The ratio changes through the season** (about 15 percent spread across season months in both regions), so the factor should depend on the calendar month.
5. **Day and night differ.** Daytime active cell-days in Canada are very stable (CV years 4.2 percent, median error 7.3 percent); night-time ones are not (CV years 37 percent). In Zambia the night ratio is about 10 against 2.5 by day. Whether separate day and night factors help is tested when fitting (BURN-007).
6. **NOAA-20 is interchangeable with S-NPP**: ratio 1.01 (counts) and 1.04 (cell-days) in Canada, 1.03 and 1.06 in Zambia over 2019 to 2025, monthly median error 3 to 5 percent. Years with S-NPP outages (2022, 2024) stand out at 1.08 to 1.19.
7. **MODIS after 2021 has drifted**: in Canada the cell-day ratio moves from 1.87 (2012 to 2021) to 1.57 (2022 to 2025). This confirms that the fit must stop at 2021 and that MODIS should not carry the record after VIIRS begins.
8. **FRP sums are also stable**, most of all in Zambia. They are not chosen as the unit because the challenge asks for a hotspot calendar, MODIS FRP has a known view-angle bias and VIIRS 375 m FRP saturates on intense fires, but FRP is a useful cross-check.
9. **One MODIS satellite alone is a much weaker predictor** than both: for example S-NPP against Aqua alone in Zambia has r = 0.88 to 0.95, and Terra alone needs a factor of 7 to 15. The Terra-only period (November 2000 to June 2002) can be scaled but must be flagged as less certain.

**Most stable candidate: active cell-days on the 0.1 degree grid**, with a calendar-month factor.

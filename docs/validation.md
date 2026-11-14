# Validation of the harmonization (BURN-008)

Script: [`analysis/validate.py`](../analysis/validate.py). Run Saturday, November 14, 2026. Thresholds were set beforehand in [`unit-decision.md`](unit-decision.md).

## Method

The factors that turn MODIS active cell-days into VIIRS-equivalent ones were fitted on **2012 to 2018 only**. They were then applied to MODIS for **2019 to 2021**, years the fit never saw, and the result was compared with what VIIRS S-NPP actually recorded, on days when S-NPP, Terra and Aqua all operated. Metrics are on monthly regional totals for the months that hold 95 percent of activity (Canada April to December, Zambia May to October).

## Result: both regions pass

| Metric | Threshold | Canada | Zambia |
|---|---|---|---|
| Bias | within ±10% | **+1.5%** | **−3.5%** |
| Correlation of log monthly totals | ≥ 0.95 | **0.98** | **1.00** |
| Median absolute error, monthly | ≤ 20% | **14.5%** | **4.8%** |
| RMSE as a share of the mean month | (reported) | 22.5% | 5.0% |
| Peak month, VIIRS / MODIS-derived | same | **July / July** | **September / September** |

Without the factors (unscaled cell-days) the bias is −45 percent in Canada and −61 percent in Zambia.

Plots: `docs/figures/validation_monthly_<region>.png` (monthly, held-out years shaded) and `docs/figures/harmonized_before_after_<region>.png` (raw detections per year before, harmonized series after).

## Choice of factor structure

Leave-one-year-out over 2012 to 2021, MODIS Terra+Aqua to VIIRS:

| Structure | Canada: monthly median error | Canada: worst annual error | Zambia: monthly median error | Zambia: worst annual error |
|---|---|---|---|---|
| One factor per region | 15.9% | 14.5% | 10.9% | 4.5% |
| **One per region and calendar month** (used) | **11.0%** | **8.0%** | **3.9%** | 4.7% |
| Two per region: seen by day, seen only at night | 17.7% | 20.3% | 4.6% | 7.6% |

The calendar-month structure is the simplest that passes everywhere and has the lowest error, so it is used. With one factor per region the peak month in Zambia moves from September to August in the hold-out; with monthly factors it does not. Day and night factors did not help.

## The sensor change in the final record (stretch)

| | Canada | Zambia |
|---|---|---|
| Change from 2011 (MODIS-derived) to 2012 (VIIRS) | +11% | +1% |
| Year-to-year changes within the MODIS era, 2003 to 2011 | −32% to +54% | −13% to +12% |
| Mean 2012 to 2016 against mean 2007 to 2011 | +31% | +1% |
| The same step with unscaled cell-days | +151% | +154% |

In both regions the change across the transition is inside the range of ordinary year-to-year changes. In Zambia, where seasons repeat closely, the five-year means differ by 1 percent. Canada's +31 percent between the five-year means cannot be separated from real change: 2012 to 2016 contains the large fire years 2014 and 2015, and the hold-out bias for Canada is +1.5 percent.

## The early Terra-only period (stretch)

Terra alone, scaled with its own monthly factors, tested the same way on 2019 to 2021: Canada bias +2.5 percent, median monthly error 12.5 percent; Zambia bias +0.3 percent, median monthly error 4.5 percent. Both would pass. The factors are large (2 to 8 in Canada, 6 to 12 in Zambia) because Terra's morning overpass sees a small share of the burning, so this period stays flagged as lower confidence.

## Small areas

The factors are fitted for the whole region. Applied to 2 degree by 2 degree blocks (held-out years, blocks with at least 200 VIIRS cell-days a year), the annual error is:

| | Canada | Zambia |
|---|---|---|
| Median absolute error | 18% | 9% |
| 90th percentile | 44% | 34% |

So for a small area the pre-2012 values are less certain than for the region, mainly where the local fire type differs from the regional mix.

## Limitations

- **The years before 2012 cannot be validated against VIIRS**, because VIIRS did not exist. The validation shows that MODIS-derived values reproduce VIIRS in years when both flew, and assumes the relationship was the same in 2000 to 2011. A change in fire size or type over time within a region would change it.
- The factors are regional and by calendar month. They are less accurate for small areas (above), for unusual months, and outside the main season, where few detections go into the fit (months with fewer than 200 MODIS cell-days in the fit use the all-year factor).
- November 2000 to June 2002 rests on Terra alone. 15 April 2001, 15 June to 3 July 2001 and 19 to 28 March 2002 have no data.
- The unit counts a grid cell once per day whether one hotspot or fifty were detected in it, so it measures how widespread burning is, not its intensity. Intensity is better read from FRP, which is in the hotspot CSV export.
- NOAA-20 is treated as equal to S-NPP up to one factor per region (0.97 to 0.98). After 2 November 2026 the record rests on NOAA-20 alone.
- 2026 uses the Area API clipped with Natural Earth country polygons, while earlier years use FIRMS's own per-country files, so detections right on a border or coast can differ slightly. Near real-time months have no `type`, so static sources are removed with a mask instead.
- Cloud and smoke hide fires from every sensor; no correction is made.
- Two regions were tested. The factors are not valid elsewhere; another region needs its own fit.

## Independent review (Saturday, November 14, 12:55 p.m.)

A second session re-checked the method and the pipeline without reusing the validation script.

- **Pipeline recount from the raw FIRMS files**, written from scratch (distinct type 0 cell-days, times the published factors): Zambia 2015 S-NPP 267,793 (app 267,793), Canada 2019 S-NPP 16,696 (app 16,696), Canada 2004 MODIS 30,926 (app 30,926), Zambia 2008 MODIS 271,721 (app 271,720). Canada 2023 differs by 469 cell-days (0.6 percent) because S-NPP has no data on 26 July 2023 and NOAA-20 fills that day, as designed.
- **No days without a source after 2012.** The only no-source days are the 30 known MODIS gaps before 2012.
- **The VIIRS to MODIS ratio depends on the size of the fire year in Canada.** On shared days in 2012 to 2021 it runs from 1.70 (2021) to 2.17 (2020), with a correlation of −0.89 against log annual activity: in big years large fires already light up a cell for MODIS, so VIIRS adds fewer cells. The calendar-month factors absorb most of this. Leave-one-year-out annual errors stay between −8 and +8 percent (mean absolute 4.7 percent). A power-law fit (shared exponent about 0.8) was tested and did no better (mean 4.2 percent, wider spread), so the method is unchanged. Read single pre-2012 years in Canada as about ±8 percent.
- **Zambia's ratio creeps up** from 2.45 (2012) to 2.64 (2021), about 0.8 percent a year. If that held before 2012, early Zambian values could read high by up to about 10 percent. Neither region shows a significant trend in the app (Canada p = 0.29, Zambia p = 0.43), so this does not create a false trend claim.
- **The reference is stable within about ±3 percent:** S-NPP over NOAA-20 runs 0.94 to 0.99 by year, against the single factor of 0.97 to 0.98 that applies after 2 November 2026.

Changes made: the app now shows a notice whenever the area is smaller than the whole region (pre-2012 values and the baseline are less certain there), and the explainer gives single-year and single-month error, not only the three-year total.

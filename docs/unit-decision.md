# The unit of burning activity (BURN-006)

Decided Saturday, November 14, 2026, before any calibration was fitted.

## Decision

**A calendar cell holds VIIRS-equivalent active fire cell-days.**

Plain-language definition, for the app:

> **Burning activity** is the number of 0.1 degree grid cells (about 11 km) times days on which a satellite detected at least one vegetation-fire hotspot, expressed on the scale of the VIIRS S-NPP sensor. One unit is one grid cell burning on one day. Years before 2012, when only MODIS was flying, are converted to this scale with factors measured while both sensors flew together.

- **Grid:** 0.1 degree latitude by longitude (`ix = floor(lon / 0.1)`, `iy = floor(lat / 0.1)`).
- **Time step:** one UTC day; the calendar sums days into UTC months.
- **Reference sensor:** VIIRS S-NPP, the longest VIIRS record with a stable orbit.

## Evidence (BURN-025, `overlap-exploration.md`)

- Raw counts: the VIIRS to MODIS ratio swings from 3.2 to 6.1 between years in Canada (CV 16 percent), because intense fires multiply into many more VIIRS pixels. Active 0.1 degree cell-days halve that (CV 7.4 percent) and give the best monthly correlation in Zambia (0.987).
- Coarser grids saturate in peak season and are less stable within the season.
- After gridding, VIIRS still has 1.9 times (Canada) and 2.6 times (Zambia) the active cell-days of MODIS, and the ratio varies through the season by about 15 percent, so a calendar-month factor per region is needed.
- NOAA-20 matches S-NPP within about 4 percent.
- MODIS overpass times drift after 2021 (`sensor-differences.md`).

## Rejected alternatives

| Alternative | Why not |
|---|---|
| Scaled raw detections ("MODIS-equivalent counts") | Least stable ratio in Canada; a count of pixels is not a count of anything on the ground |
| Active cell-days on 0.2, 0.5 or 1.0 degree grids | No more stable between years, worse within the season; coarser answers for small areas |
| FRP sums | Stable, but not a hotspot count as the challenge asks; MODIS view-angle bias and VIIRS saturation; kept as a cross-check |
| MODIS scale as the reference | MODIS is the sensor that is ending and drifting; the future record is VIIRS, so the past is converted to the scale that continues |
| Unscaled cell-days | A step of about 2 times at the sensor change |

## Which satellite supplies each day

For each region and day, the first available source in this order is used, and the others are ignored. The source is stored with every value (provenance).

| Order | Source | Period | Factor |
|---|---|---|---|
| 1 | VIIRS S-NPP | 2012-01-20 to 2026-11-02 | 1 (reference) |
| 2 | VIIRS NOAA-20 | from 2018-04-01, when S-NPP is missing; all days after 2026-11-02 | NOAA-20 to S-NPP factor per region (about 1) |
| 3 | MODIS Terra+Aqua | 2002-07-04 to 2012-01-19 | region and calendar-month factor, fitted 2012 to 2021 |
| 4 | MODIS Terra alone | 2000-11-01 to 2002-07-03, and Aqua outages before 2012 | its own region and calendar-month factor, fitted on Terra-only cell-days 2012 to 2021 |
| 5 | MODIS Aqua alone | Terra outages before 2012 | its own factor, same way |

A satellite counts as missing on a day when it reports nothing in the region while another satellite reports at least 20 active cell-days there.

- **MODIS-only years (2000 to 2011):** scaled to the VIIRS scale. Cannot be validated against VIIRS; the validation is done on held-out overlap years instead.
- **Overlap (2012 to 2026):** VIIRS only. MODIS is used here only to fit and test the factors (2012 to 2021), so the orbit drift after 2021 never enters the record.
- **Early period with Terra only (November 2000 to June 2002):** corrected with the Terra-only factor and **flagged** in the app as lower confidence (morning overpass, weaker relationship). 15 June to 3 July 2001 has no data at all and is flagged as a gap.
- **Several VIIRS satellites at once:** never summed. One satellite per day, so a second or third satellite in orbit cannot raise the number. NOAA-21 is not used.
- **End of S-NPP (2 November 2026):** NOAA-20 continues with its factor. **End of MODIS (2027):** no effect, because MODIS is not used after 2012.
- **Near real-time months:** same treatment; flagged provisional.

## Validation thresholds (set before the fit)

BURN-008 fits on 2012 to 2018 and tests on 2019 to 2021, comparing the MODIS-derived series with the VIIRS S-NPP series, on monthly totals per region for the months that hold 95 percent of activity. Pass needs all four:

| Metric | Pass |
|---|---|
| Bias: (sum of MODIS-derived) / (sum of VIIRS) − 1 | within ±10 percent |
| Correlation of log monthly totals | at least 0.95 |
| Median absolute percent error of monthly totals | at most 20 percent |
| Peak month of the average season | the same month in both series |

The simplest factor structure that passes is used. Candidates, compared by leave-one-year-out error over 2012 to 2021: one factor per region; one per region and calendar month; one per region, calendar month and MODIS day/night class.

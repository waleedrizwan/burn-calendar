# Calendar metrics and anomaly statistics (BURN-013)

Decided Saturday, November 14, 2026. The API computes all of these; the interface only displays them.

## Wording

- The raw observations are **hotspot detections**, never "fires". One fire produces many detections and a detection is not always a fire.
- The calendar value is **burning activity**, in VIIRS-equivalent active cell-days (see `unit-decision.md`): the number of 0.1 degree grid cells times days with at least one vegetation-fire hotspot detection.

## Time

Days and months are **UTC**. For the pilot regions the daytime and the following night-time overpass fall on the same UTC day.

## Monthly value

`V(y, m)` = sum of harmonized values over all cells in the area and all days of month `m` of year `y`.

## Baseline

For calendar month `m`, the baseline is the set `B(m) = { V(y, m) : y in baseline years }`, where the **baseline years are every complete year in the record before the current year** (2001 to 2025 now; 2000 has only November and December and is left out). Using the whole record keeps the sample as large as possible (25 values); the trend view shows whether the record is drifting.

Statistics of `B(m)`: **median**, 10th, 25th, 75th and 90th percentiles (linear interpolation), minimum and maximum. The mean is reported but not used for anomalies: counts are skewed, and one extreme year (Canada 2023) would move it.

## Anomaly of a month

1. **Percentile rank**: `P = (number of baseline values below V + half the number equal to V) / N x 100`. The month being ranked is excluded from its own baseline.
2. **Ratio to median**: `R = V / median(B(m))`, only when the median is at least 5 (see low activity).
3. **Category**, from `P`:

| Category | Rule |
|---|---|
| Record high | `V` above every baseline value |
| Well above normal | `P` ≥ 90 |
| Above normal | 75 ≤ `P` < 90 |
| Near normal | 25 < `P` < 75 |
| Below normal | 10 < `P` ≤ 25 |
| Well below normal | `P` ≤ 10 |

Ranks are used in place of standard deviations because the counts are skewed and full of zeros: a rank needs no distribution and one extreme year cannot distort it.

## The current, incomplete month

A partial month is never compared with full months. If the data run through day `d` of the month, `V` is the sum over days 1 to `d`, and every baseline value is also the sum over days 1 to `d` of that month in its year. The response says "through day d" and marks the cell `partial`. Near real-time data are marked `provisional`.

## Zero and low activity

- If the baseline median for the month is below **5** cell-days, the ratio is not reported and the category is **"Too little activity to compare"**, unless `V` is itself at least 5 and above every baseline value, which is reported as a record high. The value is still shown.
- If the area has no detections in the whole record, the response says so.

## Year totals and trend

- Year total `A(y)` = sum of the twelve months. The current year is marked partial.
- **Trend**: Theil-Sen slope (median of all pairwise slopes) of `A(y)` over complete years with full MODIS coverage onward (2003 to last complete year), reported as percent of the median year per decade, with the Mann-Kendall test p-value. Reported as "no clear trend" when p > 0.05.

## Flags shown with a month

- `partial`: month not complete.
- `provisional`: includes near real-time data.
- `sources`: which satellites supplied the days of the month.
- `lower_confidence`: any day supplied by one MODIS satellite alone (mainly November 2000 to June 2002).
- `gap_days`: days in the month with no satellite data.

# API contract

All responses are JSON unless the path ends in `.csv`. Months and days are **UTC**. Definitions of every statistic are in [`metrics.md`](metrics.md). Errors are `{"detail": "..."}` with status 404 (unknown region or series), 422 (invalid input, area outside the region), 413 (export too large) or 503 (data not loaded).

## Area parameters (all endpoints)

| Parameter | Meaning |
|---|---|
| `region` | `canada` or `zambia` (see `/api/regions`). Default `canada` |
| `bbox` | `west,south,east,north` in degrees. Must overlap the region |
| `lat`, `lon`, `radius_km` | A point inside the region and a radius of up to 2,000 km |

Give `bbox`, or the circle, or neither (whole region). A 0.1 degree grid cell belongs to the area when its centre is inside. An area smaller than one cell returns the cell containing it and a warning.

## `GET /api/regions`

`{"regions": [{"id": "canada", "name": "Canada", "regime": "boreal forest", "bbox": [-141.1, 41.6, -52.5, 83.2]}, ...]}`

## `GET /api/calendar`

Extra parameters: `series` = `harmonized` (default) or `modis_raw` (whole regions only, raw MODIS detections, for comparison); `start`, `end` as `YYYY-MM` limit the `cells` returned (the baseline always uses the whole record).

Example: `/api/calendar?region=zambia&bbox=27,-15,29,-13&start=2025-08&end=2025-08`

```json
{
  "region": "zambia",
  "area": {"type": "bbox", "bbox": [27.0, -15.0, 29.0, -13.0], "cells": 400},
  "series": "harmonized", "harmonized": true,
  "unit": {"id": "viirs_equivalent_active_cell_days", "label": "Burning activity (VIIRS-equivalent active cell-days)", "short": "active cell-days", "description": "..."},
  "harmonization_version": "1.0",
  "period": {"start": "2000-11", "end": "2026-11", "last_data_date": "2026-11-14"},
  "time_basis": "UTC",
  "warnings": [],
  "cells": [{"year": 2025, "month": 8, "value": 3051.0, "partial": false, "provisional": false,
             "sources": ["SNPP"], "lower_confidence": false, "gap_days": 0,
             "percentile": 62.0, "ratio_to_median": 1.08, "category": "near_normal"}],
  "baseline": [{"month": 1, "n_years": 25, "median": 3.0, "p10": 0.0, "p25": 1.0, "p75": 6.0, "p90": 9.0, "min": 0.0, "max": 14.0, "mean": 4.1}],
  "current": {"year": 2026, "month": 11, "through_day": 14, "complete": false, "value": 310.0,
              "baseline_years": [2001, 2025], "baseline_median_to_date": 205.0, "baseline_p25_to_date": 150.0,
              "baseline_p75_to_date": 290.0, "baseline_max_to_date": 420.0, "rank": 4, "of": 26,
              "provisional": true, "percentile": 88.0, "ratio_to_median": 1.51, "category": "above"},
  "years": [{"year": 2025, "total": 14210.5, "partial": false}],
  "trend": {"available": true, "start_year": 2003, "end_year": 2025, "slope_per_year": -50.1,
            "percent_per_decade": -2.5, "p_value": 0.16, "significant": false, "direction": "none"},
  "source_labels": {"SNPP": "VIIRS S-NPP", "...": "..."}
}
```

(The numbers in the example are illustrative.)

- `cells`: one entry per month in order, `value` 0 where nothing was detected. `category` is one of `record_high`, `well_above`, `above`, `near_normal`, `below`, `well_below`, `low_activity`, `partial`, `no_baseline`.
- `sources`: `MODIS_T`, `MODIS_A`, `MODIS_TA`, `SNPP`, `NOAA20`. `lower_confidence` is true when any day came from a single MODIS satellite. `gap_days` counts days with no satellite data.
- `current` compares the latest month, through its last day with data, with the same days of that month in each baseline year.
- With `series=modis_raw` only `region`, `area`, `series`, `harmonized`, `unit`, `period`, `time_basis`, `warnings` and `cells` (`year`, `month`, `value`, `partial`, `provisional`) are returned.

## `GET /api/calendar.csv`

Same parameters as `/api/calendar` (harmonized). One row per month: value, baseline median and quartiles, percentile, ratio, category and flags. Lines starting with `#` describe the search and the unit.

## `GET /api/hotspots.csv`

Area parameters plus `start` and `end` as `YYYY-MM-DD` (required). Every MODIS and VIIRS detection in the area and period, unfiltered: `latitude, longitude, acq_datetime_utc, sensor, satellite, confidence, confidence_pct, frp_mw, daynight, type, brightness_k, scan_km, track_km, quality, version`. At most 500,000 rows; a larger search returns 413 with the row count.

## `GET /api/health`

`{"status": "ok"}`

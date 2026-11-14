# API contract

All responses are JSON. Months are calendar months in **UTC**. Counts are hotspot detections, never "fires".

## `GET /api/regions`

```json
{"regions": [{"id": "canada", "name": "Canada", "regime": "boreal forest", "bbox": [-141.1, 41.6, -52.5, 83.2]}]}
```

`bbox` is west, south, east, north.

## `GET /api/calendar?region=<id>&series=<series>`

| Parameter | Values | Default |
|---|---|---|
| `region` | a region id from `/api/regions` | `canada` |
| `series` | `modis_raw` (walking skeleton). `harmonized` is added by BURN-010 | `modis_raw` |

Planned for BURN-010, same response shape: `bbox=w,s,e,n` or `lat`, `lon`, `radius_km` to select an area inside the region, and `start`, `end` as `YYYY-MM`.

```json
{
  "region": "canada",
  "area": {"type": "region", "name": "Canada", "bbox": [-141.1, 41.6, -52.5, 83.2]},
  "series": "modis_raw",
  "harmonized": false,
  "unit": {"id": "modis_detections", "label": "MODIS hotspot detections (unharmonized)", "description": "..."},
  "period": {"start": "2000-11", "end": "2026-11", "last_data_date": "2026-11-13"},
  "time_basis": "UTC",
  "cells": [
    {"year": 2000, "month": 11, "value": 12, "partial": false, "provisional": false}
  ]
}
```

- `cells` has one entry for every month from `period.start` to `period.end`, in order, with `value` 0 where nothing was detected.
- `partial` is true for the last month when it is not complete. `provisional` is true when the month includes near real-time data that FIRMS will later replace with standard-quality data.
- `area.type` will be `region`, `bbox` or `circle`.
- Errors: `404` for an unknown region or series, `503` when no data are loaded, each as `{"detail": "..."}`.

## `GET /api/health`

`{"status": "ok"}`

---
id: BURN-010
title: Query API: area and date range to analytics
type: build
priority: must
requirement: 3. The number must be answerable for any area
timebox: 2h
status: done
depends: BURN-007, BURN-009
---

## First principle

The user's question has two inputs, an area and a time range, and one output, the activity numbers. Something must turn the inputs into the output.

## What fails without this task

The harmonized data and the screen have no connection.

## Description

An endpoint that takes an area and a date range and returns monthly harmonized totals, baseline statistics and anomalies.

## Acceptance criteria

- [x] It accepts a bounding box or a point with radius
- [ ] Stretch: it accepts a polygon (GeoJSON)
- [x] Invalid input and oversized areas return a clear error
- [x] Responses meet the target set in BURN-009 for pilot areas
- [x] An example request and response are documented
- [x] An area smaller than one grid cell returns a result with a warning about precision

## Outcome (Sat Nov 14)

`burn/analytics.py` and `burn/app.py`; contract and example in `docs/api.md`; tests in `tests/test_app.py`. Measured 60 to 90 ms per request including statistics. Polygon input (stretch) not done.

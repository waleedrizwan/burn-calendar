---
id: BURN-010
title: Query API: area and date range to analytics
type: build
priority: must
requirement: 3. The number must be answerable for any area
timebox: 2h
status: in-progress
depends: BURN-007, BURN-009
---

## First principle

The user's question has two inputs, an area and a time range, and one output, the activity numbers. Something must turn the inputs into the output.

## What fails without this task

The harmonized data and the screen have no connection.

## Description

An endpoint that takes an area and a date range and returns monthly harmonized totals, baseline statistics and anomalies.

## Acceptance criteria

- [ ] It accepts a bounding box or a point with radius
- [ ] Stretch: it accepts a polygon (GeoJSON)
- [ ] Invalid input and oversized areas return a clear error
- [ ] Responses meet the target set in BURN-009 for pilot areas
- [ ] An example request and response are documented
- [ ] An area smaller than one grid cell returns a result with a warning about precision

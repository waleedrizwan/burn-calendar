---
id: BURN-009
title: Architecture and data-volume spike
type: decision
priority: must
requirement: 3. The number must be answerable for any area
timebox: 30m
status: todo
depends: BURN-002, BURN-006
---

## First principle

Response time is set by how much data a query must touch. The full record is very large, and a user will not wait minutes for a calendar.

## What fails without this task

We pick a stack by preference, and discover late that an arbitrary polygon query takes too long or that the data does not fit on free hosting.

## Description

Measure real data size for one pilot region and extrapolate. Choose the simplest stack that one person can build and deploy in the time available, for example a pre-aggregated grid in Parquet/DuckDB. Compare a second store only if the first choice is too slow. Decide whether raw points are kept alongside the grid, because the hotspot CSV export in BURN-018 needs them.

## Acceptance criteria

- [ ] Measured row counts and disk size for one pilot region are written down
- [ ] Stretch: query timings are compared on two candidate stores
- [ ] A short decision record in `docs/` covers data store, API, frontend framework, map library and hosting
- [ ] The map library and the tile source are open source or freely available, and need no commercial key
- [ ] The record states whether raw points are kept for export
- [ ] A response-time target is set for pilot areas

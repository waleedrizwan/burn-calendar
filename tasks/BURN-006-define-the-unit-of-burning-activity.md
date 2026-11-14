---
id: BURN-006
title: Define the unit of burning activity
type: decision
priority: must
requirement: 2. The number must be comparable over time
timebox: 30m
status: todo
depends: BURN-004, BURN-005, BURN-025
---

## First principle

A measurement is comparable only if its unit is the same everywhere. A raw hotspot count is not a unit: one fire is one MODIS pixel but several VIIRS pixels.

## What fails without this task

The calendar shows a jump in 2012 that is caused by the sensor change, and every trend and anomaly in the app is wrong. This is the most important decision on the board.

## Description

Decide what number a calendar cell holds. Options include scaled 'MODIS-equivalent' counts, active grid-cell-days, and FRP sums. Decide the grid size and the time step. Base the choice on the measured comparison in BURN-025.

## Acceptance criteria

- [ ] The decision cites the evidence from BURN-025 and lists the rejected alternatives
- [ ] The unit has a plain-language definition that can be shown in the app
- [ ] The grid size and time step are fixed
- [ ] Handling is defined for the MODIS-only years, the overlap period, and the VIIRS-only future
- [ ] Handling is defined for the early period when only one MODIS satellite was flying: corrected, flagged or excluded
- [ ] The treatment of several VIIRS satellites flying at once is defined
- [ ] Handling is defined for the end of S-NPP data on 2 November 2026 and the planned end of MODIS in 2027
- [ ] Pass and fail thresholds for the validation in BURN-008 are set before the fit is run

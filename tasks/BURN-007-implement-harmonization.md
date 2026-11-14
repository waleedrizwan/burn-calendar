---
id: BURN-007
title: Implement harmonization
type: build
priority: must
requirement: 2. The number must be comparable over time
timebox: 2h30
status: done
depends: BURN-002, BURN-006
---

## First principle

The challenge sets its own test: after harmonization, the sensor of origin should no longer matter. That is a property of a dataset, so only transformed data can meet it; a described method cannot.

## What fails without this task

We have a method on paper and two incompatible datasets on disk.

## Description

Apply the filters from BURN-004, aggregate hotspots to the common grid, fit the calibration on the overlap period only, and apply it to the full record.

## Acceptance criteria

- [x] One harmonized value exists per cell and day from 2000 to the present
- [x] The value can be used without knowing the sensor
- [x] A provenance flag records which sensors contributed
- [x] The whole process is reproducible from one command with versioned parameters
- [x] The sum of gridded counts equals the filtered point counts (tested)

## Outcome (Sat Nov 14)

`burn/grid.py` (filters, 0.1 degree cell-days) and `burn/harmonize.py` (fit 2012 to 2021, apply, `source` provenance, factors in `burn/harmonization_params.json`). One command: `uv run python -m burn.pipeline`. Record runs 2000-11-01 to 2026-11-14. Tests in `tests/test_harmonize.py`.

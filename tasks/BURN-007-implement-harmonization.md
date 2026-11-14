---
id: BURN-007
title: Implement harmonization
type: build
priority: must
requirement: 2. The number must be comparable over time
timebox: 2h30
status: in-progress
depends: BURN-002, BURN-006
---

## First principle

The challenge sets its own test: after harmonization, the sensor of origin should no longer matter. That is a property of a dataset, so only transformed data can meet it; a described method cannot.

## What fails without this task

We have a method on paper and two incompatible datasets on disk.

## Description

Apply the filters from BURN-004, aggregate hotspots to the common grid, fit the calibration on the overlap period only, and apply it to the full record.

## Acceptance criteria

- [ ] One harmonized value exists per cell and day from 2000 to the present
- [ ] The value can be used without knowing the sensor
- [ ] A provenance flag records which sensors contributed
- [ ] The whole process is reproducible from one command with versioned parameters
- [ ] The sum of gridded counts equals the filtered point counts (tested)

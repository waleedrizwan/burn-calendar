---
id: BURN-002
title: Ingestion pipeline for FIRMS archives
type: build
priority: must
requirement: 1. The number must exist
timebox: 1h30
status: in-progress
depends: BURN-001
---

## First principle

The app can only answer questions about data that has been loaded in one consistent shape. Two sensors with two schemas are two datasets, not one.

## What fails without this task

There is nothing to harmonize or display, and every later step would need its own sensor-specific loading code.

## Description

One command that downloads MODIS and VIIRS hotspots for the configured regions and years and normalizes them to a common schema: latitude, longitude, UTC datetime, sensor, satellite, confidence, fire radiative power (FRP), day/night, type. Store the result as Parquet files, so this task does not wait on the architecture decision.

## Acceptance criteria

- [ ] One command loads all sensors for the configured regions and years
- [ ] Re-running it creates no duplicates
- [ ] Row counts per sensor and year are logged and match the source
- [ ] Raw files stay outside git
- [ ] The common schema is documented

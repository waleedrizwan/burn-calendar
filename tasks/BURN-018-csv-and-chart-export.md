---
id: BURN-018
title: CSV and chart export
type: build
priority: must
requirement: 4. A person must be able to read it
timebox: 1h
status: in-progress
depends: BURN-010, BURN-016
---

## First principle

Analysis continues outside the app. Scientists and managers need the numbers in their own tools and reports.

## What fails without this task

Users must retype values or take screenshots.

## Description

Downloads for the hotspots in a search, the monthly summary, and the charts.

## Acceptance criteria

- [ ] A CSV of the raw hotspots within the area and dates downloads with documented columns, including sensor and satellite
- [ ] A CSV of the monthly harmonized summary downloads
- [ ] File names include the area and date range
- [ ] Very large exports are capped with a clear message
- [ ] Stretch: charts export as PNG

## Outcome (Sat Nov 14)

`/api/calendar.csv`, `/api/hotspots.csv` (500,000 row cap) and SVG download buttons on both charts. Check the remaining criteria in the task file against the running app.

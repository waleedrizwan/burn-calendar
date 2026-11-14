---
id: BURN-016
title: Burning activity calendar
type: build
priority: must
requirement: 4. A person must be able to read it
timebox: 2h
status: in-progress
depends: BURN-010, BURN-013, BURN-024
---

## First principle

Seasonal and yearly patterns are easier to see than to read. A year-by-month grid puts both on one screen.

## What fails without this task

The app returns a table of numbers and the user must find the pattern alone.

## Description

A year-by-month heatmap from the earliest year to the present, colored by harmonized activity.

## Acceptance criteria

- [ ] The grid covers the earliest year to the present
- [ ] Cells use a color-vision-safe sequential ramp, for example viridis or cividis, with a legend
- [ ] Hover or keyboard focus shows the value
- [ ] Row and column totals mark the highest year and the highest month
- [ ] The partial current month is visibly marked

## Outcome (Sat Nov 14)

Harmonized calendar table with cividis ramp, year totals, flags. Rendered and checked in a headless screenshot.

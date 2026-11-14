---
id: BURN-017
title: Anomaly and historical comparison views
type: build
priority: must
requirement: 4. A person must be able to read it
timebox: 1h
status: todo
depends: BURN-016
---

## First principle

A single value means little without a reference. The user needs 'compared with what' answered on the screen.

## What fails without this task

The user sees that there were 400 detections this month and cannot tell whether that is normal.

## Description

Views that place the current period against history, using the definitions from BURN-013.

## Acceptance criteria

- [ ] The current month is shown against the historical median with its percentile
- [ ] An anomaly calendar uses the diverging ramp
- [ ] The app shows 'data through <date>'
- [ ] Stretch: a chart shows yearly totals over time
- [ ] Stretch: a seasonal profile shows the median and range by month with a selected year overlaid
- [ ] All numbers match the API

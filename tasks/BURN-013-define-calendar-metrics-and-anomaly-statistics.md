---
id: BURN-013
title: Define calendar metrics and anomaly statistics
type: brainstorm
priority: must
requirement: 4. A person must be able to read it
timebox: 30m
status: todo
depends: BURN-011
---

## First principle

'Unusual' has no meaning without a definition of 'usual'. Fire counts are skewed and full of zeros, so a plain average misleads.

## What fails without this task

The data code and the interface compute different things, or the app flags every month in a quiet area as extreme.

## Description

Define the baseline period, the summary statistic (median and percentiles), the anomaly measure, and how the partial current month and low-activity areas are handled.

## Acceptance criteria

- [ ] The baseline period and statistic are defined
- [ ] The anomaly measure is chosen and justified for skewed count data
- [ ] Rules exist for the partial current month
- [ ] Rules exist for areas with zero or very low activity
- [ ] Formulas are written so that data and interface code implement the same thing
- [ ] Month boundaries are defined as UTC or local time
- [ ] The app's wording is fixed as 'hotspot detections', never 'fires'

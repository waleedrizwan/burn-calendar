---
id: BURN-013
title: Define calendar metrics and anomaly statistics
type: brainstorm
priority: must
requirement: 4. A person must be able to read it
timebox: 30m
status: done
depends: BURN-011
---

## First principle

'Unusual' has no meaning without a definition of 'usual'. Fire counts are skewed and full of zeros, so a plain average misleads.

## What fails without this task

The data code and the interface compute different things, or the app flags every month in a quiet area as extreme.

## Description

Define the baseline period, the summary statistic (median and percentiles), the anomaly measure, and how the partial current month and low-activity areas are handled.

## Acceptance criteria

- [x] The baseline period and statistic are defined
- [x] The anomaly measure is chosen and justified for skewed count data
- [x] Rules exist for the partial current month
- [x] Rules exist for areas with zero or very low activity
- [x] Formulas are written so that data and interface code implement the same thing
- [x] Month boundaries are defined as UTC or local time
- [x] The app's wording is fixed as 'hotspot detections', never 'fires'

## Outcome (Sat Nov 14)

Written in [`docs/metrics.md`](../docs/metrics.md): whole-record baseline per calendar month, median and percentiles, percentile-rank anomaly categories, month-to-date rule, low-activity rule, UTC months, wording.

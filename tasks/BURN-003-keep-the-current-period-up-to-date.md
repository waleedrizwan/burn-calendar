---
id: BURN-003
title: Keep the current period up to date
type: build
priority: should
requirement: 1. The number must exist
timebox: 1h
status: todo
depends: BURN-002, BURN-007
---

## First principle

Comparing 'this month' against history requires this month's data. A historical archive alone cannot answer the question an emergency manager asks today.

## What fails without this task

The calendar stops at the last archive download and the 'current versus historical median' feature has no current value.

## Description

Pull near-real-time hotspots through the FIRMS API, which returns at most 5 days per request, and run them through the same filtering and harmonization as the archive. S-NPP stopped delivering new data on 2 November 2026, so current data comes from NOAA-20, NOAA-21 and, until its planned end in 2027, MODIS.

## Acceptance criteria

- [ ] One manual command fetches every day since the last archive download
- [ ] Stretch: the command runs on a schedule
- [ ] The same filters and harmonization are applied as for the archive
- [ ] The app shows 'data through <date>'
- [ ] Provisional data is replaced when standard-quality data arrives, or this is documented as a limitation

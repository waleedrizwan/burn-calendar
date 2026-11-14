---
id: BURN-008
title: Validate the harmonization
type: build
priority: must
requirement: 2. The number must be comparable over time
timebox: 1h
status: in-progress
depends: BURN-007
---

## First principle

A claim that has not been tested against evidence is only a claim. Users who make response decisions need to know how far the numbers can be trusted.

## What fails without this task

We cannot tell a working harmonization from a broken one, and neither can a judge or a scientist.

## Description

Hold out part of the overlap period from the fit. Compare the series derived from MODIS with the series derived from VIIRS over the held-out period.

## Acceptance criteria

- [ ] Bias, correlation and error on monthly totals are reported per pilot region
- [ ] Each metric is compared with the thresholds set in BURN-006, and any failure is documented
- [ ] The peak month of the fire season is preserved in each pilot region
- [ ] Stretch: the change in mean activity across the sensor transition is within the range of year-to-year changes in the MODIS-only record
- [ ] Stretch: the early single-satellite period is checked separately
- [ ] Before and after plots are saved
- [ ] Limitations are written down, including that the years before the overlap cannot be validated against VIIRS

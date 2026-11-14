---
id: BURN-005
title: How others have harmonized MODIS and VIIRS
type: research
priority: must
requirement: 2. The number must be comparable over time
timebox: 30m
status: todo
depends:
---

## First principle

This is a published scientific problem. Known methods with known weaknesses are a better starting point than an invented one.

## What fails without this task

We spend the hackathon rediscovering an approach that the literature has already tested or already rejected.

## Description

Review published work on MODIS to VIIRS active fire continuity. Candidate families include per-cell or per-biome scaling fitted on the overlap period, counting active grid cells per day in place of raw detections, FRP-based comparison, and statistical calibration.

## Acceptance criteria

- [ ] At least two approaches are summarized with source links
- [ ] Each has its data needs, complexity and failure modes listed
- [ ] One approach is recommended that fits the time available (see BURN-020)
- [ ] The summary is saved in `docs/harmonization-options.md`

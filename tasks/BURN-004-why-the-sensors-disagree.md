---
id: BURN-004
title: Why the sensors disagree
type: research
priority: must
requirement: 2. The number must be comparable over time
timebox: 45m
status: done
depends:
---

## First principle

A difference cannot be corrected until it is characterized. MODIS and VIIRS report different counts for the same fire for physical reasons, and each reason needs its own treatment.

## What fails without this task

Harmonization becomes curve fitting with no understanding of what is being corrected, and it will fail in regions unlike the ones we tested.

## Description

Document what makes the counts differ: pixel size (1 km versus 375 m), overpass times, how many satellites were flying in each period, pixel growth at the swath edge, detection algorithms, confidence scales, and the `type` field that separates vegetation fires from volcanoes, gas flares and other static sources. Note known sensor outages, and check how the orbit drift of Terra and Aqua since they left their constellation has shifted overpass times in recent years.

## Acceptance criteria

- [x] A comparison table covers each difference and its expected effect on counts
- [x] A timeline shows which satellites were active in which years
- [x] A list of filters to apply is written, each with a justification
- [x] Stretch: known outages and data gaps are listed

## Outcome (Sat Nov 14)

Written in [`docs/sensor-differences.md`](../docs/sensor-differences.md). Key measured finding: Terra and Aqua overpass times are stable to 2021 and drift strongly after (Terra 10.4 h to 9.2 h, Aqua 13.7 h to 15.0 h by 2025), so MODIS after 2021 is not used for fitting or as the record.

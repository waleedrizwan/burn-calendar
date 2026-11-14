---
id: BURN-025
title: Explore MODIS against VIIRS in the overlap period
type: research
priority: must
requirement: 2. The number must be comparable over time
timebox: 1h
status: done
depends: BURN-002, BURN-011
---

## First principle

A choice between methods should rest on what the data shows. The relationship between the two sensors is an empirical fact that can be measured.

## What fails without this task

The unit in BURN-006 is chosen by argument alone and may not fit the data.

## Description

For each pilot region, compare MODIS and VIIRS activity over the overlap years under each candidate unit: raw counts, active grid-cell-days at one or two grid sizes, and FRP sums.

## Acceptance criteria

- [x] Plots are saved per pilot region and candidate unit
- [x] The stability of the MODIS to VIIRS relationship across seasons and years is reported for each candidate
- [x] The candidate with the most stable relationship is identified
- [x] The notebook or script is committed

## Outcome (Sat Nov 14)

Written in [`docs/overlap-exploration.md`](../docs/overlap-exploration.md). Most stable unit: active cell-days on the 0.1 degree grid (Canada CV across years 7.4% against 16.2% for raw counts). Script `analysis/explore_overlap.py`, plots in `docs/figures/`.

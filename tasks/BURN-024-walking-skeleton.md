---
id: BURN-024
title: Walking skeleton: raw MODIS calendar for one region
type: build
priority: must
requirement: 4. A person must be able to read it
timebox: 1h30
status: done
depends: BURN-001, BURN-023
---

## First principle

A plan is proven only when its parts work together. The earliest end-to-end version exposes problems that isolated parts hide.

## What fails without this task

Nothing is visible until harmonization is finished, and a slip there leaves no demo.

## Description

Build the thinnest working app: a year-by-month calendar of unharmonized MODIS counts for one fixed region, served through the response shape the final API will use.

## Acceptance criteria

- [x] The app runs locally with one command
- [x] The calendar shows monthly MODIS counts for one region across all available years
- [x] The data arrives through an endpoint whose response shape is written down as the API contract
- [x] The view is clearly labelled as unharmonized

## Outcome (Sat Nov 14)

Superseded by the full app: `uv run uvicorn burn.app:app`; raw MODIS view remains at `/api/calendar?series=modis_raw`, labelled unharmonized.

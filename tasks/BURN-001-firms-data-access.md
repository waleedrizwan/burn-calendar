---
id: BURN-001
title: FIRMS data access: products, coverage, formats, limits
type: research
priority: must
requirement: 1. The number must exist
timebox: 1h
status: in-progress
depends:
---

## First principle

Every number in the app is a count of satellite detections. A detection that cannot be obtained cannot be counted, so the products and years available set the outer limit of what the product can show.

## What fails without this task

Every later task guesses. We could design a harmonization for a product that does not cover the years we need, or an app that depends on an API that cannot serve 20 years of history.

## Description

List the FIRMS active fire products: MODIS (Terra and Aqua) and VIIRS 375 m (S-NPP, NOAA-20, NOAA-21). For each, find the date coverage, columns, and the difference between near-real-time and standard-quality data. Compare bulk archive download with the API (key, area and date-range limits).

## Facts checked on 2026-11-13

These came from a web search of NASA pages. Confirm them on the live FIRMS pages as part of this task.

- MODIS Collection 6.1: Terra from 1 November 2000, Aqua from July 2002. NASA plans to end science operations around February 2027 for Terra and September 2027 for Aqua.
- VIIRS 375 m, S-NPP: from 20 January 2012. FIRMS stopped delivering new S-NPP data on 2 November 2026; the archive remains available.
- VIIRS 375 m, NOAA-20: from 1 April 2018.
- VIIRS 375 m, NOAA-21: the Archive Download page lists it from 1 March 2023; the 2024 FIRMS announcement gave 17 January 2024. Use the Archive Download page.
- Data older than 7 days comes from the Archive Download tool. The request is processed and then delivered by an emailed download link; the page gives no processing time. Signing in is by Earthdata Login or an emailed code.
- The Archive Download page also links a "yearly summary by country" CSV download at https://firms.modaps.eosdis.nasa.gov/country/. Its sensors and years were not read. If the archive request is slow, check whether these files can feed the skeleton in BURN-024.
- API: 5,000 transactions per 10 minutes per key, and a larger request may count as several transactions.
- The area endpoint allows 1 to 5 days per request, as read from the live page on 2026-11-13. The API therefore suits recent data only, and the 20-year history must come from the Archive Download tool.
- The API offers each sensor in a standard-processing version (`MODIS_SP`, `VIIRS_SNPP_SP`, `VIIRS_NOAA20_SP`, `VIIRS_NOAA21_SP`) and a near-real-time version (the same names ending in `_NRT`).
- `/api/data_availability/csv/[MAP_KEY]/[SENSOR]` reports which dates each source holds.

Sources:

- https://firms.modaps.eosdis.nasa.gov/download/
- https://firms.modaps.eosdis.nasa.gov/api/area/
- https://firms.modaps.eosdis.nasa.gov/api/map_key/
- https://firms.modaps.eosdis.nasa.gov/api/data_availability/
- https://www.earthdata.nasa.gov/news/blog/transitioning-from-s-npp-viirs-omps-what-nasa-firms-users-need-know
- https://ladsweb.modaps.eosdis.nasa.gov/learn/modis-to-viirs-transition/

## Acceptance criteria

- [ ] The archive request for the full history of both pilot regions is submitted first, at 9:00 a.m. on Saturday, because the archive may deliver by email after a wait
- [x] A table lists each product with start date, end date or status, resolution, columns, and near-real-time versus standard quality
- [x] The access method is chosen for bulk history and for the latest data, with rate and size limits written down
- [x] An API key is obtained and stored outside the repo (`.env`, gitignored)
- [x] One year of each sensor for one region is downloaded and loads in a script
- [x] Citation and licence requirements are noted

## Outcome (Sat Nov 14, 9:06 a.m.)

Written in [`docs/data-access.md`](../docs/data-access.md).

- **History does not need the archive request.** FIRMS serves yearly per-country CSV files without a login (`/data/country/<source>/<year>/...`): MODIS 2000 to 2025, S-NPP 2012 to 2025, NOAA-20 2018 to 2025, standard quality with `type`. `uv run python -m burn.fetch_country` downloaded all 96 files for Canada and Zambia (3.0 GB, 36.5 million rows) in about a minute; they load in DuckDB.
- **2026** comes from the Area API in 5-day requests (`_SP` up to its max date, `_NRT` after). The `/api/country` endpoint is not available. No NOAA-21 per-country files exist, so NOAA-21 is left out of the first version.
- **Key:** a valid `FIRMS_MAP_KEY` (5,000 transactions per 10 minutes) is already in the project's gitignored `.env`. `~/.config/nasa-burn/.env` is still empty; code reads either.
- **Archive request (first criterion):** being submitted by the other session at 9:01 a.m. for Canada. It is now only a backup and a cross-check, so nothing waits on it. Tick the first criterion when the "FIRMS requests (submitted by the overnight session)" entry appears in `docs/progress-log.md`. A Zambia archive request is optional.

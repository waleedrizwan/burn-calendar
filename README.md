# Harmonized Burning Activity Calendar

A web application that turns NASA FIRMS active fire hotspots from MODIS (Terra, Aqua) and VIIRS 375 m (S-NPP, NOAA-20, NOAA-21) into one consistent month-by-year calendar of burning activity for a selected area, from November 2000 to the present.

Built for the 2026 NASA Space Apps Challenge, [Harmonization of MODIS and VIIRS Hot Spots](https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/), Guelph Local Event, Team 347.

**Status:** working locally with both pilot regions (Canada, Zambia), November 2000 to the present. Not yet deployed. See `docs/progress-log.md`.

## What it does

- Pick a region, a rectangle or a point with a radius, and a range of years.
- See a month-by-year **calendar of burning activity** that means the same thing in 2003 as in 2026, whichever satellite saw it.
- See the **current month against its history** (median, percentile, rank), a difference-from-normal view, the season against its historical range, and year totals with a trend test.
- **Download** the monthly table, the hotspot detections for the search, and the charts.

## How the harmonization works

1. Keep vegetation-fire detections only; count each satellite separately.
2. Count **active cell-days**: 0.1 degree grid cells times days with at least one detection. This removes most of the difference between 1 km and 375 m pixels (in Canada the VIIRS to MODIS ratio varies 16 percent between years for raw counts, 7 percent for cell-days).
3. Put everything on the scale of **VIIRS S-NPP**. From 2012 the record is VIIRS (S-NPP, then NOAA-20). Earlier years are MODIS multiplied by a factor per region and calendar month, fitted on 2012 to 2021 when both flew and MODIS orbits were stable.
4. **Validated on held-out years** (fit 2012 to 2018, test 2019 to 2021): bias +1.5 percent in Canada and −3.5 percent in Zambia, median monthly error 14.5 and 4.8 percent, peak month preserved. All thresholds were set before fitting.

Details: [`docs/sensor-differences.md`](docs/sensor-differences.md), [`docs/overlap-exploration.md`](docs/overlap-exploration.md), [`docs/unit-decision.md`](docs/unit-decision.md), [`docs/validation.md`](docs/validation.md) (including limitations), [`docs/metrics.md`](docs/metrics.md), [`docs/api.md`](docs/api.md).

## Run it

Requirements: [uv](https://docs.astral.sh/uv/) (it installs Python and every dependency).

```bash
uv sync                               # set up the environment (one command)
cp .env.example .env                  # add a free FIRMS MAP_KEY (needed only to fetch the current year)
uv run python -m burn.pipeline        # download, ingest, grid, harmonize (about 3.5 GB, 15 to 30 minutes)
uv run uvicorn burn.app:app           # the app, at http://127.0.0.1:8000
uv run pytest                         # tests
uv run python analysis/validate.py    # reproduce the validation
```

Data files are not in git. See [`docs/data-access.md`](docs/data-access.md) and [`docs/deploy.md`](docs/deploy.md).

## Layout

| Path | What it holds |
|---|---|
| `burn/` | Python package: ingestion, harmonization, query API |
| `web/` | Front end (static files served by the API) |
| `analysis/` | Overlap exploration and validation scripts |
| `tests/` | Tests |
| `docs/` | Rules, data access notes, references, AI-use record, progress log |
| `tasks/` | The task board (one markdown file per task) |

## Data and citation

Hotspot data: NASA FIRMS (Fire Information for Resource Management System), MODIS Collection 6.1 and VIIRS 375 m active fire products. Full citations and the licence of every third-party material are in [`docs/references.md`](docs/references.md).

## Use of AI

AI tools (Anthropic Claude, through Claude Code) were used to plan the work and to write code, documentation and data-processing scripts in this repository. Details are in [`docs/ai-usage.md`](docs/ai-usage.md). No AI-generated images, video or audio are included, and no AI-generated content contains NASA logos, flags or mission identifiers.

## Licence

Apache License 2.0. See [`LICENSE`](LICENSE).

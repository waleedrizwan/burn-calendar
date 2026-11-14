# Harmonized Burning Activity Calendar

A web application that turns NASA FIRMS active fire hotspots from MODIS (Terra, Aqua) and VIIRS 375 m (S-NPP, NOAA-20, NOAA-21) into one consistent month-by-year calendar of burning activity for a selected area, from November 2000 to the present.

Built for the 2026 NASA Space Apps Challenge, [Harmonization of MODIS and VIIRS Hot Spots](https://www.spaceappschallenge.org/2026/challenges/modis-and-viirs-hot-spots/), Guelph Local Event, Team 347.

**Status:** work in progress (hackathon weekend, November 14 to 15, 2026). See `docs/progress-log.md`.

## Run it

Requirements: [uv](https://docs.astral.sh/uv/) (it installs Python 3.12 and every dependency).

```bash
uv sync                      # set up the environment (one command)
cp .env.example .env         # then add your FIRMS MAP_KEY (only needed to fetch data)
uv run uvicorn burn.app:app --reload   # start the app at http://127.0.0.1:8000
uv run pytest                # run the tests
```

Data files are not in git. `data/raw/` holds FIRMS Archive Download files; see `docs/data-access.md` for how to get them.

## Layout

| Path | What it holds |
|---|---|
| `burn/` | Python package: ingestion, harmonization, query API |
| `web/` | Front end (static files served by the API) |
| `tests/` | Tests |
| `docs/` | Rules, data access notes, references, AI-use record, progress log |
| `tasks/` | The task board (one markdown file per task) |

## Data and citation

Hotspot data: NASA FIRMS (Fire Information for Resource Management System), MODIS Collection 6.1 and VIIRS 375 m active fire products. Full citations and the licence of every third-party material are in [`docs/references.md`](docs/references.md).

## Use of AI

AI tools (Anthropic Claude, through Claude Code) were used to plan the work and to write code, documentation and data-processing scripts in this repository. Details are in [`docs/ai-usage.md`](docs/ai-usage.md). No AI-generated images, video or audio are included, and no AI-generated content contains NASA logos, flags or mission identifiers.

## Licence

Apache License 2.0. See [`LICENSE`](LICENSE).

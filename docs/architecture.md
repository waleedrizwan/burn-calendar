# Architecture decision record (BURN-009)

Decided Saturday, November 14, 2026.

## Measured data volume

| | Canada | Zambia |
|---|---|---|
| Raw hotspot rows, 2000 to 2025, three sensors | 12.9 million | 23.7 million |
| Raw CSV on disk | 3.0 GB for both regions | |
| Normalized hotspots, Parquet (zstd) | 465 MB for both regions | |
| Filtered cell-day aggregate (per satellite, day/night) | 1.5 million rows | 8.6 million rows; 41 MB for both |
| Harmonized grid (one value per cell and day) | 0.55 million rows | 4.6 million rows; 6 MB for both |

Extrapolation: a country with a savanna regime costs about 20 MB of Parquet per year of record for points and under 1 MB for the harmonized grid. The harmonized grid for the whole globe would be a few gigabytes; the raw points for the globe (hundreds of gigabytes) would need object storage and are the part that does not scale in this design.

## Decisions

| Part | Choice | Why |
|---|---|---|
| Data store | **Parquet files queried by DuckDB in the API process.** The harmonized grid is loaded into an in-memory DuckDB table at startup | Measured: monthly totals for the whole of Zambia in 9 ms, a 2 degree box in 4 ms. No database server to run. A second store was not needed, so none was compared |
| Raw points | **Kept**, as Parquet beside the grid, read on demand for the hotspot CSV export (BURN-018). Counting 1.3 million points in a box took 55 ms | The challenge asks for a downloadable CSV of hotspots |
| API | **FastAPI** (Python), JSON; one process serves the API and the static front end | Same language as the pipeline; one container |
| Front end | **Plain HTML, CSS and JavaScript, no build step.** The calendar is an HTML table; charts are inline SVG drawn by our own code | Nothing to compile or break on deploy day; tables are accessible by default |
| Map | **Leaflet 1.9** (BSD-2-Clause) with **OpenStreetMap** standard tiles (data ODbL, attribution shown). No key | Open source, no commercial key. OSM's tile policy allows light use; a demo fits |
| Hosting | **Cloudflare Containers** (Workers Paid), one `basic` container (1 GiB memory) behind a Worker, data baked into the image (about 0.5 GB). Fly.io config kept as fallback | The process uses about 450 MB with the grid in memory. Owner chose Cloudflare on 2026-11-14 |

## Response-time target

For any area inside a pilot region: **calendar and analytics under 1 second**, hotspot CSV export under 10 seconds. An export is capped at 500,000 rows; a larger search returns an error asking for a smaller area or period.

## Area selection

Rectangle (west, south, east, north) or point with radius. A 0.1 degree grid cell belongs to the area when its centre is inside. An area smaller than one cell returns the cell that contains it, with a precision warning.

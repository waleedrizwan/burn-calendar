# Common hotspot schema (BURN-002)

`uv run python -m burn.ingest` writes every sensor to the same columns, as Parquet under
`data/processed/hotspots/region=<id>/source=<modis|viirs-snpp|viirs-jpss1>/year=<yyyy>/data.parquet`.

| Column | Type | Meaning |
|---|---|---|
| `latitude`, `longitude` | double | Centre of the detecting pixel, WGS84 degrees |
| `acq_datetime` | timestamp | Acquisition time, **UTC** (from `acq_date` + `acq_time`) |
| `sensor` | text | `MODIS` or `VIIRS` |
| `satellite` | text | `Terra`, `Aqua`, `SNPP`, `NOAA20` (raw `T`, `A`, `N`, `N20` are mapped) |
| `confidence` | text | `l`, `n`, `h`. VIIRS as delivered; MODIS percent mapped as below 30 = `l`, 30 to 79 = `n`, 80 and above = `h` (the classes FIRMS documents) |
| `confidence_pct` | int | MODIS only: the original 0 to 100 value |
| `frp` | float | Fire radiative power, MW |
| `daynight` | text | `D` or `N` |
| `type` | int | 0 presumed vegetation fire, 1 active volcano, 2 other static land source, 3 offshore. **Null for near real-time rows** |
| `brightness` | float | MODIS channel 21/22 or VIIRS I-4 brightness temperature, K |
| `scan`, `track` | float | Actual pixel size, km |
| `quality` | text | `SP` standard processing, or `NRT` near real-time |
| `version` | text | As delivered |
| `region`, `source`, `year` | partition | Pilot region id, FIRMS source folder, UTC year |

Sources of each partition: years up to 2025 are the FIRMS yearly per-country files (standard quality). 2026 is the FIRMS Area API (`_SP` to its last date, `_NRT` after), requested by bounding box and clipped to the Natural Earth 1:10m country polygon. The FIRMS per-country files use FIRMS's own country boundary, so a few detections on the border or coast can differ between 2026 and earlier years.

Re-running ingestion rewrites the partitions, so there are no duplicates. It prints row counts per sensor and year and asserts that the history row count equals the source files' row count.

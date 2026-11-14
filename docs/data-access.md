# FIRMS data access (BURN-001)

Read from the live FIRMS pages and API on Saturday, November 14, 2026.

## Products

All are point detections (the centre of a pixel flagged as containing one or more active fires or other thermal anomalies). A hotspot is not a fire: one fire gives many detections, and a detection can be a volcano, a gas flare or another static heat source.

| Product | Satellite(s) | Pixel at nadir | Swath | Local overpass | Standard (science) quality | Near real-time (NRT) | Status |
|---|---|---|---|---|---|---|---|
| MODIS Collection 6.1 (MCD14ML standard, MCD14DL NRT) | Terra, Aqua | 1 km | 2,330 km | Terra ~10:30 a.m./p.m.; Aqua ~1:30 p.m./a.m. | 2000-11-01 to 2026-08-31 (Aqua from July 2002) | 2026-09-01 to today | Running; NASA plans to end Terra science operations around Feb 2027 and Aqua around Sep 2027. Both orbits have drifted in recent years |
| VIIRS 375 m S-NPP (VNP14IMGTML, VNP14IMGTDL_NRT) | Suomi NPP | 375 m | 3,040 km | ~1:30 p.m./a.m. | 2012-01-20 to 2026-07-31 | 2026-08-01 to 2026-11-02 | **Ended**: FIRMS stopped new S-NPP data on 2026-11-02 |
| VIIRS 375 m NOAA-20 (VJ114IMGTML, VJ114IMGTDL_NRT) | NOAA-20 | 375 m | 3,040 km | ~1:30 p.m./a.m., half an orbit (~50 min) from S-NPP | 2018-04-01 to 2026-07-31 | 2026-08-01 to today | Running |
| VIIRS 375 m NOAA-21 (VJ214IMGTML, VJ214IMGTDL_NRT) | NOAA-21 | 375 m | 3,040 km | ~1:30 p.m./a.m. | 2023-03-01 to 2026-07-31 | 2024-01-17 to today | Running. **Not used in the first version** (no per-country files; see below) |

Dates come from `/api/data_availability/csv/[MAP_KEY]/ALL` on 2026-11-14. NRT is replaced by standard data after a lag (the FAQ says 2 to 3 months, the download page about 5).

### Standard versus NRT

- Standard data use final satellite position data, fill missing granules and drop data degraded by spacecraft manoeuvres. NRT is delivered within about 3 hours and its geolocation can occasionally be off by kilometres.
- **`type` exists only in standard data** (0 = presumed vegetation fire, 1 = active volcano, 2 = other static land source, 3 = offshore). NRT rows have no `type`, so static sources cannot be removed from NRT by that column.
- Day/night flag: standard uses solar zenith angle; NRT uses ascending/descending orbit.
- `version` tells them apart: MODIS `61.03` / `6.1` standard, `6.1NRT`; VIIRS `2` standard, `2.0NRT`.

### Columns

| Column | MODIS | VIIRS 375 m |
|---|---|---|
| `latitude`, `longitude` | centre of the ~1 km pixel | centre of the ~375 m pixel |
| `brightness` / `bright_ti4` | channel 21/22 brightness temperature, K | I-4 channel brightness temperature, K |
| `bright_t31` / `bright_ti5` | channel 31, K | I-5 channel, K |
| `scan`, `track` | actual pixel size in km (grows towards the swath edge, up to ~4.8 x 2 km) | actual pixel size in km (much more constant across the swath) |
| `acq_date`, `acq_time` | UTC date, UTC time as HHMM (leading zeros dropped by the API) | same |
| `satellite` | `Terra`/`Aqua` (`T`/`A` in NRT) | `N` (S-NPP), `N20`, `N21` |
| `instrument` | `MODIS` | `VIIRS` |
| `confidence` | 0 to 100 | `l`, `n`, `h` (low, nominal, high) |
| `version` | collection and processing level | same |
| `frp` | fire radiative power, MW | MW (per 375 m pixel) |
| `daynight` | `D` / `N` | `D` / `N` |
| `type` | standard only | standard only |

## Access methods

| Need | Method | Limits |
|---|---|---|
| **History, 2000 to 2025** (chosen) | **Yearly per-country CSV files**, no login: `https://firms.modaps.eosdis.nasa.gov/data/country/<source>/<year>/<source>_<year>_<Country>.csv` with `<source>` = `modis` (2000 to 2025), `viirs-snpp` (2012 to 2025), `viirs-jpss1` = NOAA-20 (2018 to 2025). Standard quality, same columns as above including `type` | No NOAA-21 files and no 2026 file (both return 404). Sizes: Canada 3 to 76 MB a year per VIIRS sensor, Zambia about 70 MB |
| **Current year, 2026** (chosen) | **Area API**: `/api/area/csv/[MAP_KEY]/[SOURCE]/[west,south,east,north]/[DAY_RANGE]/[DATE]`, sources `MODIS_SP`, `MODIS_NRT`, `VIIRS_SNPP_SP`, `VIIRS_SNPP_NRT`, `VIIRS_NOAA20_SP`, `VIIRS_NOAA20_NRT` (and `VIIRS_NOAA21_*`) | 1 to 5 days per request; bounding box only, so rows must be clipped to the country; 5,000 transactions per 10 minutes per key, and a 5-day country-sized request costs about 8 to 12 transactions (measured). Use `_SP` up to its `max_date` and `_NRT` after it |
| History, alternative | Archive Download tool (sign in, request, emailed link) | Processing time unknown. A Canada request for 2000-11-01 to 2026-11-13 was queued at 9:01 a.m. as a backup and as a cross-check for 2026 |
| Not available | `/api/country/...` | Returns "Invalid API call" |

`python -m burn.fetch_country` downloads the per-country history; ingestion (BURN-002) adds 2026 from the API.

## Key

`FIRMS_MAP_KEY` is read from the environment: a gitignored `.env` in the project root, or `~/.config/nasa-burn/.env`. It is never committed. It is needed only to fetch 2026 data, not to run the app.

## Citation and licence

NASA shares FIRMS data fully and openly; the FAQ names no specific licence. FIRMS asks for an acknowledgement sentence and for users to read the LANCE disclaimer. The wording and the algorithm papers are in [`references.md`](references.md).

## Sources

- https://firms.modaps.eosdis.nasa.gov/download/
- https://firms.modaps.eosdis.nasa.gov/api/area/ and https://firms.modaps.eosdis.nasa.gov/api/data_availability/
- https://www.earthdata.nasa.gov/data/tools/firms/faq
- https://www.earthdata.nasa.gov/data/tools/firms/active-fire-data-attributes-modis-viirs

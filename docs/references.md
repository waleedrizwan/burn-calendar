# References

Every dataset, library, tool and text source used in this project, with its licence. Add a row when something new is used. BURN-026 copies this into the Project page.

## NASA data

| Source | Used for | Terms |
|---|---|---|
| NASA FIRMS (Fire Information for Resource Management System), https://www.earthdata.nasa.gov/data/tools/firms and https://firms.modaps.eosdis.nasa.gov/ | All hotspot data | NASA full and open data sharing policy; the FIRMS FAQ names no specific licence |
| MODIS Collection 6.1 active fire detections, Terra and Aqua, 1 km: standard MCD14ML, near real-time MCD14DL | History from November 2000 | as above |
| VIIRS 375 m active fire detections, Suomi NPP: standard VNP14IMGTML, near real-time VNP14IMGTDL_NRT | 2012 to 2 November 2026 | as above |
| VIIRS 375 m active fire detections, NOAA-20: standard VJ114IMGTML, near real-time VJ114IMGTDL_NRT | 2018 to present | as above |
| VIIRS 375 m active fire detections, NOAA-21: standard VJ214IMGTML, near real-time VJ214IMGTDL_NRT | 2023 to present (if used) | as above |
| FIRMS yearly per-country files, `https://firms.modaps.eosdis.nasa.gov/data/country/...` | Bulk history for the pilot regions | as above |
| FIRMS API (`/api/area`, `/api/data_availability`) | Current-year data | as above; needs a free MAP_KEY |
| FIRMS FAQ, https://www.earthdata.nasa.gov/data/tools/firms/faq, and attribute tables, https://www.earthdata.nasa.gov/data/tools/firms/active-fire-data-attributes-modis-viirs | Product facts, column meanings | NASA web content |

### Acknowledgement (the form FIRMS asks for)

We acknowledge the use of data and imagery from the NASA LANCE FIRMS (Fire Information for Resource Management System), https://www.earthdata.nasa.gov/data/tools/firms, part of the NASA Earth Science Data and Information System (ESDIS).

The exact sentence in the FIRMS FAQ ("How do I cite/acknowledge FIRMS data?") should be copied into the Project page at submission (BURN-026). The FAQ also asks users to read the LANCE disclaimer.

### Algorithm papers

- Giglio, L., Descloitres, J., Justice, C. O., & Kaufman, Y. J. (2003). An enhanced contextual fire detection algorithm for MODIS. Remote Sensing of Environment, 87, 273–282. doi:10.1016/S0034-4257(03)00184-6
- Schroeder, W., Oliva, P., Giglio, L., & Csiszar, I. A. (2014). The New VIIRS 375 m active fire detection data product: Algorithm description and initial assessment. Remote Sensing of Environment, 143, 85–96. doi:10.1016/j.rse.2013.12.008

## Software

| Library | Used for | Licence |
|---|---|---|
| Python 3.12 | Language | PSF-2.0 |
| uv | Environment management | Apache-2.0 / MIT |
| FastAPI | Web API | MIT |
| Uvicorn | Web server | BSD-3-Clause |
| DuckDB | Query engine | MIT |
| pandas | Data processing | BSD-3-Clause |
| PyArrow / Apache Parquet | Storage format | Apache-2.0 |
| httpx | HTTP client | BSD-3-Clause |
| python-dotenv | Reads `.env` | BSD-3-Clause |
| pytest, ruff (development only) | Tests, linting | MIT |

## Other text sources

| Source | Used for |
|---|---|
| NASA Space Apps Challenge 2026 pages (challenge statement, submission guide, judging guide, FAQs, terms) | `challengedescrption.md`, `docs/rules.md` |
| Apache License 2.0 text, https://www.apache.org/licenses/LICENSE-2.0.txt | `LICENSE` |

## Images, video, audio

None so far.

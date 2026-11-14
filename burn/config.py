"""Project configuration: pilot regions, sensors, paths."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
PROCESSED = DATA / "processed"

# Pilot regions (decided in BURN-011). bbox = west, south, east, north.
REGIONS = {
    "canada": {"name": "Canada", "firms_country": "Canada", "regime": "boreal forest",
               "bbox": (-141.1, 41.6, -52.5, 83.2)},
    "zambia": {"name": "Zambia", "firms_country": "Zambia", "regime": "tropical savanna",
               "bbox": (21.9, -18.1, 33.8, -8.1)},
}

# FIRMS yearly per-country files: folder name -> (sensor label, first year).
COUNTRY_SOURCES = {
    "modis": ("MODIS", 2000),
    "viirs-snpp": ("VIIRS_SNPP", 2012),
    "viirs-jpss1": ("VIIRS_NOAA20", 2018),
}
LAST_COUNTRY_YEAR = 2025  # newest year published as per-country files (checked 2026-11-14)

# Area API sources for the current year: (API prefix, country-file folder it continues).
API_SOURCES = {"MODIS": "modis", "VIIRS_SNPP": "viirs-snpp", "VIIRS_NOAA20": "viirs-jpss1"}
CURRENT_YEAR = 2026
BOUNDARIES = RAW / "boundaries" / "ne_10m_admin_0_countries.geojson"
HOTSPOTS = PROCESSED / "hotspots"  # Parquet, partitioned region=/source=/year=

# Gridding (BURN-007). Cell index: ix = floor(longitude / GRID_DEG), iy = floor(latitude / GRID_DEG).
GRID_DEG = 0.1
CELLDAY = PROCESSED / "cellday"      # Parquet, partitioned region=/year=
STATIC_DEG = 0.01                    # cell size of the static-source mask
STATIC_MIN = 3                       # type 2/3 detections needed to mark a cell as static

# Harmonization (docs/unit-decision.md). Version the parameters: change VERSION when any of these change.
HARMONIZED = PROCESSED / "harmonized"   # Parquet, partitioned region=/year=
PARAMS_FILE = ROOT / "burn" / "harmonization_params.json"
HARMONIZATION = {
    "version": "1.0",
    "fit_years": [2012, 2021],            # MODIS orbits stable; inclusive
    "n20_fit_years": [2018, 2025],
    "snpp_period": ["2012-01-20", "2026-11-02"],
    "noaa20_start": "2018-04-01",
    "aqua_start": "2002-07-04",
    "missing_rule_min_cells": 20,         # a satellite is missing on a day it reports nothing while another reports >= this many cell-days
    "min_fit_cells_per_month": 200,       # calendar months with fewer source cell-days in the fit use the all-year factor
    "known_gaps": [["2001-04-15", "2001-04-15"], ["2001-06-15", "2001-07-03"], ["2002-03-19", "2002-03-28"]],
}

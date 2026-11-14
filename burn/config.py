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

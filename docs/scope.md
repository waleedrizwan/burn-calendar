# Primary user, scope and pilot regions (BURN-011)

Decided Saturday, November 14, 2026.

## Primary persona

**A regional fire duty officer** at a provincial or national wildfire agency (for example a fire intelligence officer in a Canadian province, or a district fire officer in Zambia's Forestry Department). They are not a remote-sensing specialist. Each week in the season they must say, in a briefing, whether burning in their area is normal for the time of year, and they must plan crews and monitoring ahead of the months that usually burn most. They know FIRMS maps, but FIRMS shows where fires are now, not whether this month is unusual against 25 years, and they cannot put MODIS counts from 2005 next to VIIRS counts from 2025.

Scientists and land managers are secondary users: they are served by the same calendar plus the CSV export and the methods notes.

## User stories

1. As a fire duty officer, I want to pick my area and see a month-by-year calendar of burning activity since 2000, so that I can see at a glance which months and which years burned most.
2. As a fire duty officer, I want the current month compared with the historical median for my area, so that I can tell my briefing whether activity is below, near or above normal.
3. As a fire duty officer, I want the numbers to mean the same thing in 2003 as in 2025, whichever satellite saw the fire, so that a rise in the calendar is a rise in burning and not a change of sensor.
4. As an analyst, I want to download the hotspots and the monthly table for my search as CSV, so that I can check the numbers and use them in my own reports.

## Pilot regions

| Region | Fire regime | Why |
|---|---|---|
| **Canada** | Boreal and temperate forest. Few, very large, high-intensity wildfires in a short summer season (May to September); extreme year-to-year variation (2023 was a record) | The home region of this Local Event; anomalies matter most where years differ this much; high latitude means many overlapping overpasses, a hard case for harmonization |
| **Zambia** | Tropical savanna and miombo woodland. Very many small, low-intensity, mostly human-lit fires every dry season (May to November, peak August to September); similar from year to year | The opposite regime: small fires are where VIIRS 375 m sees far more than MODIS 1 km, so it stresses the harmonization differently; a regular season shows the calendar's seasonal pattern clearly |

Data for both are available without a login as FIRMS yearly per-country files (see `docs/data-access.md`).

## Scope

**Pilot regions only.** The app answers for any area (rectangle, or point with radius) inside Canada or Zambia. The data layout (one Parquet dataset partitioned by region, sensor and year; region configuration in `burn/config.py`) lets another country be added by adding one entry and re-running ingestion, so going global later is a data-volume question, not a redesign.

## Out of scope

- Global coverage, and areas outside the two pilot countries.
- Burned area, fire perimeters, fire spread or forecasting; smoke and emissions.
- Individual fire events (grouping hotspots into fires). The unit is the hotspot detection, not the fire.
- Real-time alerting. The current month is refreshed from FIRMS near real-time data, but the tool is for context, not dispatch.
- Landsat, GOES and other geostationary hotspots; VIIRS 750 m.
- User accounts, saved areas, uploads of custom polygons (shapefile, GeoJSON).
- Languages other than English.

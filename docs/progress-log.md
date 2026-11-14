# Progress log

## NEEDS YOU, 9:00 a.m.

1. **FIRMS MAP_KEY.** Request one at https://firms.modaps.eosdis.nasa.gov/api/map_key/ and paste it into `~/.config/nasa-burn/.env` as `FIRMS_MAP_KEY=<key>` (file exists, outside the repo, mode 600). Never put the key in the repo.
   - Status: a different Claude session (with your approval) is submitting this at 9:01 a.m. Check your email for the key, then paste it into the file above.
2. **FIRMS Archive Download request** at https://firms.modaps.eosdis.nasa.gov/download/ (sign in with Earthdata Login or emailed code). Parameters:
   - Region: Country, **Canada** (provisional boreal pilot). A second request with the same settings follows for the savanna pilot country once BURN-011 picks it (see log below).
   - Fire sources (standard quality / science archive where offered): **MODIS C6.1**, **VIIRS S-NPP 375 m**, **VIIRS NOAA-20 375 m**, **VIIRS NOAA-21 375 m**.
   - Date range: **2000-11-01 to 2026-11-13** for all (each sensor only returns what exists: MODIS from Nov 2000, S-NPP from Jan 2012, NOAA-20 from 2018 (NRT era, standard from ~2020), NOAA-21 from 2024).
   - Format: **Comma-Separated Text (.csv)**; tick email confirmation.
   - Status: the overnight session is submitting the Canada request (MODIS, S-NPP, NOAA-20) at 9:01 a.m. See "FIRMS requests (submitted by the overnight session)" below when it appears. NOAA-21 was not in the pre-filled form.
   - When the "your data is ready" emails arrive, download the zips into `data/raw/` in this project (gitignored) or tell a Claude session to.

## Log

- **Sat 09:00** kickoff session started. Created this log. Reading plan, rules, tasks.

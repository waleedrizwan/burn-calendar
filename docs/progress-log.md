# Progress log

## NEEDS YOU

1. **Approve the public GitHub repository** (BURN-023, needed for the submission link). When you say yes, a session runs: `gh repo create burn-calendar --public --source . --remote origin --push`. Until then the work is committed locally only, with no remote backup.
2. **Log in to Fly.io** for the Saturday deploy (BURN-021): run `fly auth login` in a terminal (the session has expired). Then approve the first public deploy.
3. **FIRMS archive emails** (low priority now): history for both pilot regions was downloaded another way (see 09:06 below), so the Archive Download request is only a backup. If the "data ready" email arrives, save the zip into `data/raw/archive/`. No Zambia request is needed.
4. **FIRMS MAP_KEY:** nothing to do. A valid key is already in the project's gitignored `.env`. If the 9:01 request emails you a new key, either works; optionally paste it into `~/.config/nasa-burn/.env`.

<details><summary>Original 9:00 a.m. request parameters (kept for the record)</summary>

1. **FIRMS MAP_KEY.** Request one at https://firms.modaps.eosdis.nasa.gov/api/map_key/ and paste it into `~/.config/nasa-burn/.env` as `FIRMS_MAP_KEY=<key>` (file exists, outside the repo, mode 600). Never put the key in the repo.
   - Status: a different Claude session (with your approval) is submitting this at 9:01 a.m. Check your email for the key, then paste it into the file above.
2. **FIRMS Archive Download request** at https://firms.modaps.eosdis.nasa.gov/download/ (sign in with Earthdata Login or emailed code). Parameters:
   - Region: Country, **Canada** (provisional boreal pilot). A second request with the same settings follows for the savanna pilot country once BURN-011 picks it (see log below).
   - Fire sources (standard quality / science archive where offered): **MODIS C6.1**, **VIIRS S-NPP 375 m**, **VIIRS NOAA-20 375 m**, **VIIRS NOAA-21 375 m**.
   - Date range: **2000-11-01 to 2026-11-13** for all (each sensor only returns what exists: MODIS from Nov 2000, S-NPP from Jan 2012, NOAA-20 from 2018 (NRT era, standard from ~2020), NOAA-21 from 2024).
   - Format: **Comma-Separated Text (.csv)**; tick email confirmation.
   - Status: the overnight session is submitting the Canada request (MODIS, S-NPP, NOAA-20) at 9:01 a.m. See "FIRMS requests (submitted by the overnight session)" below when it appears. NOAA-21 was not in the pre-filled form.
   - When the "your data is ready" emails arrive, download the zips into `data/raw/` in this project (gitignored) or tell a Claude session to.

</details>

## Log

- **Sat 09:00** kickoff session started. Created this log. Reading plan, rules, tasks.
- **Sat 09:01** BURN-023: local git repo, `uv` environment, README, `.gitignore`, app stub and test. Open: public GitHub repo (needs owner). `fly auth whoami` says the session expired (needs owner).
- **Sat 09:04** BURN-028: `LICENSE` (Apache 2.0), `docs/references.md`, `docs/ai-usage.md`. All criteria met; stays in-progress only because it depends on BURN-023.
- **Sat 09:05** BURN-011 done: persona, stories, pilot regions **Canada** and **Zambia**, scope, out-of-scope in `docs/scope.md`.
- **Sat 09:06** BURN-001: `docs/data-access.md`. Found FIRMS yearly per-country files (no login) and downloaded the full 2000 to 2025 history for both regions: 96 files, 3.0 GB, 36.5 M rows, in `data/raw/country/`. 2026 will come from the Area API (key works). Only the archive-request criterion is open, and it belongs to the other session; no "FIRMS requests (submitted by the overnight session)" entry had appeared yet.
- **Decision:** BURN-024 starts although BURN-001 and BURN-023 are not formally `done`, because their only open criteria wait on the owner or the other session and do not affect the build.

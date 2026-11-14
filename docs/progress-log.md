# Progress log

## NEEDS YOU

1. **GitHub repository:** created **private** on 2026-11-14 at owner's request (`waleedrizwan/burn-calendar`) and pushed. The rules need the final project link to open without a login, so make it public before submitting (BURN-026): `gh repo edit waleedrizwan/burn-calendar --visibility public --accept-visibility-change-consequences`.
2. **Cloudflare deploy (BURN-021):** hosting switched from Fly.io to Cloudflare Containers at owner's request. Config is in `wrangler.jsonc` and `worker/index.ts`, and the image was tested locally. `npx wrangler deploy` failed with 401 on the Containers API, because the existing Wrangler login has no Containers permission or the account is not on Workers Paid. To fix it: make sure the account has Workers Paid ($5/month), run `npx wrangler login` again to re-authorize, then `npx wrangler deploy`.
3. **App checked by hand (12:45 p.m.):** calendar, rectangle drawn on the map, point mode, both CSV downloads, and phone width all work. Minor: if the browser window is resized after the page loads, the map can show the wrong area until the page is reloaded.
4. **FIRMS archive emails** (low priority now): history for both pilot regions was downloaded another way (see 09:06 below), so the Archive Download request is only a backup. If the "data ready" email arrives, save the zip into `data/raw/archive/`. No Zambia request is needed.
5. **FIRMS MAP_KEY:** nothing to do. A valid key is already in the project's gitignored `.env`. If the 9:01 request emails you a new key, either works; optionally paste it into `~/.config/nasa-burn/.env`.

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
- **Sat 09:08 to 09:20** BURN-002 done (ingestion, schema; 2026 from the Area API, which hit the 5,000-transaction limit and took about 12 minutes). BURN-004, BURN-005, BURN-025, BURN-006 done (docs: `sensor-differences`, `harmonization-options`, `overlap-exploration`, `unit-decision`). Key findings: MODIS orbits drift after 2021; active 0.1 degree cell-days are the most stable unit; unit = VIIRS S-NPP-equivalent active cell-days.
- **Sat 09:17** BURN-007, BURN-008 done: harmonization passes all pre-set thresholds on the 2019 to 2021 hold-out in both regions (`docs/validation.md`). The 9:30 p.m. fallback is not needed.
- **Sat 09:18** BURN-009, BURN-013 done (`docs/architecture.md`, `docs/metrics.md`).
- **Sat 09:26** BURN-010 done (query API, 25 tests pass). BURN-015, 016, 017, 018 built and left `in-progress`: their acceptance criteria were not ticked because the interface has not been used by hand. BURN-024 done (superseded by the full app).
- **Not started:** BURN-021 (deploy: `Dockerfile`, `fly.toml`, `docs/deploy.md` are ready; needs Fly login and approval), BURN-026 (submission), BURN-003, BURN-012, BURN-019, BURN-022 (should), BURN-014 (stretch).
- **Not verified:** the Docker image has not been built. The 2026 clip (Natural Earth polygon) was not cross-checked against a FIRMS per-country file. NOAA-21 is not used.
- **Still no** "FIRMS requests (submitted by the overnight session)" entry in this file as of 09:27, so the first criterion of BURN-001 is unticked and BURN-001 stays `in-progress`.
- **Next session:** after the owner's checks, tick BURN-015 to 018, deploy (BURN-021), then BURN-019, BURN-022, BURN-026.
- **Sat 12:40 to 12:55** (the original setup session): the 9:01 FIRMS submission never ran (session restarted overnight); the archive form is still unsubmitted in Chrome and is no longer needed. App checked by hand. Private GitHub repo created and pushed. Cloudflare Containers deploy added; first deploy blocked by a 401 (see NEEDS YOU 2).

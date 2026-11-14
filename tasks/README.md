# Epic: Harmonized Burning Activity Calendar

Source: [`challengedescrption.md`](../challengedescrption.md)

## How the tasks are derived

The whole product reduces to one number in one calendar cell: **how much burning happened in area A during month M of year Y**. That number must mean the same thing in 2003 as it does today.

Five requirements follow from that. Every task exists because one of them would fail without it, and each task file states the principle it rests on and what fails if it is skipped.

## Task types

- **research**: a fact that is missing and can only be found by looking it up or measuring it.
- **brainstorm**: a choice with no single right answer.
- **decision**: a choice that evidence can settle.
- **build**: something to make once the above are settled.

## Priorities

- **must**: the submission fails without it.
- **should**: do it if time allows.
- **stretch**: only after every must is done.

An acceptance criterion that starts with "Stretch:" does not block a task from being done.

The deadline is Sunday, November 15, 2026 at 11:59 p.m. Eastern (Guelph Local Event). The board is scoped for one person: the `must` tasks add up to about 25 hours of work in a 39-hour window.

## Working on a task

Each task is one markdown file. Change `status` in its header to `in-progress` when starting and `done` when every acceptance criterion is ticked. A task is blocked while any task in its `depends` field is not done.

## Time limits

Every open task carries a `timebox`. For research, brainstorm and decision tasks it is a limit: when it runs out, write down what is known and move on. For build tasks it is a budget: when it runs out, ship what works, leave the rest as stretch, and move on.

## Board view

Run `python3 tasks/board.py` and open http://127.0.0.1:8765. The board reads and writes these files, so editing a file by hand and moving a card do the same thing.

## Solo plan

The rules say participants may not begin working on the project before the hackathon. No research or build task starts before Saturday, November 14 at 9:00 a.m. Eastern. BURN-020 and BURN-027 are done.

The `must` tasks run in this order, one at a time. Times are Eastern and leave about three hours of slack across the weekend.

| When | Tasks | Checkpoint |
|---|---|---|
| Sat 9:00 a.m. | The archive request from BURN-001 first, then BURN-023, BURN-028, BURN-011, and the rest of BURN-001 | Repo, licence and data access exist by 11:30 a.m. |
| Sat 11:30 a.m. | BURN-024, the first deploy of BURN-021, BURN-002 | By 1:00 p.m. a raw MODIS calendar runs locally, and by 1:45 p.m. it is at a public URL |
| Sat 3:00 p.m. | BURN-004, BURN-005, BURN-025, BURN-006 | By 6:00 p.m. the unit of burning activity is decided |
| Sat 6:00 p.m. | BURN-007, BURN-008 | By 9:30 p.m. the harmonized series is validated for both pilot regions |
| Sat 9:30 p.m. | BURN-009, BURN-013 | The stack and the anomaly formulas are written down |
| Sun 8:00 a.m. | BURN-010, BURN-015, BURN-016 | By 10:00 a.m. a first submission with the repository link and a draft summary is saved. By 2:30 p.m. the app shows the harmonized calendar for a selected area |
| Sun 2:30 p.m. | The redeploy of BURN-021 | By 3:15 p.m. the finished app is at the public URL |
| Sun 4:00 p.m. | BURN-017, BURN-018 | At 6:00 p.m. features freeze, finished or not |
| Sun 6:00 p.m. | BURN-026 | By 8:30 p.m. a first complete version is submitted |
| Sun 11:59 p.m. | | Deadline |

The first deploy on Saturday takes 45 minutes from the slack. The redeploy on Sunday is 45 minutes shorter than the single deploy it replaces, which gives the time back.

The kickoff is on Saturday at 9:00 a.m. in the Main Room voice channel of the event's Discord server, and its length is not stated, so the first block may start late. The Canadian Space Agency presentation at 10:30 a.m. is optional and recorded; it is not in the plan.

If the harmonization is not validated by Saturday 9:30 p.m., fall back to one scaling factor per pilot region fitted on the overlap period, state that limit in the README, and move on.

The `should` tasks (BURN-003, BURN-012, BURN-019, BURN-022) and the `stretch` task (BURN-014) use slack only. Further cuts are listed in [`docs/rules.md`](../docs/rules.md).

## 1. The number must exist

| Task | Title | Type | Priority | Time | Depends on |
|---|---|---|---|---|---|
| [BURN-001](BURN-001-firms-data-access.md) | FIRMS data access: products, coverage, formats, limits | research | must | 1h | none |
| [BURN-002](BURN-002-ingestion-pipeline-for-firms-archives.md) | Ingestion pipeline for FIRMS archives | build | must | 1h30 | BURN-001 |
| [BURN-003](BURN-003-keep-the-current-period-up-to-date.md) | Keep the current period up to date | build | should | 1h | BURN-002, BURN-007 |

## 2. The number must be comparable over time

| Task | Title | Type | Priority | Time | Depends on |
|---|---|---|---|---|---|
| [BURN-004](BURN-004-why-the-sensors-disagree.md) | Why the sensors disagree | research | must | 45m | none |
| [BURN-005](BURN-005-how-others-have-harmonized-modis-and-viirs.md) | How others have harmonized MODIS and VIIRS | research | must | 30m | none |
| [BURN-006](BURN-006-define-the-unit-of-burning-activity.md) | Define the unit of burning activity | decision | must | 30m | BURN-004, BURN-005, BURN-025 |
| [BURN-007](BURN-007-implement-harmonization.md) | Implement harmonization | build | must | 2h30 | BURN-002, BURN-006 |
| [BURN-008](BURN-008-validate-the-harmonization.md) | Validate the harmonization | build | must | 1h | BURN-007 |
| [BURN-025](BURN-025-explore-modis-against-viirs-in-the-overlap-period.md) | Explore MODIS against VIIRS in the overlap period | research | must | 1h | BURN-002, BURN-011 |

## 3. The number must be answerable for any area

| Task | Title | Type | Priority | Time | Depends on |
|---|---|---|---|---|---|
| [BURN-009](BURN-009-architecture-and-data-volume-spike.md) | Architecture and data-volume spike | decision | must | 30m | BURN-002, BURN-006 |
| [BURN-010](BURN-010-query-api.md) | Query API: area and date range to analytics | build | must | 2h | BURN-007, BURN-009 |

## 4. A person must be able to read it

| Task | Title | Type | Priority | Time | Depends on |
|---|---|---|---|---|---|
| [BURN-011](BURN-011-decide-the-primary-user-scope-and-pilot-regions.md) | Decide the primary user, scope and pilot regions | brainstorm | must | 30m | none |
| [BURN-012](BURN-012-prior-art.md) | Prior art: existing fire calendars and dashboards | research | should | 30m | none |
| [BURN-013](BURN-013-define-calendar-metrics-and-anomaly-statistics.md) | Define calendar metrics and anomaly statistics | brainstorm | must | 30m | BURN-011 |
| [BURN-014](BURN-014-calendar-and-dashboard-design-sketches.md) | Calendar and dashboard design sketches | brainstorm | stretch | 30m | BURN-011, BURN-012 |
| [BURN-015](BURN-015-app-shell-and-map-with-area-selection.md) | App shell and map with area selection | build | must | 2h | BURN-009, BURN-024 |
| [BURN-016](BURN-016-burning-activity-calendar.md) | Burning activity calendar | build | must | 2h | BURN-010, BURN-013, BURN-024 |
| [BURN-017](BURN-017-anomaly-and-historical-comparison-views.md) | Anomaly and historical comparison views | build | must | 1h | BURN-016 |
| [BURN-018](BURN-018-csv-and-chart-export.md) | CSV and chart export | build | must | 1h | BURN-010, BURN-016 |
| [BURN-019](BURN-019-accessibility-and-usability-check.md) | Accessibility and usability check | build | should | 45m | BURN-017 |
| [BURN-024](BURN-024-walking-skeleton.md) | Walking skeleton: raw MODIS calendar for one region | build | must | 1h30 | BURN-001, BURN-023 |

## 5. Someone else must be able to trust and judge it

| Task | Title | Type | Priority | Time | Depends on |
|---|---|---|---|---|---|
| [BURN-020](BURN-020-challenge-rules-deliverables-and-judging-criteria.md) | Challenge rules, deliverables and judging criteria | research | must | done | none |
| [BURN-021](BURN-021-deploy-a-public-demo.md) | Deploy a public demo | build | must | 1h30 | BURN-024 |
| [BURN-022](BURN-022-methods-and-data-sources-page.md) | Methods and data sources page | build | should | 1h | BURN-008 |
| [BURN-023](BURN-023-repository-and-environment-setup.md) | Repository and environment setup | build | must | 30m | none |
| [BURN-026](BURN-026-pitch-demo-and-submission.md) | Pitch, demo and submission | build | must | 2h30 | BURN-011, BURN-020, BURN-021, BURN-027, BURN-028 |
| [BURN-027](BURN-027-team-registration-and-eligibility.md) | Team registration and eligibility | build | must | done | BURN-020 |
| [BURN-028](BURN-028-licence-references-and-ai-use-record.md) | Licence, references and AI-use record | build | must | 30m | BURN-020, BURN-023 |

## Coverage check against the challenge text

Each thing the challenge asks for or suggests, and the task that delivers it. A request with no task here is a gap.

| The challenge asks for | Task |
|---|---|
| Harmonize MODIS and VIIRS so the sensor of origin no longer matters | BURN-006, BURN-007, BURN-008 |
| A web application that takes harmonized data as input | BURN-010, BURN-024 |
| Select a region: draw on a map or enter latitude and longitude | BURN-015 |
| Select a date range | BURN-015 |
| A calendar from the early 2000s to the present | BURN-016 |
| Which periods of the year and which years had the most activity | BURN-016 |
| Current month against the historical median | BURN-013, BURN-017, with the archive as downloaded; BURN-003 brings it up to date |
| Anomalies against multi-year averages and trends | BURN-013, BURN-017 |
| Accessible color ramps | BURN-016, BURN-019 |
| Downloadable CSV of hotspots from a search | BURN-018 |
| Downloadable analytics and visualizations | BURN-018 |
| Number of fires detected and reported | BURN-013 fixes the wording as hotspot detections, because a hotspot is not a fire |

Every row is delivered by at least one task marked must.

## Coverage check against the rules

The judging criteria and the required deliverables are mapped to tasks in [`docs/rules.md`](../docs/rules.md). A criterion or deliverable with no task there is a gap.

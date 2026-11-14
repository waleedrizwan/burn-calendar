# Why MODIS and VIIRS hotspot counts disagree (BURN-004)

Written Saturday, November 14, 2026. "Measured" means computed from the FIRMS data downloaded for the two pilot regions (Canada, Zambia; 2000 to 2025). Other statements come from the FIRMS FAQ and attribute tables and from the algorithm papers listed in [`references.md`](references.md).

## Differences and their effect on counts

| Difference | MODIS (Terra, Aqua) | VIIRS 375 m (S-NPP, NOAA-20) | Effect on counts |
|---|---|---|---|
| Pixel size at nadir | 1 km | 375 m | One fire front that fills one MODIS pixel can fill about seven VIIRS pixels, and VIIRS sees small or cool fires that MODIS misses. VIIRS counts are several times higher. Measured, vegetation fires 2012 to 2021: see `overlap-exploration.md` |
| Pixel growth at the swath edge | Up to about 4.8 km x 2 km | Stays near 375 to 800 m (pixel aggregation scheme) | MODIS loses small fires towards the swath edge and can see one fire twice in adjacent scans (the "bow-tie" effect). The MODIS deficit is not constant across the swath |
| Swath width | 2,330 km: gaps between orbits near the equator | 3,040 km: no gaps, more overlap | At low latitude (Zambia) one MODIS satellite misses some areas on some days. At high latitude (Canada) both overlap several orbits a day, so one fire can be counted on consecutive passes, and VIIRS does so more often |
| Overpass time (local solar) | Terra about 10:30 and 22:30; Aqua about 13:30 and 01:30 | About 13:30 and 01:30 | Fire activity peaks in the early afternoon. Terra sees much less than Aqua (measured in Zambia: Terra 1.4 million detections, Aqua 3.4 million over the record). Aqua and VIIRS sample the same part of the day; Terra does not |
| Number of satellites | One (Terra) to July 2002; two since | One (S-NPP) from 2012; two from April 2018; one (NOAA-20) after 2 November 2026 in this project | Adding a satellite adds detections without any change in burning. Counts must be defined per satellite or per fixed configuration |
| Orbit drift | Terra and Aqua no longer hold their crossing times. Measured median daytime local time in Zambia: Terra 10.42 h through 2020, 10.36 (2021), 10.20 (2022), 9.97 (2023), 9.65 (2024), 9.18 (2025); Aqua 13.7 h through 2021, 13.79 (2022), 13.99 (2023), 14.35 (2024), 14.95 (2025) | Stable: 13.55 to 13.62 h in every year | MODIS counts since 2022 drift for a reason that is not burning: Terra moves into the morning minimum, Aqua moves past the afternoon peak. **MODIS after 2021 should not be used for calibration or as the record where VIIRS exists** |
| Detection algorithm | Contextual test on 4 and 11 µm channels, Collection 6.1 (Giglio et al.) | Contextual test on the I-4 and I-5 bands (Schroeder et al. 2014); better at night | The gain from VIIRS is larger at night and for small fires, so the VIIRS to MODIS ratio depends on the fire regime and time of day |
| Confidence | 0 to 100 percent | low, nominal, high | Not the same scale. Measured share of low confidence among vegetation-fire detections, 2018 to 2021: MODIS about 6 percent (Canada) and 3 percent (Zambia); VIIRS about 4 percent (Canada) and 18 percent (Zambia, daytime; low-confidence VIIRS daytime pixels are typically sun glint or weak anomalies) |
| `type` | Standard data only | Standard data only | Types 1 to 3 (volcano, static land source such as gas flares and industry, offshore) are not burning vegetation. Measured share: MODIS 0.15 percent in both regions; VIIRS 4.1 percent in Canada (1.5 percent static, 2.6 percent offshore), 0.2 percent in Zambia. VIIRS detects far more static sources |
| Near real-time data | No `type`; geolocation less exact | Same | Static sources cannot be removed from NRT months by `type` |
| Fire radiative power | Per 1 km pixel | Per 375 m pixel; saturates on intense fires | FRP sums are not directly comparable either |

## Which satellites were active

| Period | MODIS | VIIRS | Note |
|---|---|---|---|
| Nov 2000 to Jun 2002 | Terra | none | Morning and late evening overpasses only |
| Jul 2002 to Jan 2012 | Terra, Aqua | none | The core MODIS record |
| Jan 2012 to Mar 2018 | Terra, Aqua | S-NPP | Overlap, one VIIRS |
| Apr 2018 to 2021 | Terra, Aqua | S-NPP, NOAA-20 | Overlap, two VIIRS, MODIS orbits still stable |
| 2022 to Nov 2, 2026 | Terra, Aqua (drifting) | S-NPP, NOAA-20 (and NOAA-21 from 2023, not used here) | MODIS no longer comparable with its own past |
| From Nov 3, 2026 | Terra, Aqua (drifting; planned end 2027) | NOAA-20 (and NOAA-21) | S-NPP delivery ended |

## Filters to apply

1. **Keep `type` = 0 only** in standard data. Volcanoes, gas flares, industry and offshore sources are not burning activity, and VIIRS detects many more of them than MODIS, so they would bias the ratio.
2. **Near real-time rows (no `type`): drop detections that fall in grid cells known to hold static sources**, where a static cell is a 0.01 degree cell with repeated type 2 or 3 detections in the standard record.
3. **Keep all confidence levels.** The two scales are not equivalent, so a confidence cut removes different things from each sensor, and FIRMS says the meaning of confidence varies by region. The calibration absorbs the difference. (Low-confidence detections remain in the hotspot CSV export with their confidence value, so a user can filter.)
4. **Count day and night detections separately** in the aggregates, because the VIIRS gain over MODIS is larger at night. Whether the calibration needs separate factors is tested in BURN-025.
5. **Count each satellite separately**, never a pooled total, so that the number of satellites in orbit cannot change the unit.
6. **Use MODIS only up to 2021 for fitting**, and not as the record from 2012 on, because of the orbit drift.
7. **Mark days when a satellite delivered nothing** (below) so that an outage is not read as a quiet period.

## Outages and gaps (stretch, measured)

Runs of days with no detections at all in Zambia during the fire season (June to October), where every operating satellite sees fires daily:

| Satellite | Gap | Days |
|---|---|---|
| Terra | 2001-06-15 to 2001-07-03 | 19 (no other satellite then: a true gap in the record) |
| Aqua | first weeks after launch, 2002-07-30 to 2002-09-14 | 11 scattered |
| Aqua | 2020-08-16 to 2020-09-01 | 17 |
| Terra | 2022-10-11 to 2022-10-23 | 13 |
| S-NPP | 2022-07-27 to 2022-08-10 | 15 |
| S-NPP | 2024, scattered between June and September | 14 |
| NOAA-20 | 2023, scattered between July and September | 5 |

Gaps outside the fire season cannot be found this way; the FIRMS FAQ lists more.

# How others have harmonized MODIS and VIIRS (BURN-005)

Written Saturday, November 14, 2026. Sources were found by web search; "abstract" means only the abstract or a search record was read, not the full text.

## What the literature says about the difference

| Source | Finding |
|---|---|
| Schroeder, Oliva, Giglio, Csiszar (2014), RSE 143:85–96, [doi:10.1016/j.rse.2013.12.008](https://doi.org/10.1016/j.rse.2013.12.008) (abstract) | The VIIRS 375 m algorithm. Much better detection of small fires and at night than coarser products |
| Giglio, Schroeder, Justice (2016), RSE 178:31–41, [doi:10.1016/j.rse.2016.02.054](https://doi.org/10.1016/j.rse.2016.02.054) (abstract) | The MODIS Collection 6 algorithm |
| Li, Zhang, Kondragunta, Csiszar (2018), JGR Atmospheres 123:4545–4563, [doi:10.1029/2017JD027823](https://doi.org/10.1029/2017JD027823) (abstract) | Aqua MODIS against S-NPP FRP: MODIS FRP depends strongly on view angle, VIIRS does not. On a 1 degree grid FRP differs by about 20 percent in fire-prone regions; VIIRS is lower for large boreal fires |
| Li, Zhang, Kondragunta (2020), Remote Sensing 12:1561, [doi:10.3390/rs12101561](https://doi.org/10.3390/rs12101561) (abstract) | Africa: MODIS misses many low-intensity fires and underestimates daily FRP |
| Fu et al. (2020), Remote Sensing 12:2870, [doi:10.3390/rs12182870](https://doi.org/10.3390/rs12182870) (abstract) | Northeast Asia, 2012 to 2017: MODIS missed about 65 percent of VIIRS fire pixels in forest and 83 percent in low-biomass land |
| Vadrevu and Lasko (2018), Remote Sensing 10:978, [doi:10.3390/rs10070978](https://doi.org/10.3390/rs10070978) (read: [PMC6108185](https://pmc.ncbi.nlm.nih.gov/articles/PMC6108185/)) | Punjab crop fires: VIIRS counts are 4.8 times Terra+Aqua and 6.5 times Aqua alone; monthly FRP sums correlate at r² = 0.98 |
| Wooster et al. (2021), RSE 267:112694, [doi:10.1016/j.rse.2021.112694](https://doi.org/10.1016/j.rse.2021.112694) (abstract) | Review of satellite active fire remote sensing |

So the VIIRS to MODIS count ratio is roughly 3 to 6 and depends on the fire regime. Our own measurement (`overlap-exploration.md`) gives 4.8 in Canada and 4.3 in Zambia for raw counts.

## Approaches

| Approach | Who uses it | Data needs | Complexity | Failure modes |
|---|---|---|---|---|
| **1. Multiplicative scaling fitted on the overlap**, per cell, biome or region | Operational emission systems do this for FRP: NASA QFED (biome- and satellite-specific regression against Aqua MODIS; conference slides only) and ECMWF GFAS (bias-corrects VIIRS FRP to its MODIS baseline; not verified in a paper). GFED5 (Chen et al. 2023, ESSD 15:5227, [doi:10.5194/essd-15-5227-2023](https://doi.org/10.5194/essd-15-5227-2023)) scales active-fire area by region and land cover, by analogy | Co-gridded counts from both sensors in the overlap | Low | Ratios are unstable where counts are low; the ratio changes with fire size, season and time of day; orbit drift and outages contaminate the overlap; assumes the relationship holds outside the overlap |
| **2. Count active grid cells per day** instead of detections (presence or absence on a coarser grid) | No peer-reviewed precedent found for MODIS to VIIRS; the nearest relative is the 0.5 degree MODIS Climate Modeling Grid product (Giglio, Csiszar, Justice 2006, [doi:10.1029/2005JG000142](https://doi.org/10.1029/2005JG000142)) | Point detections only | Low | Saturates where burning is dense (a cell is active or not, however much burns); VIIRS still finds small fires MODIS never sees, so a scaling step remains; depends on the grid size |
| **3. Fire radiative power** in place of counts | Li et al. 2018 and 2020; Fu et al. 2020 | FRP, view angle | Medium | MODIS view-angle bias; VIIRS I-band saturation on intense fires; FRP is not what the challenge asks to count |
| **4. Statistical calibration** (regression with covariates, quantile mapping) | QFED uses linear regression; no fire-count example found | Overlap series and covariates | Medium to high | Overfitting; extrapolation beyond the overlap range; many zeros |

We found no peer-reviewed harmonized MODIS and VIIRS hotspot-count record. FINN v2.5 (Wiedinmyer et al. 2023, [doi:10.5194/gmd-16-3873-2023](https://doi.org/10.5194/gmd-16-3873-2023)) runs MODIS-only and MODIS+VIIRS as separate versions and does not harmonize them.

## Recommendation

**Combine 2 and 1.** First reduce the resolution difference by counting active 0.1 degree cell-days per satellite configuration (approach 2), then remove what remains with a small set of multiplicative factors fitted on the 2012 to 2021 overlap (approach 1), with held-out years for validation. It needs only the point data we already have, is explainable in one sentence, and fits the time available. FRP (approach 3) is kept as a cross-check only, and regression with covariates (approach 4) is out of scope for the weekend.

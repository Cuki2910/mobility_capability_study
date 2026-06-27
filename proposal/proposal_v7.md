# Fragmented Mobility Capability in Motorcycle-Dependent Green Megaprojects

## A Dual-Scale and Mode-Competitive Accessibility Framework from Vinhomes Ocean Park, Hanoi

Working proposal v8 draft. Last updated: 2026-06-25.

## 1. Summary

This study examines whether a green-branded megaproject can produce sustainable mobility capability when residents still live in a motorcycle-dominant metropolitan travel environment. The empirical case is Vinhomes Ocean Park in Gia Lam, Hanoi, where local amenities, electric-bus branding, and planned urban form coexist with the continued practical advantage of motorcycles.

The proposal develops a dual-scale and mode-competitive accessibility framework. It separates neighborhood walking access from metropolitan opportunity access, then evaluates whether walking and transit are competitive with motorcycle access. The central metric is the Sustainable Mobility Capability Index (SMCI), defined as the joint presence of local access, metropolitan access, and relative competitiveness against motorcycles.

The current implementation is a pilot, not a full final study. It covers 462 grid cells around Vinhomes Ocean Park and uses real OSM walking and driving networks, Hanoi GTFS as a pre-VinBus transit baseline, VinBus pseudo-GTFS for the intervention scenario, OSM plus Overture POIs, OSM landuse/office enrichment for economic opportunities, WorldPop, VIDA building footprints, and manual Android Google Maps motorcycle checks. The pipeline runs end to end and passes 70 tests.

## 2. Research Problem

Green megaprojects are often evaluated through internal amenities, environmental branding, and transit provision. These indicators are necessary but incomplete in a city such as Hanoi, where motorcycles remain fast, flexible, affordable, and embedded in everyday travel.

The key problem is fragmentation. A neighborhood may provide nearby schools, parks, shops, and services, yet residents may still need motorcycles to reach jobs, higher education, hospitals, or wider metropolitan opportunities. In that case, local completeness does not become sustainable mobility capability. This study treats that mismatch as fragmented mobility capability.

## 3. Research Questions

RQ1. How much neighborhood-scale walking accessibility exists within and around Vinhomes Ocean Park?

RQ2. How much metropolitan opportunity accessibility is available through walking plus conventional transit, and how does it change with VinBus?

RQ3. Where is walking-and-transit accessibility competitive with motorcycle accessibility?

RQ4. Which spatial typologies emerge when local accessibility and metropolitan competitiveness are evaluated together?

RQ5. Does VinBus improve sustainable mobility capability broadly, or mainly for selected corridors and cells?

## 4. Contribution

The study contributes three elements.

First, it separates local walkability from metropolitan mobility capability. This avoids treating local POI proximity as sufficient evidence of sustainable mobility.

Second, it introduces Relative Accessibility Competitiveness (RAC), which compares walking-and-transit performance against motorcycle performance. This is important for Southeast Asian cities where the main competitor to public transport is often the motorcycle, not the private car.

Third, it produces a theory-first typology: Integrated Capability, Fragmented Capability, Transit-Dependent, and Motorcycle Lock-in. The typology is designed for interpretation and planning, not purely for cluster optimization.

## 5. Study Area

The study area is Vinhomes Ocean Park and its surrounding Gia Lam context in Hanoi. The site is suitable because it combines planned green-urban branding, internal amenities, VinBus services, and exposure to Hanoi's motorcycle-oriented regional mobility system.

The analysis uses a 250 m grid. The pilot contains 462 cells, allowing neighborhood-scale variation to be observed while keeping network routing feasible.

## 6. Data

The confirmed pilot data are:

| Data source | Use | Current status |
| --- | --- | --- |
| OSM walking network | Network A, NAI routing | Fetched for pilot |
| OSM driving network | Network D motorcycle routing base | Fetched for pilot |
| OSM POIs | Baseline local opportunities | 106 POIs; 20-record spot check complete |
| Overture Maps Places | POI supplement | Fetched; gate passed; merged with OSM |
| OSM landuse and office tags | Economic and higher-education enrichment | 47 fresh POIs added; primary POI layer now 208 POIs |
| Building footprints | Built-cell audit, population cross-check, opportunity proxy support | 41,816 VIDA footprints fetched; 455/462 cells built |
| Hanoi GTFS | Network B baseline transit | 2018 World Bank feed; pre-VinBus baseline |
| VinBus pseudo-GTFS | Network C intervention | API-derived feed; 176 routes, 5,631 stops, observed headways 5-48 min |
| WorldPop 2020 | Population exposure check | Downloaded; about 92.77 m raster resolution |
| Android Google Maps checks | Motorcycle validation | 10 OD pairs manually measured |

The 2018 Hanoi GTFS is not treated as current service. It is used as a deliberate pre-VinBus conventional transit baseline because VinBus launched later. A post-2021 GTFS feed, if verified, should be used as a future sensitivity test rather than a replacement for the baseline logic.

The VinBus feed is a pseudo-GTFS representation built from the public VinBus web API. Because no official GTFS is published, this is reported as a transparent proxy. OSM VinBus relations are retained as a sensitivity source.

The POI layer is still open-data based. OSM and Overture improve coverage, and economic enrichment reduces a weak commercial-proxy problem, but the resulting MAI is still an opportunity proxy, not a census employment measure.

## 7. Network and Scenario Definitions

The framework uses four networks.

| Network | Definition | Role |
| --- | --- | --- |
| A | Walking | Local access and walk approach links |
| B | Walking + conventional transit | Scenario A baseline |
| C | Walking + conventional transit + VinBus | Scenario B intervention |
| D | Motorcycle | Competitive benchmark |

Scenario A combines Networks A and B and represents the no-VinBus baseline. Scenario B combines Networks A and C and represents the VinBus intervention. Network D is used in both scenarios to calculate motorcycle competitiveness.

Motorcycle travel time is not raw car-equivalent OSM driving time. The routing uses calibrated motorcycle speed assumptions, then checks plausibility against manual Android Google Maps motorcycle-mode measurements.

## 8. Index Construction

### 8.1 Neighborhood Accessibility Index

The Neighborhood Accessibility Index (NAI) measures local walking access to daily opportunities:

```text
NAI_i = count of qualifying POIs reachable by walking within the neighborhood threshold
```

NAI is count-based because the neighborhood question is whether daily functions are present within a walkable catchment.

### 8.2 Metropolitan Accessibility Index

The Metropolitan Accessibility Index (MAI) measures walking-and-transit access to metropolitan opportunities. It is framed as Metropolitan Opportunity Accessibility rather than direct employment accessibility, because building-resolution employment counts are not available.

Four opportunity domains are used:

| Domain | Weight |
| --- | ---: |
| Economic opportunities | 0.40 |
| Higher education | 0.20 |
| Tertiary healthcare | 0.20 |
| Metropolitan commercial/services | 0.20 |

For each cell `i` and domain `k`:

```text
A_i,k = sum_j opportunity_weight_j,k * f(t_ij)
```

The `opportunity_weight_j,k` combines three signals: a POI-type base weight, a building-footprint
magnitude scaling where a matched footprint exists, and a supply-side population multiplier
`m_j = clip(sqrt(pop_density_j / median), 0.5, 2.0)` that scales each opportunity by the residential
density of the grid cell containing it (an opportunity in a denser catchment serves a larger market).
The square root damps the signal and median-centering leaves a typical-density opportunity unchanged,
so population refines magnitudes without letting any single domain dominate. The same effective weights
enter the transit and motorcycle MAI so the RAC_opp ratio stays internally consistent.

with a linear time-decay function:

```text
f(t) = 1               if t <= 30 min
     = (60 - t) / 30  if 30 < t <= 60 min
     = 0              if t > 60 min
```

The composite MAI is:

```text
MAI_i = 0.40*A_i,economic + 0.20*A_i,education
      + 0.20*A_i,healthcare + 0.20*A_i,commercial
```

Economic enrichment now uses OSM landuse polygons, office tags, financial/marketplace features, and corrected domain classification. After enrichment, the primary POI layer contains 208 POIs. Domain decomposition over motorcycle-accessible MAI mass is: economic 54.1%, higher education 24.7%, metropolitan commercial/services 15.5%, and tertiary healthcare 5.8% — unchanged after adding the supply-side population multiplier, which scales all domains proportionally. Opportunity magnitudes are derived from POI type, building footprint, and residential population density rather than direct employment or enrollment counts, which remain unavailable at building resolution for Hanoi; the measure is therefore an opportunity-magnitude index grounded in observable supply and population, not a census of jobs. Integrating population into MAI changes mean SMCI_B only marginally (no-population sensitivity gives Cohen's kappa = 0.976, with 8 of 462 cells relabelled).

### 8.3 Relative Accessibility Competitiveness

Relative Accessibility Competitiveness (RAC) asks whether walking and transit can compete with motorcycles.

```text
RAC_time_raw_i = motorcycle_travel_time_i / walk_transit_travel_time_i
RAC_opp_raw_i  = MAI_transit_i / MAI_motorcycle_i
```

`RAC_time_raw_i` is operationalized as motorcycle opportunity-weighted mean travel time divided by walk-transit opportunity-weighted mean travel time. It uses the same metropolitan opportunity set, domain weights, POI opportunity weights, and 60-minute cutoff as MAI. Cells with no reachable weighted destination receive the cutoff. Network B uses the 2018 GTFS stop-proximity timing proxy; Network C uses pseudo-GTFS stop routing with access, wait, line-haul, and egress components. The input table reports `moto_mean_opp_time_min`, `wt_A_mean_opp_time_min`, and `wt_B_mean_opp_time_min` for auditability.

Both `MAI_transit` and `MAI_motorcycle` use the same opportunity domains, weights, and decay function. The ratios are normalized, then combined:

```text
RAC_i = sqrt(RAC_time_i * RAC_opp_i)
```

The geometric mean is intentional. A mode is not competitive if it is fast but reaches few opportunities, or reaches many opportunities but is too slow.

### 8.4 Sustainable Mobility Capability Index

The primary index is:

```text
SMCI_i = NAI_norm_i * MAI_norm_i * RAC_norm_i
```

SMCI is a weakest-link index. A cell needs local walking access, metropolitan opportunity access, and mode competitiveness at the same time.

Scenario A/B comparison uses shared normalization bounds across both scenarios. Delta SMCI is therefore:

```text
Delta_SMCI_i = SMCI_B_i - SMCI_A_i
```

computed on a common scale, not from separately normalized scenario scores.

## 9. Typology

The typology uses two axes: NAI and Metropolitan Competitiveness Score (MCS).

```text
MCS_i = sqrt(MAI_norm_i * RAC_norm_i)
```

Cells are split by rank-based medians of NAI and MCS.

| NAI | MCS | Typology | Meaning |
| --- | --- | --- | --- |
| High | High | Integrated Capability | Local access and metropolitan competitiveness both present |
| High | Low | Fragmented Capability | Local access exists, but metropolitan sustainable mobility is weak |
| Low | High | Transit-Dependent | Metropolitan access exists despite weak local access |
| Low | Low | Motorcycle Lock-in | Local access and sustainable metropolitan competitiveness are both weak |

Rank-based medians preserve the four conceptual categories even when indicators contain ties or mass points. K-means is used only as robustness, not as the primary classifier.

## 10. Validation and Robustness

The validation strategy has five parts.

First, POI validation combines a manual OSM spot check and an Overture gate. The OSM spot check reviewed 20 records: 14 confirmed, 2 duplicates, 2 misclassified, and 2 missing/unverified. The Overture-only gate passed with 55/55 confirmed before promotion to the merged layer.

Second, motorcycle routing is checked against 10 Android Google Maps motorcycle OD pairs. The current mean absolute error is about 1.90 minutes, with model bias about -1.04 minutes.

Third, multicollinearity is reported because MAI and RAC_opp share the MAI_transit component. In the current pilot, VIF is high in the primary specification:

| Variable | VIF | Status |
| --- | ---: | --- |
| NAI | 2.67 | OK |
| MAI | 8.21 | High |
| RAC | 7.90 | High |

The RAC_time-only contingency reduces collinearity:

| Variable | VIF | Status |
| --- | ---: | --- |
| NAI | 2.59 | OK |
| MAI | 3.25 | OK |
| RAC_time | 1.86 | OK |

Primary versus RAC_time-only typology agreement is strong: Cohen's kappa = 0.9004, Spearman rho(SMCI rank) = 0.9875, and 32/462 cells change label. The primary full-RAC specification is retained, with RAC_time-only reported as robustness.

Fourth, SMCI robustness uses an additive alternative:

```text
SMCI_additive_i = (NAI_norm_i + MAI_norm_i + RAC_norm_i) / 3
```

This is meaningful because it allows compensation across dimensions. A geometric mean alternative is not used because it is only a monotonic transformation of the multiplicative product.

Fifth, built-cell and population audits check whether zero-access results are open-space artifacts. VIDA building footprints are present in 455/462 cells, and many zero-access cells are built and populated. Zero inflation is therefore interpreted cautiously rather than dismissed.

## 11. Current Pilot Results

The current pilot results are:

| Metric | Value |
| --- | ---: |
| Grid cells | 462 |
| Mean SMCI_A | 0.0322 |
| Mean SMCI_B | 0.0435 |
| Mean Delta SMCI | 0.0113 |
| Improved cells | 298 / 462 (64.50%) |
| Unchanged cells | 88 / 462 (19.05%) |
| Declined cells | 76 / 462 (16.45%) |
| Motorcycle validation MAE | 1.90 min |

The pilot results should be interpreted through distributional and spatial diagnostics rather than the global mean alone. Mean SMCI rises from 0.0322 in Scenario A to 0.0435 in Scenario B, but this average is affected by zero-inflation in the weakest-link index. In the walking-access layer, 88 of 462 cells (19.0%) have zero NAI; the same 88 cells also have zero SMCI_B because any zero component collapses the multiplicative index. Cross-checking these zero-access cells against VIDA building footprints shows that 84 of them (95.5%) are built cells, so zero accessibility is not simply a lake, park, or open-space artifact.

The VinBus scenario improves SMCI in 298 of 462 cells (64.5%), while 88 cells (19.0%) remain unchanged and 76 cells (16.5%) decline slightly under the opportunity-weighted time-competitiveness term. Among cells with positive SMCI, the median rises from 0.0197 in Scenario A to 0.0220 in Scenario B. This non-zero median comparison is more interpretable than the global mean for cells that have at least some sustainable mobility capability. The unchanged group remains analytically important: these cells identify locations where adding metropolitan transit access does not overcome missing neighborhood walking access or weak local opportunity structure.

Scenario B typology counts are:

| Typology | Count |
| --- | ---: |
| Integrated Capability | 166 |
| Fragmented Capability | 65 |
| Transit-Dependent | 65 |
| Motorcycle Lock-in | 166 |

The equal high/low structure is expected under a rank-median typology and should not be interpreted as a discovered natural cluster distribution. The substantive interpretation depends on where those cells are located and how stable they are under robustness checks.

The population-weighted cross-check remains a useful caution. Total estimated population is about 78,816. Population-weighted mean SMCI_B is 0.0423, compared with an unweighted mean of 0.0435, a difference of -2.7%. Spearman rho between population and SMCI_B is -0.0173 (p = 0.711), so population is roughly evenly distributed across SMCI levels. Population shares by typology are: Integrated Capability 31.1%, Fragmented Capability 19.6%, Transit-Dependent 16.0%, and Motorcycle Lock-in 33.4%.

The built/population zero-access audit adds a second caution. The 84 built zero-NAI cells contain about 11,798 residents, or 15.0% of the pilot population. Zero accessibility is therefore not only a lake/park/open-space issue; it is a substantive access and mapping uncertainty issue that should be reported separately from low-but-positive accessibility.

## 12. Expected Argument

The expected argument is not simply that VinBus improves accessibility. The stronger contribution is that improvement can coexist with persistent fragmentation.

Ocean Park may show high local amenity access in some cells, and VinBus may improve transit-based metropolitan access, but motorcycle competitiveness can still dominate in many locations. The key empirical question is whether cells move into Integrated Capability or remain in Fragmented Capability and Motorcycle Lock-in.

The pilot already suggests this mixed pattern: mean SMCI improves and 64.5% of cells improve, but 19.0% remain unchanged, 16.5% decline slightly under the time-competitiveness term, population-weighted SMCI_B is lower than the unweighted mean, and Motorcycle Lock-in contains the largest population share.

## 13. Limitations

This is a single-site study. It supports theory-building and methodological contribution, not national generalization.

Network B uses a 2018 GTFS feed as a pre-VinBus baseline. This is methodologically deliberate but not equivalent to current conventional transit service.

Network C uses a pseudo-GTFS built from VinBus public API data, not an official GTFS feed. It is more detailed than a corridor proxy, but still not a full validated timetable product.

MAI is an open-data opportunity proxy. Economic enrichment improves the domain balance, but it is not a direct employment census. Nighttime lights, enterprise census data, or verified employment layers would strengthen the final paper.

POI completeness remains uncertain despite OSM checks, Overture gating, and economic enrichment.

Motorcycle validation uses 10 manual OD pairs. It is a useful plausibility check, not a full calibration dataset.

MAI/RAC collinearity is structurally high in the full-RAC specification. The RAC_time-only sensitivity reduces VIF and shows high typology agreement, so the issue is reported rather than hidden.

Mode and impedance specifications omit fares, parking, explicit transfer penalties, access/egress discomfort, and schedule unreliability. Transit-impedance sensitivity now partially bounds this by testing conservative and pessimistic wait/access/egress/reliability penalties; it is not a replacement for observed mode-choice data.

Motorcycle speed sensitivity tests slow-congestion and fast-lane-splitting scenarios. Typology is stable (kappa = 0.994; 2 cells relabelled), but the paper should still frame this as a bounded robustness check rather than full behavioral validation.

## 14. Work Plan

Immediate next steps:

1. Keep the 208-POI enriched layer as the current primary input and preserve OSM-only / Overture-only / economic-enrichment audit trails.
2. Refresh all validation outputs after each pipeline run so proposal numbers, supervisor memo, and self-audit remain synchronized.
3. Use maps and spatial narratives to interpret where Integrated Capability, Fragmented Capability, Transit-Dependent, and Motorcycle Lock-in cells occur.
4. Treat TUMI or other post-2021 Hanoi GTFS candidates only as current-service sensitivity after license and service-date checks.
5. Strengthen MAI with external opportunity proxies if available, especially nighttime lights or enterprise/employment data.
6. Prepare the supervisor package around the core finding: VinBus improves mean SMCI, but population-weighted and built-cell audits reveal persistent fragmentation.

## 15. Reproducibility

Core commands:

```powershell
python scripts/build_accessibility_inputs.py --mode network --gtfs-status baseline_limited
python scripts/run_pilot_metrics.py
python scripts/compute_population_weighted_smci.py
python scripts/built_population_zero_access_audit.py
python scripts/rac_time_only_sensitivity.py
python scripts/motorcycle_speed_sensitivity.py
python scripts/transit_impedance_sensitivity.py
python scripts/rac_scaling_sensitivity.py
python scripts/make_validation_report.py
python scripts/make_supervisor_memo.py
python scripts/make_pilot_maps.py
pytest tests/ -q
```

Current test baseline: 70 tests pass.

## 16. Ethics and Data Statement

The study uses open geospatial data, public transport feeds, and manually collected route-time checks from a consumer mapping application. It does not collect personal traces, survey responses, or identifiable human-subject data.

VinBus does not publish official GTFS. The pseudo-GTFS is derived from publicly accessible web-app API responses; no private user data, authentication bypass, or personal data are used. Licensing and terms-of-service uncertainty remain, so the derived route tables should be used for academic reproducibility only and replaced by official GTFS if one becomes available. OSM VinBus route relations remain a non-API sensitivity source.

All data limitations are reported explicitly, including OSM and Overture completeness, GTFS vintage, VinBus pseudo-GTFS construction, motorcycle validation scale, and proxy-based MAI construction.

## 17. AI Use Statement

AI assistance was used to audit methodology consistency, update proposal wording, and structure documentation. The research design, data decisions, interpretation, and final responsibility remain with the author.

# Fragmented Mobility Capability in Motorcycle-Dependent Green Megaprojects

## A Dual-Scale and Mode-Competitive Accessibility Framework from Vinhomes Ocean Park, Hanoi

Working proposal v8 draft. Last updated: 2026-06-29.

## 1. Summary

This study examines whether a green-branded megaproject can produce sustainable mobility capability when residents still live in a motorcycle-dominant metropolitan travel environment. The empirical case is Vinhomes Ocean Park in Gia Lam, Hanoi, where local amenities, electric-bus branding, and planned urban form coexist with the continued practical advantage of motorcycles.

The proposal develops a dual-scale and mode-competitive accessibility framework. It separates neighborhood walking access from metropolitan opportunity access, then evaluates whether walking and transit are competitive with motorcycle access. The central metric is the Sustainable Mobility Capability Index (SMCI), defined as the joint presence of local access, metropolitan access, and relative competitiveness against motorcycles.

The current implementation is a pilot, not a full final study. It covers 462 grid cells around Vinhomes Ocean Park and uses real OSM walking and driving networks, Hanoi GTFS as a pre-VinBus transit baseline, VinBus pseudo-GTFS for the intervention scenario, OSM plus Overture POIs, OSM landuse/office enrichment for economic opportunities, WorldPop, VIDA building footprints, and manual Android Google Maps motorcycle checks. The metropolitan opportunity index is now built on a strict source-backed observed-magnitude specification with full coverage of all included destinations. The pipeline runs end to end and passes 77 tests.

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

A methodological by-product is a documented, provenance-tracked hierarchy for assigning opportunity magnitudes from open and source-backed data, which addresses the common weakness of accessibility studies that treat every point of interest as one undifferentiated opportunity.

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
| Building footprints | Built-cell audit, population cross-check, observed magnitude derivation | 41,816 VIDA footprints fetched; 455/462 cells built |
| Hanoi GTFS | Network B baseline transit | 2018 World Bank feed; pre-VinBus baseline |
| VinBus pseudo-GTFS | Network C intervention | API-derived feed; 176 routes, 5,631 stops, observed headways 5-48 min |
| WorldPop 2020 | Population exposure check and supply-side weighting | Downloaded; about 92.77 m raster resolution |
| Android Google Maps checks | Motorcycle validation | 10 OD pairs manually measured |

The 2018 Hanoi GTFS is not treated as current service. It is used as a deliberate pre-VinBus conventional transit baseline because VinBus launched later. A post-2021 GTFS feed, if verified, should be used as a future sensitivity test rather than a replacement for the baseline logic.

The VinBus feed is a pseudo-GTFS representation built from the public VinBus web API. Because no official GTFS is published, this is reported as a transparent proxy. OSM VinBus relations are retained as a sensitivity source.

The POI layer is open-data based but now supports a strict source-backed observed-magnitude hierarchy. OSM and Overture improve coverage; OSM landuse/office enrichment reduces the earlier weak commercial-proxy problem; and a generic observed-magnitude schema (`obs_magnitude`, `obs_unit`, `obs_source_tier`, `obs_confidence`, `obs_audit_status`, `include_in_mai`, `exclusion_reason`) records a measured magnitude and its provenance for every metropolitan destination. The strict specification carries no tag-only proxy fallback for included MAI destinations: point-only service and transport listings without a measurable magnitude are explicitly excluded from MAI with audit reasons rather than assigned an arbitrary weight.

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

The Metropolitan Accessibility Index (MAI) measures walking-and-transit access to metropolitan opportunities. It is framed as Metropolitan Opportunity Accessibility. Under the strict primary specification, every included destination carries a source-backed observed magnitude; a destination that has no measurable magnitude is excluded from MAI rather than weighted by a tag-only proxy.

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

**Observed opportunity weights.** Each destination's weight comes from a measured magnitude, converted to a within-domain weight that is bounded so no single facility dominates its domain:

```text
healthcare:  weight = clip(beds / 50,        0.4, 30.0)
higher_ed:   weight = clip(enrollment / 1000, 0.5, 20.0)
economic:    weight = clip(jobs / 500,        0.1,  5.0)
commercial:  weight = clip(gla_m2 / 1000,     0.1, 25.0)
```

The reference denominators are set so that a typical mid-size facility receives a weight near 1.0. The economic reference of 500 jobs and cap of 5.0 are deliberate: they keep a typical small-and-medium enterprise cluster in the [0.1, 1.0] range and prevent a single large industrial park (tens of thousands of workers) from flooding the economic domain, a discipline carried over from earlier domain-domination corrections.

**Source provenance.** A magnitude is assigned through a strict hierarchy and tagged with its source tier:

| Source tier | Meaning | Pilot count (included) |
| --- | --- | ---: |
| `observed_point` | Named facility with a citable count | 2 |
| `official_source` | National standard applied by facility type (MOET class sizes, MOH commune-station beds) | 25 |
| `facility_source` | Facility-level website or report | 13 |
| `geometry_measured` | Floorspace measured from building footprint and levels | 80 |
| `manual_checked` | Sector-standard estimate, reviewed | 57 |
| `observed_dasymetric_weak` | Employment density disaggregated by area | 23 |

A supply-side population multiplier `m_j = clip(sqrt(pop_density_j / median), 0.5, 2.0)` further scales each opportunity by the residential density of the grid cell containing it, on the rationale that an opportunity in a denser catchment serves a larger market. The square root damps the signal and median-centering leaves a typical-density opportunity unchanged, so population refines magnitudes without letting any single domain dominate. The same effective weights enter the transit and motorcycle MAI so the RAC_opp ratio stays internally consistent. Integrating population into MAI changes results only marginally (no-population sensitivity gives Cohen's kappa = 0.976, with 8 of 462 cells relabelled).

**Coverage.** The strict observed-magnitude layer covers all included MAI destinations: healthcare 18/18, higher education 70/70, economic 32/32, and commercial/services 80/80; 8 point-only service/transport records are excluded from MAI with explicit audit reasons recorded in `data/interim/poi_observed_audit.csv`. Commercial/services no longer treats all destinations as retail floorspace: retail uses measured gross leasable area (`m2_gla`), park/leisure/agrarian polygons use measured service/leisure area, and non-measurable point listings are excluded rather than assigned artificial capacity.

**Provenance honesty.** Full coverage means every included destination has a source-backed magnitude, not that every value is an official facility census. Economic remains the weakest domain: 23 of its values are area-disaggregated employment-density estimates (`observed_dasymetric_weak`) and must be read as areal interpolation, not point truth. National-standard tiers (MOET class sizes, MOH commune-station beds) are citable but apply a class-of-facility figure rather than a school-by-school or clinic-by-clinic count. These tiers are flagged so that the final paper can upgrade them with named facility sources where possible.

**Sensitivity against the proxy baseline.** The pre-observed proxy specification (`--opportunity-basis proxy`) is retained as a regression baseline, and the strict specification is compared against it. Moving from proxy to strict observed magnitudes raises mean SMCI_B from 0.0435 to 0.0500, relabels 40 of 462 cells (Cohen's kappa = 0.876), and preserves the cell ranking almost exactly (Spearman rho = 0.991). Variance inflation rises modestly (VIF_MAI 8.96 to 10.23, VIF_RAC 8.85 to 11.12) because the richer healthcare and economic magnitudes increase the covariance between MAI and RAC; this is handled by the RAC_time-only contingency in Section 10.

### 8.3 Relative Accessibility Competitiveness

Relative Accessibility Competitiveness (RAC) asks whether walking and transit can compete with motorcycles.

```text
RAC_time_raw_i = motorcycle_travel_time_i / walk_transit_travel_time_i
RAC_opp_raw_i  = MAI_transit_i / MAI_motorcycle_i
```

`RAC_time_raw_i` is operationalized as motorcycle opportunity-weighted mean travel time divided by walk-transit opportunity-weighted mean travel time. It uses the same metropolitan opportunity set, domain weights, opportunity weights, and 60-minute cutoff as MAI. Cells with no reachable weighted destination receive the cutoff. Network B uses the 2018 GTFS stop-proximity timing proxy; Network C uses pseudo-GTFS stop routing with access, wait, line-haul, and egress components. The input table reports `moto_mean_opp_time_min`, `wt_A_mean_opp_time_min`, and `wt_B_mean_opp_time_min` for auditability.

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

First, POI validation combines a manual OSM spot check and an Overture gate. The OSM spot check reviewed 20 records: 14 confirmed, 2 duplicates, 2 misclassified, and 2 missing/unverified. The Overture-only gate passed with 55/55 confirmed before promotion to the merged layer. The strict observed-magnitude layer adds a third audit artifact, `data/interim/poi_observed_audit.csv`, which records the source tier, confidence, and inclusion decision for every metropolitan destination.

Second, motorcycle routing is checked against 10 Android Google Maps motorcycle OD pairs. The current mean absolute error is about 1.90 minutes, with model bias about -1.04 minutes.

Third, multicollinearity is reported because MAI and RAC_opp share the MAI_transit component. In the strict observed specification, VIF is high in the primary full-RAC formula:

| Variable | VIF | Status |
| --- | ---: | --- |
| NAI | 2.42 | OK |
| MAI | 10.23 | High |
| RAC | 11.12 | High |

The RAC_time-only contingency reduces collinearity below the conventional threshold:

| Variable | VIF | Status |
| --- | ---: | --- |
| NAI | 2.26 | OK |
| MAI | 2.93 | OK |
| RAC_time | 2.02 | OK |

Primary versus RAC_time-only typology agreement is strong: Cohen's kappa = 0.9125, Spearman rho(SMCI rank) = 0.9889, and 28/462 cells change label. The primary full-RAC specification is retained, with RAC_time-only reported as robustness.

Fourth, SMCI robustness uses an additive alternative:

```text
SMCI_additive_i = (NAI_norm_i + MAI_norm_i + RAC_norm_i) / 3
```

This is meaningful because it allows compensation across dimensions. A geometric mean alternative is not used because it is only a monotonic transformation of the multiplicative product.

Fifth, built-cell and population audits check whether zero-access results are open-space artifacts. VIDA building footprints are present in 455/462 cells, and many zero-access cells are built and populated. Zero inflation is therefore interpreted cautiously rather than dismissed.

## 11. Current Pilot Results

The current pilot results, under the strict observed-magnitude specification, are:

| Metric | Value |
| --- | ---: |
| Grid cells | 462 |
| Mean SMCI_A | 0.0357 |
| Mean SMCI_B | 0.0500 |
| Mean Delta SMCI | 0.0143 |
| Improved cells | 286 / 462 (61.90%) |
| Unchanged cells | 88 / 462 (19.05%) |
| Declined cells | 88 / 462 (19.05%) |
| Motorcycle validation MAE | 1.90 min |

The pilot results should be interpreted through distributional and spatial diagnostics rather than the global mean alone. Mean SMCI rises from 0.0357 in Scenario A to 0.0500 in Scenario B, but this average is affected by zero-inflation in the weakest-link index. In the walking-access layer, 88 of 462 cells (19.0%) have zero NAI; the same 88 cells also have zero SMCI_B because any zero component collapses the multiplicative index. Cross-checking these zero-access cells against VIDA building footprints shows that the large majority are built cells, so zero accessibility is not simply a lake, park, or open-space artifact.

The VinBus scenario improves SMCI in 286 of 462 cells (61.9%), while 88 cells (19.0%) remain unchanged and 88 cells (19.0%) decline slightly under the opportunity-weighted time-competitiveness term. Among cells with positive SMCI, the median rises from 0.0251 in Scenario A to 0.0296 in Scenario B. This non-zero median comparison is more interpretable than the global mean for cells that have at least some sustainable mobility capability. The unchanged group remains analytically important: these cells identify locations where adding metropolitan transit access does not overcome missing neighborhood walking access or weak local opportunity structure.

Scenario B typology counts are:

| Typology | Count |
| --- | ---: |
| Integrated Capability | 169 |
| Fragmented Capability | 62 |
| Transit-Dependent | 62 |
| Motorcycle Lock-in | 169 |

The equal high/low structure is expected under a rank-median typology and should not be interpreted as a discovered natural cluster distribution. The substantive interpretation depends on where those cells are located and how stable they are under robustness checks.

The population-weighted cross-check remains a useful caution. Total estimated population is about 78,816. Population shares by typology are: Integrated Capability 33.0%, Fragmented Capability 17.7%, Transit-Dependent 14.9%, and Motorcycle Lock-in 34.4%. The largest single population share is in Motorcycle Lock-in, which reinforces the core argument that aggregate improvement coexists with persistent fragmentation.

The built/population zero-access audit adds a second caution. The built zero-NAI cells contain about 12,267 residents, or 15.6% of the pilot population. Zero accessibility is therefore not only a lake/park/open-space issue; it is a substantive access and mapping uncertainty issue that should be reported separately from low-but-positive accessibility.

## 12. Expected Argument

The expected argument is not simply that VinBus improves accessibility. The stronger contribution is that improvement can coexist with persistent fragmentation.

Ocean Park may show high local amenity access in some cells, and VinBus may improve transit-based metropolitan access, but motorcycle competitiveness can still dominate in many locations. The key empirical question is whether cells move into Integrated Capability or remain in Fragmented Capability and Motorcycle Lock-in.

The pilot already suggests this mixed pattern: mean SMCI improves and 61.9% of cells improve, but 19.0% remain unchanged, 19.0% decline slightly under the time-competitiveness term, and Motorcycle Lock-in contains the largest population share.

## 13. Limitations

This is a single-site study. It supports theory-building and methodological contribution, not national generalization.

Network B uses a 2018 GTFS feed as a pre-VinBus baseline. This is methodologically deliberate but not equivalent to current conventional transit service.

Network C uses a pseudo-GTFS built from VinBus public API data, not an official GTFS feed. It is more detailed than a corridor proxy, but still not a full validated timetable product.

MAI is fully source-backed for included pilot destinations under the strict specification, but full coverage is not the same as a complete official facility census. Economic employment is the weakest domain because 23 of its values rely on sector-density or dasymetric estimates labelled `observed_dasymetric_weak`; national-standard tiers for schools and commune health stations are citable but apply class-of-facility figures. These should be upgraded with named firm/facility sources before submission.

POI completeness remains uncertain despite OSM checks, Overture gating, and economic enrichment.

Motorcycle validation uses 10 manual OD pairs. It is a useful plausibility check, not a full calibration dataset.

MAI/RAC collinearity is structurally high in the full-RAC specification. The RAC_time-only sensitivity reduces VIF and shows high typology agreement, so the issue is reported rather than hidden.

Mode and impedance specifications omit fares, parking, explicit transfer penalties, access/egress discomfort, and schedule unreliability. Transit-impedance sensitivity now partially bounds this by testing conservative and pessimistic wait/access/egress/reliability penalties; it is not a replacement for observed mode-choice data.

Motorcycle speed sensitivity tests slow-congestion and fast-lane-splitting scenarios. Typology is stable (kappa = 0.994; 2 cells relabelled), but the paper should still frame this as a bounded robustness check rather than full behavioral validation.

## 14. Work Plan

Immediate next steps:

1. Keep the 208-POI enriched layer with the strict observed-magnitude specification as the current primary input, and preserve OSM-only / Overture-only / economic-enrichment / observed-audit trails.
2. Refresh all validation outputs after each pipeline run so proposal numbers, supervisor memo, and self-audit remain synchronized.
3. Use maps and spatial narratives to interpret where Integrated Capability, Fragmented Capability, Transit-Dependent, and Motorcycle Lock-in cells occur.
4. Treat TUMI or other post-2021 Hanoi GTFS candidates only as current-service sensitivity after license and service-date checks.
5. Upgrade the weakest observed tiers — `observed_dasymetric_weak` employment and national-standard school/clinic figures — with named facility sources (firm employment, school enrollment, private clinic capacity), then rerun the strict observed-vs-proxy sensitivity.
6. Prepare the supervisor package around the core finding: VinBus improves mean SMCI, but population-weighted and built-cell audits reveal persistent fragmentation.

## 15. Reproducibility

Core commands:

```powershell
python scripts/derive_all_observed.py
python scripts/build_accessibility_inputs.py --mode network --gtfs-status baseline_limited --pois data/interim/merged_pois_observed.gpkg --opportunity-basis observed_strict
python scripts/run_pilot_metrics.py
python scripts/observed_vs_proxy_sensitivity.py
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

Current test baseline: 77 tests pass.

## 16. Ethics and Data Statement

The study uses open geospatial data, public transport feeds, and manually collected route-time checks from a consumer mapping application. It does not collect personal traces, survey responses, or identifiable human-subject data.

VinBus does not publish official GTFS. The pseudo-GTFS is derived from publicly accessible web-app API responses; no private user data, authentication bypass, or personal data are used. Licensing and terms-of-service uncertainty remain, so the derived route tables should be used for academic reproducibility only and replaced by official GTFS if one becomes available. OSM VinBus route relations remain a non-API sensitivity source.

All data limitations are reported explicitly, including OSM and Overture completeness, GTFS vintage, VinBus pseudo-GTFS construction, motorcycle validation scale, strict observed MAI provenance and source tiers, weak derived estimates, and explicit MAI exclusions.

## 17. AI Use Statement

AI assistance was used to audit methodology consistency, update proposal wording, and structure documentation. The research design, data decisions, interpretation, and final responsibility remain with the author.

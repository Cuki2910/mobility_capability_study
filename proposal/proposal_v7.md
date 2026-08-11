# Fragmented Mobility Capability in Motorcycle-Dependent Green Megaprojects

## A Dual-Scale and Mode-Competitive Accessibility Framework from Vinhomes Ocean Park, Hanoi

Proposal v7. Last updated: 2026-07-27.

## 1. Summary

This study examines whether a green-branded megaproject can produce sustainable mobility capability when residents still live in a motorcycle-dominant metropolitan travel environment. The empirical case is Vinhomes Ocean Park in Gia Lam, Hanoi, where local amenities, electric-bus branding, TOD-like transit promises, and planned urban form coexist with the continued practical advantage of motorcycles (Calthorpe, 1993; Cervero & Kockelman, 1997; Shatkin, 2008; Caprotti, 2014; Cugurullo, 2016).

The proposal develops a dual-scale and mode-competitive accessibility framework. It separates neighborhood walking access from metropolitan opportunity access, then evaluates whether walking and transit are competitive with motorcycle access. The central metric is the Sustainable Mobility Capability Index (SMCI), defined as the joint presence of local access, metropolitan access, and relative competitiveness against motorcycles.

The current implementation is a pilot, not a full final study. It covers 462 grid cells around Vinhomes Ocean Park and uses real OSM walking and driving networks, Hanoi GTFS as a pre-VinBus transit baseline, VinBus pseudo-GTFS for the intervention scenario, OSM plus Overture POIs, OSM landuse/office enrichment for economic opportunities, WorldPop, VIDA building footprints, and manual Android Google Maps motorcycle checks. The metropolitan opportunity index is now built on a strict provenance-tiered opportunity specification with full coverage of all included destinations. The pipeline runs end to end and passes 80 tests.

## 2. Research Problem

Green megaprojects and "mega green city" developments are often evaluated through internal amenities, environmental branding, TOD-style planning language, and transit provision (Calthorpe, 1993; Cervero & Kockelman, 1997; Joss et al., 2011; Caprotti, 2015). These indicators are necessary but incomplete in a city such as Hanoi, where motorcycles remain fast, flexible, affordable, and embedded in everyday travel.

The key problem is fragmentation. A neighborhood may provide nearby schools, parks, shops, and services, yet residents may still need motorcycles to reach jobs, higher education, hospitals, or wider metropolitan opportunities. In that case, local completeness does not become sustainable mobility capability. This study treats that mismatch as fragmented mobility capability.

The paper therefore treats TOD and green-megaproject claims as hypotheses to be tested, not as proof of sustainable mobility. This follows critiques of eco-city and megaproject urbanism that distinguish planning claims from social and mobility outcomes (Shatkin, 2008; Caprotti, 2014, 2015; Cugurullo, 2016). A project can look transit-oriented or green at the master-plan scale while still failing residents if walking and transit do not provide competitive access to metropolitan opportunities.

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

Fourth, it offers a way to audit TOD-adjacent and green-megaproject claims through accessibility outcomes rather than through design labels alone: local completeness, metropolitan reach, and mode competitiveness must all appear together before a place is called integrated (Cervero & Kockelman, 1997; Shatkin, 2008; Joss et al., 2011).

A methodological by-product is a documented, provenance-tracked hierarchy for assigning opportunity magnitudes from open and source-backed data, which addresses the common weakness of accessibility studies that treat every point of interest as one undifferentiated opportunity.

## 5. Study Area

The study area is Vinhomes Ocean Park and its surrounding Gia Lam context in Hanoi. The site is suitable because it combines planned green-urban branding, internal amenities, VinBus services, TOD-like accessibility expectations, and exposure to Hanoi's motorcycle-oriented regional mobility system.

The analysis uses a 250 m grid. This scale follows grid-based urban accessibility precedent such as Albacete et al. (2017), who used 250 x 250 m cells to compare public-transport accessibility methods in Helsinki. For this study, 250 m is fine enough to capture neighborhood-scale variation inside and around Ocean Park while keeping network routing feasible. The pilot contains 462 cells.

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

The POI layer is open-data based but now supports a strict provenance-tiered opportunity magnitude hierarchy. OSM and Overture improve coverage; OSM landuse/office enrichment reduces the earlier weak commercial-proxy problem; and a generic provenance-tiered magnitude schema (`obs_magnitude`, `obs_unit`, `obs_source_tier`, `obs_confidence`, `obs_audit_status`, `include_in_mai`, `exclusion_reason`) records a measured magnitude and its provenance for every metropolitan destination. The strict specification carries no tag-only proxy fallback for included MAI destinations: point-only service and transport listings without a measurable magnitude are explicitly excluded from MAI with audit reasons rather than assigned an arbitrary weight.

## 7. Network and Scenario Definitions

The framework uses four networks.

| Network | Definition | Role |
| --- | --- | --- |
| A | Walking | Local access and walk approach links |
| B | Walking + conventional transit | Scenario A baseline |
| C | Walking + conventional transit + VinBus | Scenario B network assumption |
| D | Motorcycle | Competitive benchmark |

Scenario A combines Networks A and B and represents the modeled conventional-transit reference. Scenario B combines Networks A and C and represents the VinBus network assumption. Network D is used in both scenarios to calculate motorcycle competitiveness.

Motorcycle travel time is not raw car-equivalent OSM driving time. The routing uses calibrated motorcycle speed assumptions, then checks plausibility against manual Android Google Maps motorcycle-mode measurements.

## 8. Index Construction

### 8.1 Neighborhood Accessibility Index

The Neighborhood Accessibility Index (NAI) measures local walking access to daily opportunities:

```text
NAI_i = count of qualifying POIs reachable by walking within the neighborhood threshold
```

The pilot uses an 800 m walking-network threshold (about 10 minutes at 80 m/min) as the primary NAI catchment, and reports the 1200 m / 15-minute threshold as an optimistic upper-bound specification. This is an operational planning assumption rather than a locally validated behavioral cutoff: no identified Hanoi or Ho Chi Minh City study directly establishes 800 m as an empirically optimal walking distance. Hanoi evidence shows walking acceptability to transit depends on street conditions, safety, transit quality, and motorcycle competition rather than a fixed radius (Phuong et al. 2024; Hoang-Tung et al. 2021; Nguyen et al. 2020), while comparator evidence from motorcycle-taxi-dominant Bangkok finds typical station-access walking distances clustering around 428-500 m, with a sharp shift toward motorcycle-taxi use beyond 500 m (Pongprasert & Kubota 2017, 2019). Tropical heat and sun exposure add a measurable perceived walking cost even where shade is present (Melnikov et al. 2022; Jareemit & Srivanit 2022), reinforcing that a 15-minute network catchment is not equally comfortable in Hanoi as in European 15-minute-city applications. Rather than adopting either the stricter Bangkok-observed distances or a mechanical 15-minute-to-distance conversion, 800 m is retained as a transparent central operational value and tested against 600 m (conservative), 1000 m, and 1200 m (optimistic upper bound).

NAI remains count-based because the neighborhood question is whether daily functions are present within a walkable catchment. The 15-minute-city concept is used as a proximity and local-completeness framework, while the empirical cutoff is localized through sensitivity testing.

### 8.2 Metropolitan Accessibility Index

The Metropolitan Accessibility Index (MAI) measures walking-and-transit access to metropolitan opportunities. It is framed as Metropolitan Opportunity Accessibility. Under the strict primary specification, every included destination carries a source-backed provenance-tiered magnitude; a destination that has no measurable magnitude is excluded from MAI rather than weighted by a tag-only proxy.

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

**Empirical validation of prior weights.** The prior weights (0.40 / 0.20 / 0.20 / 0.20) were checked against trip-purpose data from the UTM-Hanoi dataset ($N = 26,106$ respondents; Kieu et al., 2024, doi:10.1038/s41597-024-02950-9). The raw distribution is work (58.0%), education (17.2%), visit (12.2%), shopping (7.4%), leisure (3.6%), and caring (1.7%). For a strict MAI-domain sensitivity, `scripts/derive_mai_weights_utm.py` maps work to `economic`, education to `higher_education`, shopping to `metro_commercial`, and caring to `tertiary_healthcare`; leisure and visit are excluded before renormalization because they do not map cleanly to the four metropolitan opportunity domains. This yields `utm_derived` weights of economic 0.6885, higher education 0.2043, tertiary healthcare 0.0198, and metro commercial 0.0874. The study deliberately retains the smoothed prior weights as the default because they represent normative accessibility needs across multiple daily functions rather than raw revealed demand, which is endogenous to Hanoi's existing employment concentration. The UTM-derived weights are therefore reported as sensitivity evidence, not promoted to the primary specification.

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
| `observed_point` | Named facility with a citable count | 3 |
| `official_source` | National standard applied by facility type (MOET class sizes, MOH commune-station beds) | 22 |
| `facility_source` | Facility-level website or report | 19 |
| `geometry_measured` | Floorspace measured from building footprint and levels | 81 |
| `manual_checked` | Sector-standard estimate, reviewed | 61 |
| `observed_dasymetric_weak` | Employment density disaggregated by area | 15 |

A supply-side population multiplier `m_j = clip(sqrt(pop_density_j / median), 0.5, 2.0)` further scales each opportunity by the residential density of the grid cell containing it, on the rationale that an opportunity in a denser catchment serves a larger market. The square root damps the signal and median-centering leaves a typical-density opportunity unchanged, so population refines magnitudes without letting any single domain dominate. The same effective weights enter the transit and motorcycle MAI so the RAC_opp ratio stays internally consistent. Integrating population into MAI changes results only marginally (no-population sensitivity gives Cohen's kappa = 0.976, with 8 of 462 cells relabelled).

**Coverage.** The strict provenance-tiered opportunity layer covers all included MAI destinations: healthcare 18/18, higher education 70/70, economic 32/32, and commercial/services 81/81; 7 point-only service/transport records are excluded from MAI with explicit audit reasons recorded in `data/interim/poi_observed_audit.csv`. Commercial/services no longer treats all destinations as retail floorspace: retail uses measured gross leasable area (`m2_gla`), park/leisure/agrarian polygons use measured service/leisure area, and non-measurable point listings are excluded rather than assigned artificial capacity.

**Provenance honesty.** Full coverage means every included destination has a source-backed magnitude, not that every value is an official facility census. Economic is no longer purely dasymetric: it is anchored by key citable headcounts (e.g., Z176 Factory, Phú Thị Industrial Cluster, VinBus Depot). The remaining disaggregated values use a built-coverage coefficient of 0.35 on industrial landuse polygons (to reflect GFA rather than land area) and are capped at 5,000 jobs to eliminate extreme outliers. Only 15 values across the study area are area-disaggregated employment-density estimates (`observed_dasymetric_weak`) and must be read as areal interpolation, not point truth. National-standard tiers (MOET class sizes, MOH commune-station beds) are citable but apply a class-of-facility figure rather than a school-by-school or clinic-by-clinic count. These tiers are flagged so that the final paper can upgrade them with named facility sources where possible.

**Sensitivity against the proxy baseline.** The pre-observed proxy specification (`--opportunity-basis proxy`) is retained as a regression baseline, and the strict specification is compared against it. Under the promoted RAC_time primary specification and 800 m NAI primary threshold, moving from proxy to strict provenance-tiered magnitudes changes mean geometric-mean SMCI_B from 0.1658 to 0.1711, relabels 20 of 462 cells (Cohen's kappa = 0.9373), and preserves the cell ranking almost exactly (Spearman rho = 0.9965). Variance inflation remains well below the conventional threshold (strict provenance-tiered VIF_MAI = 2.93, VIF_RAC = 2.05).

### 8.3 Relative Accessibility Competitiveness

Relative Accessibility Competitiveness (RAC) asks whether walking and transit can compete with motorcycles.

```text
RAC_time_raw_i = motorcycle_travel_time_i / walk_transit_travel_time_i
RAC_opp_raw_i  = MAI_transit_i / MAI_motorcycle_i
```

`RAC_time_raw_i` is operationalized as motorcycle opportunity-weighted mean travel time divided by walk-transit opportunity-weighted mean travel time. It uses the same metropolitan opportunity set, domain weights, opportunity weights, and 60-minute cutoff as MAI. Cells with no reachable weighted destination receive the cutoff. Network B uses the 2018 GTFS stop-proximity timing proxy; Network C uses pseudo-GTFS stop routing with access, wait, line-haul, and egress components. The input table reports `moto_mean_opp_time_min`, `wt_A_mean_opp_time_min`, and `wt_B_mean_opp_time_min` for auditability.

Both `MAI_transit` and `MAI_motorcycle` use the same opportunity domains, weights, and decay function. The opportunity ratio is retained as a diagnostic:

```text
RAC_opp_raw_i = MAI_transit_i / MAI_motorcycle_i
```

The primary RAC specification uses `RAC_time` only:

```text
RAC_i = RAC_time_i
```

This reviewer-safe specification is promoted because the previous full-RAC composite, `sqrt(RAC_time_i * RAC_opp_i)`, structurally reintroduced MAI through `RAC_opp` and produced high MAI/RAC collinearity. The full-RAC composite is retained as a construct-rich robustness check rather than the primary SMCI input.

### 8.4 Sustainable Mobility Capability Index

The primary index is the equal-weight geometric mean:

```text
SMCI_i = (NAI_norm_i * MAI_norm_i * RAC_norm_i)^(1/3)
```

SMCI is a multiplicative, weak-link-sensitive composite on a 0-1 scale with zero annihilation. A cell needs local walking access, metropolitan opportunity access, and mode competitiveness at the same time; any zero normalized component sets the geometric mean to zero, while partial compensation remains possible among positive values. The legacy product is retained as an audit scale: it has identical ordinal ranking but stronger compression near zero, so product-versus-geometric-mean is not a robustness test.

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

First, POI validation combines a manual OSM spot check and an Overture gate. The OSM spot check reviewed 20 records: 14 confirmed, 2 duplicates, 2 misclassified, and 2 missing/unverified. The Overture-only gate passed with 55/55 confirmed before promotion to the merged layer. The strict provenance-tiered opportunity layer adds a third audit artifact, `data/interim/poi_observed_audit.csv`, which records the source tier, confidence, and inclusion decision for every metropolitan destination.

**Sub-area Data Parity.** Classifying the 201 included metropolitan opportunities spatially shows that data confidence is higher inside the planned megaproject (Vinhomes Ocean Park, n=60) than in the surrounding informal town (Trâu Quỳ, n=141). Inside Ocean Park, **73.4%** of opportunities have high or medium confidence (11.7% high, 61.7% geometry-measured), with only **26.7%** low confidence (25.0% manual, 1.7% dasymetric). Outside in the informal town, low-confidence estimates rise to **42.6%** (32.6% manual, 9.9% dasymetric, 0.1% observed point), and geometry-measured features drop to **31.2%**. This side-by-side discrepancy indicates that any future comparison of mobility capability across planned and unplanned forms must account for data coverage bias (spontaneous small facilities are harder to verify than planned facilities).

Second, motorcycle routing is checked against 10 Android Google Maps motorcycle OD pairs. The current mean absolute error is about 1.90 minutes, with model bias about -1.04 minutes.

Third, multicollinearity is reported because MAI and RAC_opp share the MAI_transit component. In the strict provenance-tiered specification, VIF is high in the legacy full-RAC formula:

| Variable | VIF | Status |
| --- | ---: | --- |
| NAI | 3.38 | OK |
| MAI | 9.58 | High |
| RAC | 9.56 | High |

The promoted RAC_time-only primary specification reduces collinearity below the conventional threshold:

| Variable | VIF | Status |
| --- | ---: | --- |
| NAI | 2.26 | OK |
| MAI | 2.93 | OK |
| RAC_time | 2.05 | OK |

Legacy full-RAC versus promoted RAC_time-only typology agreement is strong: Cohen's kappa = <!-- headline:/full_rac_agreement/kappa|.4f -->0.9065<!-- /headline -->, Spearman rho(SMCI rank) = 0.9878, and <!-- headline:/full_rac_agreement/cells_relabelled|int -->30<!-- /headline -->/462 cells change label. The promoted primary is RAC_time-only; full RAC is reported as robustness.

Fourth, SMCI robustness uses an additive alternative:

```text
SMCI_additive_i = (NAI_norm_i + MAI_norm_i + RAC_norm_i) / 3
```

This is meaningful because it allows compensation across dimensions. The geometric mean is the primary reporting scale; the product is retained only as a monotonic legacy audit, not as an independent robustness specification.

Fifth, built-cell and population audits check whether zero-access results are open-space artifacts. VIDA building footprints are present in 455/462 cells, and many zero-access cells are built and populated. Zero inflation is therefore interpreted cautiously rather than dismissed.

Sixth, the neighborhood walking threshold is treated as a substantive sensitivity rather than a fixed import from the 15-minute-city literature. The primary NAI catchment is 800 m (10-minute neighborhood), used as a transparent operational assumption rather than a locally validated behavioral cutoff (see Section 8.1); the threshold-response audit rebuilds NAI and downstream metrics under 600 m, 800 m, 1000 m, and 1200 m walking catchments. Zero-NAI cells fall from 133/462 at 600 m to 88/462 at the 800 m primary and 33/462 at the 1200 m optimistic upper bound, while mean geometric-mean SMCI_B rises from 0.1483 to 0.1711 to 0.2009. The direction of the VinBus improvement remains and the four-typology structure is near-invariant across the range, but the apparent level of neighborhood completeness is threshold-dependent; this is why the primary cutoff is reported as an operational central value bounded by an explicit 600-1200 m sensitivity range rather than a single validated standard.

Seventh, spatial structure is evaluated as an additive diagnostic, not as a replacement for the index. Global Moran's I uses 9,999 permutations, while Local Moran's I (LISA) applies a Benjamini-Hochberg correction across cells. Under Queen contiguity, Scenario B SMCI has strong positive global autocorrelation (I = 0.7496, permutation p = 0.0001), with 58 High-High and 111 Low-Low FDR-significant cells; the same high/low clustering pattern also appears under Rook and 8-nearest-neighbour sensitivity specifications. Delta_SMCI is likewise spatially clustered (I = 0.7104, p = 0.0001). These diagnostics identify concentration and boundary outliers; they do not establish that the planning boundary causes the pattern.

Eighth, a boundary-permeability audit separates topological evidence from causal interpretation. The walking graph contains 59 physical edge crossings of the 10.11 km Ocean Park boundary (5.84 crossings/km), while the motorcycle graph contains 31 (3.07 crossings/km). For paired cells within 250 m on opposite sides, all 39 modeled pairs are connected, but median network-to-Euclidean detours are 2.10 for walking and 2.36 for motorcycle. OSM access/barrier tags do not flag a restriction on these crossing edges; missing tags are not evidence of unrestricted real-world access. Approximate fixed-seed edge betweenness is consequently reported only as a structural routing diagnostic.

Ninth, WorldPop demand-side exposure is tested with a building-footprint-constrained, population-preserving dasymetric allocation. The allocation retains the study population (difference from the baseline aggregate is -0.0003 persons from floating-point precision) and leaves every core index and typology unchanged. Population-weighted geometric-mean SMCI_B changes from 0.173003 to 0.173331, while the Motorcycle Lock-in population share changes from 33.89% to 33.63%. Because VIDA footprints do not provide dwelling counts, floor area, height, or residential use, this is reported as a sensitivity result rather than building-level population truth.

## 11. Current Pilot Results

The current pilot results, under the strict provenance-tiered opportunity specification, are:

| Metric | Value |
| --- | --- |
| Grid cells | <!-- headline:/n_cells|int -->462<!-- /headline --> |
| Mean SMCI A | 0.1470 |
| Mean SMCI B | 0.1711 |
| Mean Delta_SMCI | +0.0242 |
| Improved cells | 281 / 462 (60.82%) |
| Unchanged cells | 88 / 462 (19.05%) |
| Declined cells | 93 / 462 (20.13%) |
| NAI walking threshold | 800 m (~10 min); 1200 m reported as optimistic upper bound |
| Motorcycle validation MAE | 1.90 min |

The pilot results should be interpreted through distributional and spatial diagnostics rather than the global mean alone. Mean SMCI is 0.1470 in Scenario A and 0.1711 in Scenario B under the promoted RAC_time specification and the 800 m NAI primary threshold. This geometric-mean reporting scale retains zero annihilation while reducing compression among positive cells. In the walking-access layer, 88 of 462 cells (19.0%) have zero NAI and therefore zero SMCI_B, because any zero component collapses the geometric mean. Cross-checking these zero-access cells against VIDA building footprints shows that 84 are built cells housing about 11,798 residents (15.0% of pilot population), so zero accessibility is not simply a lake, park, or open-space artifact. At the 1200 m optimistic upper bound, zero-NAI cells fall to 33/462 (7.1%).

The VinBus network assumption yields higher SMCI in 281 of 462 cells (60.8%), while 88 cells (19.0%) remain unchanged and 93 cells (20.1%) have slightly lower modeled values under the opportunity-weighted time-competitiveness term. Among cells with positive SMCI, the median is 0.1726 in Scenario A and 0.2007 in Scenario B. This non-zero median comparison is more interpretable than the global mean for cells where all three measured components are positive. The unchanged group remains analytically important: these cells identify locations where adding metropolitan transit access does not overcome missing neighborhood walking access or weak local opportunity structure.

### Scenario B typology

| Type | Cells |
|---|---:|
| Integrated Capability | 171 |
| Fragmented Capability | <!-- headline:/typology_B/Fragmented Capability|int -->60<!-- /headline --> |
| Transit-Dependent | 60 |
| Motorcycle Lock-in | <!-- headline:/typology_B/Motorcycle Lock-in|int -->171<!-- /headline --> |

The equal high/low structure is expected under a rank-median typology and should not be interpreted as a discovered natural cluster distribution. The substantive interpretation depends on where those cells are located and how stable they are under robustness checks.

The population-weighted cross-check remains a useful caution. Total estimated population is about 78,816. Population shares by typology are: Integrated Capability 34.7%, Fragmented Capability 16.0%, Transit-Dependent 15.4%, and Motorcycle Lock-in 33.9%. Integrated Capability and Motorcycle Lock-in contain similarly large population shares, reinforcing the core argument that aggregate improvement coexists with persistent fragmentation.

The built/population zero-access audit adds a second caution. At the 800 m NAI primary, the built zero-NAI cells contain about 11,798 residents, or 15.0% of the pilot population. Zero accessibility is therefore not only a lake/park/open-space issue; it is a substantive access and mapping uncertainty issue that should be reported separately from low-but-positive accessibility.

The NAI threshold-response audit adds a third caution. At 600 m, zero-NAI cells are 133/462 (28.8%) and mean geometric-mean SMCI_B is 0.1483; at the 800 m primary, zero-NAI cells are 88/462 (19.0%) and mean geometric-mean SMCI_B is 0.1711; at 1000 m, zero-NAI cells are 58/462 (12.6%) and mean geometric-mean SMCI_B is 0.1860; at the 1200 m optimistic upper bound, zero-NAI cells are 33/462 (7.1%) and mean geometric-mean SMCI_B is 0.2009. The headline improvement is robust in direction and the four-typology structure is near-invariant, but 1200 m clearly gives the most generous reading of local walkability, which is why 800 m is the primary.

## 12. Expected Argument

The expected argument is not simply that VinBus improves accessibility, nor that Ocean Park is a success or failure. The stronger contribution is scalar: project-level accessibility and metropolitan sustainable mobility capability are different achievements.

The planned Ocean Park core appears to perform strongly. Using the Ocean Park 1 boundary, cells with more than 50% overlap with the project core are 69/70 Integrated Capability, and cells with more than 75% overlap are 63/63 Integrated Capability. This should be read as evidence of internal project success, not project failure.

The critical insight is that this internal strength is spatially bounded. Across the wider Ocean Park-plus-context surface, Scenario B still contains 170 Motorcycle Lock-in cells and 61 Fragmented Capability cells. A dedicated boundary-discontinuity output should quantify the inside/outside gradient around the project edge. The expected result is not simply a weak or strong project, but a capability discontinuity: Ocean Park can function as a green mobility enclave rather than automatically producing urban-scale sustainable mobility.

The spatial diagnostics reinforce, but do not overstate, this interpretation. FDR-corrected LISA finds robust high-high and low-low SMCI concentration, and the descriptive boundary audit finds a near-boundary inside-outside difference. The permeability audit shows that modeled cross-boundary connectivity exists but can involve substantial detours. Together, these results distinguish a spatially bounded capability pattern from a claim that gates or the project boundary alone cause it.

The policy question is consequently not whether the developer supplied internal amenities. From a developer KPI, the planned core performs well. From a public authority and transport-geography perspective, the question is whether a green megaproject's mobility benefits cross its boundary and integrate with the wider city. If sustainable mobility capability stops at the project edge, the outcome is enclave accessibility, not metropolitan sustainability.

## 13. Limitations

This is a single-site study. It supports theory-building and methodological contribution, not national generalization.

The primary NAI threshold is 800 m (10-minute pedestrian shed), used as a transparent operational assumption; no Hanoi or Ho Chi Minh City study identified in the literature review independently validates 800 m as the empirically optimal local cutoff, and comparator Bangkok evidence suggests typical walking access may be shorter (see Section 8.1). The 1200 m / 15-minute threshold is reported as an optimistic upper-bound sensitivity. The threshold-response audit (600/800/1000/1200 m) shows the four-typology structure is near-invariant across the range while absolute SMCI and zero-NAI share are threshold-sensitive, so results are reported against 800 m with 1200 m as the generous bound.

Network B uses a 2018 GTFS feed as a pre-VinBus baseline. This is methodologically deliberate but not equivalent to current conventional transit service.

Network C uses a pseudo-GTFS built from VinBus public API data, not an official GTFS feed. It is more detailed than a corridor proxy, but still not a full validated timetable product.

MAI is fully source-backed for included pilot destinations under the strict specification, but full coverage is not the same as a complete official facility census. The economic domain is anchored by key citable headcounts (e.g., Z176 Factory, Phú Thị Industrial Cluster), while remaining disaggregated values use a built-coverage coefficient (0.35) and a 5,000 jobs cap to prevent extreme outliers; national-standard tiers for schools and commune health stations are citable but apply class-of-facility figures. Only 15 POIs rely on area-density estimates labeled `observed_dasymetric_weak`, a major improvement over the earlier 100% dasymetric economic domain.

POI completeness remains uncertain despite OSM checks, Overture gating, and economic enrichment.

Motorcycle validation uses 10 manual OD pairs. It is a useful plausibility check, not a full calibration dataset.

Spatial autocorrelation is expected where nearby cells share overlapping walking catchments, destinations, and network paths. LISA therefore supports a claim about spatial concentration, not independent-cell inference or a causal boundary effect. The OSM network has incomplete access and barrier tagging, so crossing counts and detours are modeled topology rather than a field audit of every gate or sidewalk.

The dasymetric exposure sensitivity preserves WorldPop population at the study scale, but its building-footprint weights cannot distinguish residents from commercial uses or infer high-rise occupancy. It must not be interpreted as a building-level population estimate.

MAI/RAC collinearity is structurally high in the legacy full-RAC specification. The promoted RAC_time-only primary reduces VIF below 5 and keeps high agreement with the full-RAC typology, so the issue is handled directly rather than hidden.

Mode and impedance specifications omit fares, parking, explicit transfer penalties, access/egress discomfort, and schedule unreliability. Transit-impedance sensitivity now partially bounds this by testing conservative and pessimistic wait/access/egress/reliability penalties; it is not a replacement for observed mode-choice data.

Motorcycle speed sensitivity reruns the primary strict-observed specification under global −20% and +20% speed factors. The baseline reproduces mean SMCI_B = 0.01329 and 281/462 (60.8%) cells with higher modeled values; both scaled scenarios retain identical typology labels (kappa = 1.000; 0 cells relabelled). This remains a bounded robustness check rather than behavioral validation.

## 14. Work Plan

Immediate next steps:

1. Keep the 208-POI enriched layer with the strict provenance-tiered opportunity specification as the current primary input, and preserve OSM-only / Overture-only / economic-enrichment / observed-audit trails.
2. Refresh all validation outputs after each pipeline run so proposal numbers, supervisor memo, and self-audit remain synchronized.
3. Use maps and spatial narratives to interpret where Integrated Capability, Fragmented Capability, Transit-Dependent, and Motorcycle Lock-in cells occur.
4. Treat TUMI or other post-2021 Hanoi GTFS candidates only as current-service sensitivity after license and service-date checks.
5. Continue upgrading the remaining weak provenance-tiered levels — `observed_dasymetric_weak` employment and national-standard school/clinic figures — with named facility sources as they become available.
6. Prepare the supervisor package around the core finding: VinBus improves mean SMCI, but population-weighted and built-cell audits reveal persistent fragmentation.
7. Primary NAI cutoff selected at 800 m (10-minute pedestrian shed) from the 600/800/1000/1200 m threshold-response audit (Decisions #26/#27); 1200 m retained as optimistic upper-bound sensitivity. Proposal numbers synchronized to the 800 m primary.
8. Extend the matched comparison design with measurable policy levers: bus stops/km2, bus route-km/km2, POI density/mix, green/shade indicators, and street-structure indicators.

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

Current test baseline: 80 tests pass.

## 16. Ethics and Data Statement

The study uses open geospatial data, public transport feeds, and manually collected route-time checks from a consumer mapping application. It does not collect personal traces, survey responses, or identifiable human-subject data.

VinBus does not publish official GTFS. The pseudo-GTFS is derived from publicly accessible web-app API responses; no private user data, authentication bypass, or personal data are used. Licensing and terms-of-service uncertainty remain, so the derived route tables should be used for academic reproducibility only and replaced by official GTFS if one becomes available. OSM VinBus route relations remain a non-API sensitivity source.

All data limitations are reported explicitly, including OSM and Overture completeness, GTFS vintage, VinBus pseudo-GTFS construction, motorcycle validation scale, strict observed MAI provenance and source tiers, weak derived estimates, and explicit MAI exclusions.

## 17. AI Use Statement

AI assistance was used to audit methodology consistency, update proposal wording, and structure documentation. The research design, data decisions, interpretation, and final responsibility remain with the author.

## 18. Selected TOD and Green-Megaproject References

Accessibility and grid methods:

- Albacete, X., Olaru, D., Paül, V., & Biermann, S. (2017). Measuring the accessibility of public transport: A critical comparison between methods in Helsinki. *Applied Spatial Analysis and Policy, 10*, 161-188. https://doi.org/10.1007/s12061-015-9177-8
- Bruno, M., Monteiro Melo, H. P., Campanelli, B., et al. (2024). A universal framework for inclusive 15-minute cities. *Nature Cities, 1*, 633-641. https://doi.org/10.1038/s44284-024-00119-4
- Logan, T. M., Hobbs, M. H., Conrow, L. C., Reid, N. L., Young, R. A., & Anderson, M. J. (2022). The x-minute city: Measuring the 10, 15, 20-minute city and an evaluation of its use for sustainable urban design. *Cities, 131*, 103924. https://doi.org/10.1016/j.cities.2022.103924
- Moreno, C., Allam, Z., Chabaud, D., Gall, C., & Pratlong, F. (2021). Introducing the 15-minute city: Sustainability, resilience and place identity in future post-pandemic cities. *Smart Cities, 4*(1), 93-111. https://doi.org/10.3390/smartcities4010006
- Tran, M. T., Chikaraishi, M., Pham, Q. H., Zhang, J., & Fujiwara, A. (2015). Effects of perceived neighborhood walkability on mode choice of short-distance trips in Hanoi city. *Journal of the Eastern Asia Society for Transportation Studies, 11*, 1328-1345. https://doi.org/10.11175/easts.11.1328

TOD framing:

- Calthorpe, P. (1993). *The next American metropolis: Ecology, community, and the American dream*. Princeton Architectural Press.
- Cervero, R., & Kockelman, K. (1997). Travel demand and the 3Ds: Density, diversity, and design. *Transportation Research Part D: Transport and Environment, 2*(3), 199-219. https://doi.org/10.1016/S1361-9209(97)00009-6

Green megaproject / eco-city framing:

- Shatkin, G. (2008). The city and the bottom line: Urban megaprojects and the privatization of planning in Southeast Asia. *Environment and Planning A, 40*(2), 383-401. https://doi.org/10.1068/a38439
- Joss, S., Tomozeiu, D., & Cowley, R. (2011). Eco-cities: The mainstreaming of urban sustainability - key characteristics and driving factors. *International Journal of Sustainable Development and Planning, 6*(3), 268-285. https://doi.org/10.2495/SDP-V6-N3-268-285
- Caprotti, F. (2014). Eco-urbanism and the eco-city, or, denying the right to the city? *Antipode, 46*(5), 1285-1303. https://doi.org/10.1111/anti.12087
- Caprotti, F. (2015). Eco for whom? Envisioning eco-urbanism in the Sino-Singapore Tianjin Eco-city, China. *International Journal of Urban and Regional Research, 39*(3), 495-517. https://doi.org/10.1111/1468-2427.12233
- Cugurullo, F. (2016). Urban eco-modernisation and the policy context of new eco-city projects: Where Masdar City fails and why. *Urban Studies, 53*(11), 2417-2433. https://doi.org/10.1177/0042098015588727

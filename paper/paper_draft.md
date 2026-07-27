# Fragmented Mobility Capability in a Motorcycle-Dependent Green Megaproject: A Dual-Scale, Mode-Competitive Accessibility Framework from Vinhomes Ocean Park, Hanoi

**Author:** Cuki2910
**Target journal:** *Journal of Transport Geography*
**Article type:** Methods development and pilot validation
**Draft date:** 2026-06-24 (updated: 2026-07-01 — 800 m NAI primary threshold, RAC_time primary, strict-observed MAI)

---

## Abstract

Green-branded megaprojects in Southeast Asia are increasingly promoted as sustainable alternatives to dispersed, motorcycle-dependent urban growth. Yet conventional accessibility metrics evaluate such projects either at the neighborhood scale (walkability, the "15-minute city") or at the metropolitan scale (cumulative-opportunity job access), and almost always benchmark public transport against the private car. In motorcycle-dependent cities, where the practical alternative to transit is the motorcycle rather than the car, both choices misrepresent the lived constraint on sustainable mobility. This paper develops and pilots a dual-scale, mode-competitive accessibility framework that separates neighborhood-scale walking access from metropolitan-scale walk-and-transit access, and introduces a Relative Accessibility Competitiveness (RAC) term that benchmarks walk-and-transit performance directly against motorcycle performance. The three components are combined into a multiplicative Sustainable Mobility Capability Index (SMCI) and a theory-first four-way spatial typology.

We pilot the framework on Vinhomes Ocean Park, Hanoi, a 250+ ha electric-bus-branded development, across 462 grid cells of 250 m. The analysis uses OpenStreetMap walking and driving networks, a merged 208-feature opportunity layer, a 2018 pre-VinBus GTFS baseline, VinBus pseudo-GTFS stop and headway data, VIDA building footprints, and WorldPop 2020 population. Motorcycle travel times use per-road-class speed assumptions informed by the Hanoi motorcycle-speed literature (Son et al., 2012) and validated against manual Google Maps measurements (mean absolute error 1.90 minutes); all road-class values are modeling assumptions rather than direct literature citations, as no verified per-class source was identified in citation audit. Using an operational 800 m (10-minute) walking catchment as the primary neighborhood threshold and a RAC_time primary specification, mean SMCI is 0.0070 under Scenario A and 0.0133 under the VinBus network assumption; 281 of 462 cells (60.8%) have higher modeled values, 88 are unchanged, and 93 have slightly lower values under the opportunity-weighted time-competitiveness term. However, 88 cells (19.0%) remain at zero walking access; 84 of these zero-access cells are built cells housing about 15.0% of pilot population. Among cells with positive SMCI, the median is 0.0051 under Scenario A and 0.0081 under Scenario B, showing that the modeled scenario difference is not confined to the mean. Findings are robust to motorcycle-speed sensitivity (kappa >= 0.987), transit-impedance sensitivity (kappa >= 0.895), and the legacy full-RAC specification as a multicollinearity robustness check (kappa = 0.907); the 1200 m / 15-minute catchment is reported as an optimistic upper-bound sensitivity. The pilot demonstrates that local walkability and competitive sustainable mobility are distinct capabilities, and that green mobility claims must be evaluated through both distributional improvement and persistent zero-access fragmentation.

**Keywords:** accessibility; mode competition; motorcycle dependence; sustainable mobility; green megaprojects; Hanoi; Vietnam

---

## 1. Introduction

Sustainable mobility is commonly equated with two things that are, in practice, distinct: living near everyday destinations, and being able to reach the wider city without a private vehicle. The first is the logic of walkability indices and the "15-minute city" (Moreno et al., 2021). The second is the logic of cumulative-opportunity accessibility, which counts the jobs or services reachable within a travel-time threshold (Handy & Niemeier, 1997; Geurs & van Wee, 2004). Both framings are valuable, but each, used alone, can mislead. A neighborhood may be highly walkable yet poorly connected to metropolitan opportunity; conversely, a cell with good metropolitan transit access may sit in a locally barren environment.

A second limitation applies to motorcycle-dependent cities. Car–transit comparison is a well-established framework for assessing relative modal performance (e.g., Liao et al., 2020), but the locally salient competing mode in Hanoi is often the motorcycle. In a large transport-policy survey, motorcycles account for just under 60% of respondents' primary trips and approximately 95% of sampled households in four central districts own at least one motorcycle; these sample-specific figures should not be read as a citywide all-trip share (Kieu et al., 2024). Motorcycle dependence is deeply embedded in household routines and policy perceptions (Kieu et al., 2023). A transit service that appears competitive against a car benchmark may therefore remain less competitive against modeled motorcycle access.

This matters for the evaluation of green megaprojects: large, master-planned, environmentally branded developments that are proliferating across Vietnam and the wider region (Shatkin, 2008; Joss et al., 2011; Caprotti, 2014, 2015; Cugurullo, 2016). Their sustainability claims rest partly on internal amenities and partly on new transit provision, such as the electric VinBus network at our study site. But if the relevant counterfactual is the motorcycle, then neither "amenities within walking distance" nor "a bus line exists" is sufficient evidence that the development produces sustainable mobility capability.

We ask: **Does a green-branded development produce sustainable mobility capability when everyday life remains organized around the motorcycle?** We answer by building a framework that measures neighborhood access and metropolitan access on separate scales, adds a mode-competition term benchmarked against the motorcycle, and combines these into a multiplicative, weak-link-sensitive index and an interpretable spatial typology. We then validate the framework with a pilot implementation at Vinhomes Ocean Park, Hanoi.

The contribution is methodological and empirical: a reproducible, place-based accessibility framework designed for external testing in motorcycle-dependent regions. The pilot is a feasibility and validation exercise, not a direct measure of individual capability, a behavioral mode-choice model, or a final citywide result.

---

## 2. Related Work and Contribution

### 2.1 Accessibility Across Spatial Scales

Accessibility describes the potential to reach valued destinations through the interaction of land use and transport. Since Hansen's (1959) formulation, cumulative-opportunity and gravity-based measures have operationalized this potential through explicit choices about destination quantity, travel impedance, mode, and spatial scale (Handy & Niemeier, 1997; Geurs & van Wee, 2004). These choices are substantive rather than merely technical: a measure can describe access to nearby daily functions, metropolitan employment and services, or the relative performance of competing modes, but no single operationalization necessarily captures all three.

Neighborhood-proximity research, including common implementations of the 15-minute-city concept, asks whether residents can reach a portfolio of everyday destinations within a short walk or cycle (Moreno et al., 2021). Recent x-minute-city work shows that results depend on the selected amenities, impedance threshold, aggregation statistic, and treatment of population groups; a favorable average can coexist with amenity-poor locations (Logan et al., 2022; Bruno et al., 2024). Such measures are valuable descriptions of local completeness, but they do not by themselves measure access to specialized metropolitan opportunities. Conversely, cumulative and gravity-based measures can be computed at fine spatial resolution and can reveal local inequalities, but metropolitan destination sets do not inherently represent pedestrian completeness around the origin.

The relevant distinction is therefore one of construct and scale, not a contest between superior and inferior metrics. This study retains a separate Neighborhood Accessibility Index (NAI) for walking access to everyday opportunities and a Metropolitan Accessibility Index (MAI) for time-decayed access to larger and more specialized opportunities. The separation makes visible cells that are locally complete but metropolitanly constrained, as well as cells with metropolitan reach but weak local walking access.

Hanoi already has an important metropolitan-accessibility precedent. Ha et al. (2011) compared job accessibility in Hanoi and the Randstad, calculating private- and public-transport accessibility using potential-accessibility measures adjusted for competition for jobs. Their study provides an earlier application of mode-specific metropolitan accessibility analysis to Hanoi. The present study does not claim to introduce accessibility analysis to the city; it extends the local literature by coupling a metropolitan measure with a distinct neighborhood axis and a motorcycle-referenced competitiveness term.

### 2.2 Accessibility, Capability, and Transport Exclusion

A capability perspective shifts attention from infrastructure provision to the substantive freedom to participate in valued activities. Transport research using the capabilities approach emphasizes that accessibility resources are converted into opportunities through personal, social, and environmental factors; identical place-based access does not imply identical capability for people with different income, disability, caregiving duties, schedules, safety constraints, or fare burdens (Bantis & Haworth, 2020; Vecchio & Martens, 2021). Individual capability and transport-related exclusion therefore cannot be inferred from a spatial surface alone.

This distinction constrains the interpretation of SMCI. The pilot measures place-based accessibility conditions that are relevant to sustainable mobility capability: nearby opportunities, metropolitan reach by walking and transit, and modeled competitiveness against motorcycle access. It does not observe individual conversion factors, activity schedules, affordability, preferences, or realized participation. "Capability" is retained as a theoretical orientation toward jointly necessary spatial conditions, not as a claim that the index directly measures each resident's freedom or predicts behavior. Population exposure is consequently reported as a separate distributional cross-check rather than treated as individual-level validation.

### 2.3 Motorcycle Dependence and Modal Competitiveness in Hanoi

Relative modal performance is an established accessibility question. Liao et al. (2020), for example, mapped disparities in travel time between cars and public transport across cities. Such comparisons show why absolute transit accessibility can be behaviorally incomplete: the same transit time may be relatively attractive where the competing mode is slow and unattractive where it is fast. Car-transit comparison is thus a recurring framework, although it is not the only benchmark used in accessibility research.

Hanoi requires a different comparator. A large transport-policy survey reports motorcycle use for just under 60% of respondents' primary trips and motorcycle ownership in approximately 95% of sampled households in four central districts; the sample and primary-trip denominator prevent treating either figure as a citywide all-trip mode share (Kieu et al., 2024). Research on Hanoi's proposed motorcycle restrictions further documents entrenched motorcycle dependence and heterogeneous public responses (Kieu et al., 2023). These findings support motorcycles as a practically relevant benchmark without relying on the misleading claim that they account for more than 80% of all Hanoi trips.

The Relative Accessibility Competitiveness (RAC) term adapts established relative modal comparison to this context. Its primary specification compares opportunity-weighted walk-transit and motorcycle travel times. RAC is not a discrete-choice model, does not estimate switching probability, and does not establish that a resident would abandon a motorcycle. It describes how the modeled sustainable-mode travel-time surface performs relative to the locally salient alternative. Motorcycle times use explicit scenario-assumed speeds informed by broad Hanoi GPS ranges, bounded through speed sensitivity, and checked against ten manual consumer-app observations; the study does not attribute any modeled speed difference to an independently verified lane-splitting mechanism.

Kaszczyszyn and Sypion-Dutkowska (2019) are relevant to methods for walking access to public-transport stops, not to car-transit or motorcycle-transit competitiveness, and are therefore not used as a precedent for RAC. The closest contribution is instead the contextual adaptation of relative modal accessibility to motorcycles and its integration with separate local and metropolitan measures.

### 2.4 New Urban Areas, Green Megaprojects, and Spatial Fragmentation

The study's site interpretation also draws on two related literatures. International critiques of eco-cities and green megaprojects distinguish environmental branding, planned form, and infrastructure provision from demonstrated social and mobility outcomes (Shatkin, 2008; Caprotti, 2014, 2015; Cugurullo, 2016). These works justify testing green claims rather than accepting them, but they provide conceptual transfer rather than direct evidence about Ocean Park.

Hanoi-specific research provides a closer basis. Labbé and Boudreau (2011) analyze how new urban areas at Hanoi's peri-urban interface produce fragmentation through locally situated institutions and development processes. Their later work also documents porosity and local integration experiments, cautioning against treating planned areas as uniformly sealed enclaves (Labbé & Boudreau, 2015). This tension is important: a sharp accessibility boundary may be consistent with enclave-like spatial organization, but it does not by itself prove institutional enclosure, failed diffusion, or a causal planning mechanism. Direct scholarship located on Vinhomes Ocean Park concerns land acquisition and livelihoods rather than accessibility, VinBus, or boundary morphology (Đào Đức Hiếu et al., 2024). The present boundary analysis is therefore a new site-specific accessibility description, not confirmation of an established Ocean Park enclave diagnosis.

### 2.5 Composite Design, Typology, and Open-Data Uncertainty

Composite indicators encode assumptions about substitution among dimensions. Linear aggregation permits direct compensation, while nonlinear aggregation generally penalizes imbalance more strongly; genuinely non-compensatory methods require more than simply multiplying normalized indicators (OECD/JRC, 2008; Munda & Nardo, 2009; Greco et al., 2019). SMCI is therefore described as a multiplicative, weak-link-sensitive composite with zero annihilation. A zero on any normalized component sets the product to zero, but among positive values a sufficiently high component can still partly offset a lower one. The additive alternative tests how strongly the results depend on this aggregation choice.

The four-way typology is likewise a theory-first construction rather than a discovered natural clustering. Rank-median splits operationalize the proposed local/metropolitan distinction and ensure representation of the four conceptual classes under ties. Approximate balance is a property of the classifier, not empirical evidence that Hanoi naturally contains four equally sized mobility regimes; interpretation depends on spatial location and robustness.

Open-data accessibility also depends on source fitness. POI datasets vary in completeness, semantics, geometry, and category consistency (Psyllidis et al., 2022). This study consequently preserves source agreement, magnitude provenance, exclusions, and sensitivity specifications. Transit evidence is also differentiated: the dated official Hanoi GTFS and API-derived VinBus pseudo-GTFS support reproducible modeled networks of unequal vintage and schedule quality, not a fully observed before-and-after panel.

### 2.6 Research Gap and Contribution

Within the reviewed literature, neighborhood proximity, metropolitan opportunity accessibility, relative modal travel time, composite indicators, and quadrant typologies are established approaches. We identified no prior study that jointly separates neighborhood and metropolitan accessibility, evaluates walking-and-transit performance relative to motorcycle accessibility, and applies the resulting framework to a boundary-sensitive analysis of a Hanoi new urban area. This is a search-qualified finding, not proof that no such work exists. The contribution is best characterized as an integrated methodological operationalization, a motorcycle-specific adaptation of modal competitiveness, a provenance-tracked implementation, and a novel case application—not a new general theory of accessibility.

| Literature stream | Dominant approach | Unresolved limitation | Response in this study |
|---|---|---|---|
| Neighborhood accessibility | Short-threshold proximity to daily functions | Does not by itself measure metropolitan reach | Separate NAI |
| Metropolitan accessibility | Cumulative or gravity-weighted opportunities | Does not inherently represent local pedestrian completeness | Separate MAI |
| Capability and exclusion | Individual resources, conversion factors, and functionings | Requires person-level data unavailable here | Capability-relevant place index with explicit limitation |
| Modal competitiveness | Public transport relative to cars | Comparator poorly matches motorcycle-dependent Hanoi | Motorcycle-referenced RAC_time |
| Hanoi accessibility | Public/private-transport job access | Limited integration with neighborhood completeness | Dual-scale framework |
| New urban areas | Institutional and socio-spatial fragmentation | Limited quantitative boundary-accessibility evidence | Boundary-sensitive spatial description |
| Composite indicators | Linear, geometric, or non-compensatory aggregation | Compensability often implicit | Product plus additive sensitivity |
| Open transport data | GTFS/network and POI accessibility | Unequal feed quality and destination completeness | Explicit dated/pseudo-feed and POI provenance |

---

## 3. Study Area

The case study is Vinhomes Ocean Park in Gia Lam district, on the eastern edge of Hanoi. Vinhomes reports the original development covers 420 ha (Vinhomes, n.d.), and the developer promotes it as a "green–clean–beautiful" living environment (Vinhomes, n.d.); this is developer marketing language, not a measured sustainability outcome. Official VinBus route listings identify several routes serving the site (VinBus, n.d.). The site is analytically useful because it combines this green branding and internal amenities with continued exposure to Hanoi's motorcycle-oriented travel environment.

The analysis uses a 250 m grid covering Ocean Park and an approximately 2 km buffer, yielding 462 grid cells. This resolution distinguishes intra-development variation while remaining computationally tractable for network-based routing. The pilot extent is deliberately bounded; citywide application is future work.

---

## 4. Data

All data are open or manually collected. Table 1 summarizes sources and status.

**Table 1. Data sources.**

| Source | Role | Status in pilot |
|---|---|---|
| OpenStreetMap walking network | Network A; NAI routing | 6,846 nodes / 20,024 edges |
| OpenStreetMap driving network | Network D motorcycle base | 1,401 nodes / 3,408 edges |
| OpenStreetMap + Overture Maps POIs plus economic enrichment | Neighborhood and metropolitan opportunities | Primary layer: 208 POIs/features after Overture promotion and OSM landuse/office enrichment |
| 2018 Hanoi GTFS (World Bank, CC-BY 4.0) | Network B pre-VinBus transit baseline | 224 routes; 7,670 stops; service dates 2018 |
| VinBus public route API | Network C VinBus stops and schedule | 176 routes; 5,631 stops; per-route observed headway 5-48 min; pseudo-GTFS layer |
| VIDA building footprints | Built-cell mask; population cross-check | 41,816 footprints at confidence >= 0.70 |
| WorldPop 2020 raster | Supply-side MAI weighting; population exposure cross-check | ~92.77 m resolution; adequate for 250 m grid |
| Manual Google Maps motorcycle checks | Network D validation | 10 named origin-destination pairs |
| Motorcycle speed calibration | Network D speeds | Son et al. (2012) Hanoi GPS study as broad bounds; all per-class values are scenario-calibrated modeling assumptions (Section 5.5) |

**Data provenance and caveats.**

The 2018 GTFS feed predates VinBus's initial internal-route operation at Ocean Park in April 2021 (Vingroup, 2021a) and its entry into Hanoi's public passenger network in December 2021 (Vingroup, 2021b); it is therefore used deliberately as the conventional-transit reference network (Network B), not as current service or an observed pre-intervention panel. Stop geometry is used for stop-level accessibility; timetable frequency is treated only as a relative-magnitude proxy. Maintained GTFS catalogs were checked, and no current-service Hanoi feed was identified for replacement.

VinBus (Network C) data are sourced from the publicly accessible VinBus route-query API. No official VinBus GTFS feed was identified in the official sources searched for this study; official GTFS availability could not be established one way or the other. We therefore constructed a pseudo-GTFS layer from the application's JSON endpoints. The complete Hanoi network was extracted: 176 routes, 5,631 unique stop nodes with official GPS coordinates, 19,625 ordered stop-sequence records across both travel directions, and per-route headway data for most routes. Network C is therefore a modeled stop-level VinBus routing scenario with observed route headways where available, not a fully scheduled transit assignment.

The opportunity layer merges OpenStreetMap and Overture Maps, then adds OSM landuse and office-tag enrichment for metropolitan opportunity domains. A source-agreement audit was applied: 55 Overture-only POIs were spot-checked and all 55 were confirmed, passing the promotion gate. Economic enrichment adds landuse=commercial/retail/industrial/office polygons, office tags, financial amenities, and marketplace features. The primary opportunity layer therefore contains 208 POIs/features across economic, higher-education, healthcare, and metropolitan commercial/service domains.

WorldPop is used in two distinct ways. First, it enters MAI as a supply-side opportunity multiplier: `m_j = clip(sqrt(pop_density_j / median), 0.5, 2.0)`, applied to all opportunity domains so that opportunities in denser catchments receive larger effective weights. Second, it is used as a post-hoc population-exposure cross-check at origin cells. These two uses are reported separately: the first affects MAI/SMCI, while the second evaluates who is exposed to each capability level. The strict primary MAI includes only destinations with source-backed magnitudes; a separate coverage-oriented sensitivity specification uses geometry-measured, observed-derived, dasymetric-standard, or area/tag proxy magnitudes with explicit provenance.

### 4.1 Data Ethics and Replicability

No official VinBus GTFS feed was identified in the official sources searched for this study. The pseudo-GTFS used here is derived from publicly accessible web-application API responses and contains route, stop, direction, and headway information. No private user data, authentication bypass, personal traces, or individual-level records are used.

Licensing and terms-of-service uncertainty nevertheless remain. The derived route tables should be treated as an academic reproducibility artifact and replaced by official VinBus GTFS if one becomes available. OSM VinBus route relations are retained as a non-API sensitivity source.

---

## 5. Methods

The framework is implemented in tested Python. Formulas are maintained in `src/accessibility.py`, with scenario comparison logic in `src/pilot.py`.

### 5.1 Networks and Scenarios

Four networks are defined:

- **Network A, walking:** access to nearby neighborhood opportunities on foot.
- **Network B, walking + existing transit:** 2018 pre-VinBus GTFS baseline.
- **Network C, walking + existing transit + VinBus:** stop-level VinBus routing using pseudo-GTFS route, stop, and headway data.
- **Network D, motorcycle:** OSM driving network calibrated to motorcycle speeds.

Two scenarios are compared. **Scenario A** uses Networks A + B (no VinBus). **Scenario B** uses Networks A + C (with VinBus). Network D is the competitiveness benchmark in both. The modeled scenario difference is Delta_SMCI = SMCI(B) - SMCI(A), computed on shared A+B normalization bounds so that the difference reflects scenario change rather than re-scaling artifacts. Because A and B are modeled counterfactuals rather than observed before-and-after panels, Delta_SMCI should be interpreted as the estimated accessibility difference under each network assumption, not as a causal intervention effect.

### 5.2 Neighborhood Accessibility Index (NAI)

NAI is a count of qualifying POIs reachable on the walking network within the neighborhood threshold:

```text
NAI_i = count of qualifying POIs reachable by walking from cell i within the neighborhood threshold
```

A simple count is used deliberately: at the neighborhood scale, the presence of a school, clinic, shop, or park is more behaviorally relevant than its precise capacity. NAI is min-max normalized to NAI_norm for index construction. The primary neighborhood threshold is an 800 m network walking distance (about 10 minutes at 80 m/min), used as a transparent operational assumption rather than a locally validated behavioral cutoff — no Hanoi or Ho Chi Minh City study identified in the literature independently establishes 800 m as empirically optimal (see DEC-029). A 1200 m / 15-minute catchment is reported as an optimistic upper-bound sensitivity, and a 600/800/1000/1200 m threshold-response audit shows the four-typology structure is near-invariant across the range while absolute SMCI levels and zero-access shares are threshold-sensitive.

### 5.3 Metropolitan Accessibility Index (MAI)

MAI is a composite Metropolitan Opportunity Accessibility score across four domains, by walking plus transit. It is framed as opportunity accessibility rather than employment accessibility. Destination magnitudes follow a strict provenance-tiered hierarchy (official citable > geometry-measured > observed-derived > dasymetric-standard > area-tag proxy); only magnitudes with source-backed provenance are included in the strict primary specification, and proxy-only destinations are excluded rather than imputed.

```text
MAI_i = 0.40*A_econ + 0.20*A_edu + 0.20*A_health + 0.20*A_commerce
```

For each domain k:

```text
A_{i,k} = sum_j( opportunity_weight_{j,k} * f(t_ij) )
```

with a thresholded linear time-decay function:

```text
f(t) = 1                 if t <= 30 min
     = (60 - t) / 30     if 30 < t <= 60 min
     = 0                 if t > 60 min
```

For the coverage-oriented sensitivity specification, each POI's base opportunity weight follows the documented hierarchy of official citable, geometry-measured, observed-derived, dasymetric-standard, and area/tag proxy magnitudes; the strict primary MAI excludes proxy-only destinations. Observed values are transformed within domain using capped reference scales so that a single large facility cannot dominate the composite. Each POI's opportunity weight is then multiplied by a bounded supply-side population factor derived from the residential density of its containing grid cell:

```text
m_j = clip( sqrt(pop_density_j / median(pop_density>0)), 0.5, 2.0 )
```

The same effective weights are used for transit and motorcycle MAI, so RAC_opp remains an internally consistent ratio. Sensitivity runs compare this primary specification with a no-population baseline.

In the current pilot, observed-derived commercial floorspace and one hospital bed count are populated: 31 commercial POIs receive `obs_retail_gla_m2` (~13,205 m2 total), and Bệnh viện Đa khoa Gia Lâm receives `obs_beds=288`. Source-backed magnitudes account for 34.9% of commercial-domain opportunity weight, 36.7% of healthcare-domain weight, and 15.1% of total opportunity weight in the coverage-oriented specification; these shares do not establish complete facility-census coverage. Enrollment and job magnitudes remain proxy-backed in the coverage-oriented sensitivity specification and are excluded from the strict primary MAI pending citable source rows.

### 5.4 Relative Accessibility Competitiveness (RAC)

RAC measures whether walking-and-transit access is competitive with motorcycle access. It has two subcomponents, a time ratio and an opportunity ratio:

```text
RAC_time_raw_i = motorcycle_travel_time_i / walk_transit_travel_time_i
RAC_opp_raw_i  = MAI_transit_i / MAI_motorcycle_i
```

`RAC_time_raw_i` is computed as the motorcycle opportunity-weighted mean travel time divided by the walk-and-transit opportunity-weighted mean travel time. The destination set, domain weights, POI opportunity weights, and 60-minute cutoff are identical to the MAI calculation. Origins with no reachable weighted destination receive the 60-minute cutoff. For Network B, timing uses the 2018 GTFS stop-proximity proxy; for Network C, timing uses pseudo-GTFS stop routing with access walk, wait, line-haul, and egress components. The pipeline writes `moto_mean_opp_time_min`, `wt_A_mean_opp_time_min`, and `wt_B_mean_opp_time_min` for auditability.

`MAI_transit_i` is the composite metropolitan opportunity score by walk-and-transit; `MAI_motorcycle_i` is the same composite computed over the motorcycle network, using identical domain weights and decay. Their ratio is retained as `RAC_opp`, a diagnostic and legacy robustness component rather than an input to the primary RAC.

The primary specification uses the shared-scale normalized opportunity-weighted travel-time ratio only:

```text
RAC_i = RAC_time_i
```

The legacy full-RAC composite is retained for robustness:

```text
RAC_full_i = sqrt(RAC_time_i * RAC_opp_i)
```

This distinction is deliberate because `RAC_opp` shares its numerator with MAI and creates structural collinearity when included in the primary composite.

### 5.5 Motorcycle Network Calibration

Motorcycle Network D must not assume unmodified car-equivalent OSM speeds. Per-road-class motorcycle speeds are modeled as transparent scenario assumptions informed by Hanoi motorcycle-speed literature. Son et al. (2012) collected GPS travel-speed data for 65 Hanoi motorcycle users across three broad road categories and report highway speeds of 36.6–48.5 km/h (peak/non-peak), arterial speeds of 16.2–33.6 km/h, and residential speeds of 23.5–26.7 km/h. These broad empirical ranges are used as contextual plausibility bounds; the current OSM highway-class values (45.0, 44.0, 39.9, 35.2, 29.9, 22.0, 21.0, 14.0, 9.0 km/h) are scenario-calibrated modeling assumptions rather than direct per-class citations, as no verified Hanoi source reporting motorcycle speeds separately for OSM primary, secondary, and tertiary classes was identified in citation audit (see `docs/decisions.md` DEC-030). JICA HAIDEP (2007) provides road design speeds only, not observed motorcycle travel speeds. Manual Android Google Maps checks provide a plausibility validation; the model does not isolate or test a lane-splitting mechanism. Sensitivity of all results to ±20% and ±40% speed scaling is reported separately (`outputs/validation/motorcycle_speed_sensitivity.md`); typology agreement kappa ≥ 0.987 across scenarios.

### 5.6 Sustainable Mobility Capability Index (SMCI)

SMCI is multiplicative: a weak-link-sensitive composite with zero annihilation.

```text
SMCI_i = NAI_norm_i * MAI_norm_i * RAC_norm_i
```

A cell scores high only when local walking access, metropolitan access, and competitive sustainable mobility are jointly strong. A zero normalized component sets SMCI to zero; among positive values, however, partial compensation remains possible. Scenario comparisons use shared A+B normalization bounds throughout so that Delta_SMCI is a clean modeled scenario difference.

### 5.7 Typology

Each cell is classified by a theory-first two-axis split rather than by unsupervised clustering. First a Metropolitan Competitiveness Score is computed:

```text
MCS_i = sqrt(MAI_norm_i * RAC_norm_i)
```

Cells are then split on rank-based medians of NAI and MCS. Rank-based medians preserve the four-way partition even when MCS has a mass point at zero.

**Table 2. Typology definitions.**

| NAI | MCS | Typology | Interpretation |
|---|---|---|---|
| High | High | Integrated Capability | Local access and metropolitan competitiveness both present |
| High | Low | Fragmented Capability | Locally walkable but metropolitan sustainable mobility weak |
| Low | High | Transit-Dependent | Metropolitan access despite weak local access |
| Low | Low | Motorcycle Lock-in | Neither local access nor transit competitiveness strong |

---

## 6. Results

### 6.1 The VinBus Scenario Raises Modeled Capability, But Zero-Access Cells Must Be Separated

Across <!-- headline:/n_cells|int -->462<!-- /headline --> cells, under the primary operational 800 m (10-minute) NAI walking catchment and RAC_time specification, mean SMCI is **0.0070 under Scenario A and 0.0133 under Scenario B**, a modeled mean difference of **+0.0063**. The global mean is not the primary interpretive statistic because the multiplicative SMCI is zero-inflated: if NAI, MAI, or RAC is zero, SMCI is zero. We therefore report zero-access cells separately and compute distributional summaries for cells with positive capability.

The modeled difference is broad but spatially uneven: **<!-- headline:/delta_groups/improved|int -->281<!-- /headline --> cells (60.8%) have higher SMCI under Scenario B, 88 are unchanged, and 93 have slightly lower SMCI** once RAC_time is defined as an opportunity-weighted travel-time ratio. The unchanged cells are primarily zero-access cells. Lower Scenario B values are interpreted cautiously: the VinBus network assumption expands modeled opportunity access for many cells, but the time-competitiveness term can be lower where the additional reachable opportunities have longer weighted walk-transit times than the motorcycle benchmark.

**Table 3. Primary pilot results**

| Metric | Result |
|---|---:|
| Grid cells | 462 |
| Mean SMCI A / B / Delta | 0.0070 / 0.0133 / +0.0063 |
| Positive-cell median A / B | 0.0051 / 0.0081 |
| Cells improved / unchanged / declined | 281 / 88 / 93 |
| Share improved | 60.8% |
| Zero-NAI cells | 88 (19.0%) |

Among cells with positive SMCI, the median is **0.0051** under Scenario A and **0.0081** under Scenario B. This indicates that the modeled scenario difference is not confined to the mean or to a few high-access cells. The unchanged group is also substantively meaningful: these are cells where adding metropolitan transit access does not overcome missing neighborhood walking access or very weak local opportunity structure.

### 6.2 Spatial Fragmentation Persists Under the VinBus Network Assumption

Even with VinBus, the Scenario B typology is sharply divided (Table 4). **<!-- headline:/typology_B/Motorcycle Lock-in|int -->171<!-- /headline --> cells (37.0%) remain in Motorcycle Lock-in**, exactly matching the 171 cells in Integrated Capability, with 60 cells each in the Fragmented and Transit-Dependent types. For comparison, Scenario A places 144 cells each in Integrated and Motorcycle Lock-in and 87 each in the intermediate types; switching to the Scenario B network assumption changes the modeled classification of **130 of 462 cells** (28.1%).

**Table 4. Typology distribution by scenario.**

| Typology | Scenario A (cells) | Scenario B (cells) | Scenario B (% cells) |
|---|---:|---:|---:|
| Integrated Capability | 144 | 171 | 37.0% |
| Fragmented Capability | 87 | 60 | 13.0% |
| Transit-Dependent | 87 | 60 | 13.0% |
| Motorcycle Lock-in | 144 | 171 | 37.0% |

The persistence of a large Motorcycle Lock-in class under the Scenario B network assumption is the central substantive finding: more than a third of the megaproject grid remains modeled as having neither strong local access nor strong transit competitiveness.

### 6.3 Population Exposure: The Equity Reading Is Slightly Worse Than the Cell Average

Cell averages still require an exposure check. Using WorldPop 2020 (estimated study-area population approximately 78,816; all 462 cells non-zero), the **population-weighted mean SMCI_B is 0.0129 versus the unweighted 0.0133**, a small downward bias of 3.2%. The rank correlation between cell population and SMCI_B is near zero (Spearman rho = -0.007), so population is roughly evenly spread across capability levels.

By population share, the **Integrated Capability type houses the largest resident group at 34.7%**, with **Motorcycle Lock-in a near-equal 33.9%**, ahead of Fragmented Capability (16.0%) and Transit-Dependent (15.4%). A resident group as large as the best-served type therefore lives where sustainable mobility capability is weakest, even though the population-weighted and unweighted means are close.

### 6.4 Zero-Access Cells Are Genuinely Built and Populated

At the 800 m primary threshold the pilot has **88 zero-NAI cells (19.0%)**, and the same 88 cells have SMCI_B = 0 because the index is multiplicative. This is not a lake-and-park artifact: VIDA building footprints are present in **455 of 462 cells (98.5%)**, and **84 of the 88 zero-NAI cells are built**, housing about **11,798 residents (15.0% of the pilot population)**. Zero inflation thus reflects under-served built-up areas, which is a substantive caution for interpretation rather than a data error. (At the 1200 m optimistic upper bound, zero-NAI cells fall to 33/462, 7.1%.) These cells should be reported as a separate zero-access category rather than absorbed into the lowest positive quantile.

### 6.5 Robustness

**Headway assumptions (Network C).** VinBus route data provide observed per-route headways for most routes, with a fallback headway used only where route frequencies are absent. Sensitivity tests show that fallback-headway choices do not materially alter the study-area classification: **the typology partition is invariant (Cohen's kappa = 1.00)** across the tested fallback scenarios.

**Structural multicollinearity (MAI vs. RAC).** Because RAC_opp shares its numerator (MAI_transit) with MAI, the two are collinear by construction. In the legacy full-RAC specification VIF is high (NAI 2.45, MAI 9.07, RAC 9.73). The promoted primary uses RAC_time alone, which removes the shared term and brings all terms well within the conventional threshold (NAI 2.26, MAI 2.93, RAC_time 2.05). The typology agreement between the promoted RAC_time primary and the legacy full-RAC specification is **Cohen's kappa = <!-- headline:/full_rac_agreement/kappa|.3f -->0.906<!-- /headline --> (<!-- headline:/full_rac_agreement/cells_relabelled|int -->30<!-- /headline --> of 462 cells relabelled)**. The RAC_time specification is retained as primary, with the legacy full-RAC reported as a robustness disclosure.

**Motorcycle speed sensitivity.** Three Network D calibration scenarios were tested. The slower calibration raises mean SMCI_B to 0.0160; the faster calibration lowers it to 0.0115. Typology agreement remains near-perfect in both cases (**kappa >= 0.987; <= 4 of 462 cells relabelled**), indicating that the classification is not driven by a narrow motorcycle-speed assumption.

**Transit impedance sensitivity.** Behavioral penalties were applied only to walk-transit travel times, leaving MAI opportunity weights unchanged. Conservative penalties reduce mean SMCI_B to 0.0098 and pessimistic penalties to 0.0065; typology agreement remains high (**kappa = 0.901 and 0.895**, respectively, with 32 and 34 cells relabelled). This is a behavioral-realism sensitivity, not observed mode-choice validation.

**Supply-side population weighting.** Adding the WorldPop-derived supply-side multiplier to MAI relabels only 8 of 462 cells relative to the no-population baseline (**kappa = 0.976**). Population weighting therefore improves the defensibility of opportunity magnitudes without driving the typology result.

**Observed-vs-proxy MAI.** The primary specification uses strict, source-backed opportunity magnitudes for every included destination across all four domains. Moving from the proxy baseline to this strict provenance-tiered specification changes mean SMCI_B only from **0.0129 to 0.0133**, with **Cohen's kappa = 0.937** and **20 of 462 cells relabelled**; the cell ranking is preserved almost exactly (**Spearman rho = 0.9965**). Every included destination has a source-backed magnitude, with disaggregated values capped and key facilities anchored using citable headcounts.

**Index form.** Against an additive alternative SMCI_add = (NAI_norm + MAI_norm + RAC_norm)/3, the multiplicative SMCI ranking holds strongly but not trivially. A geometric-mean alternative is deliberately not used as a robustness check, because it is a monotonic transform of the product and would yield rho = 1.0 by construction.

**RAC normalization.** Comparing plain min-max against log(1+x) followed by min-max normalization of the RAC subcomponents yields identical typologies (kappa = 1.00) and near-identical SMCI rankings (rho = 0.9999), confirming insensitivity to the modest right-skew of RAC.

### 6.6 Validation

**Motorcycle travel times.** Ten named origin-destination pairs measured manually in the Android Google Maps app give a mean absolute error of **1.90 minutes** and a bias of **-1.04 minutes**, i.e., the calibrated model is slightly optimistic relative to the consumer app. This is a plausibility check; calibrated network times remain the primary basis because Google TWO_WHEELER API coverage for Vietnam is not relied upon.

**POI quality.** A 20-record spot-check of the initial POI layer found 14 confirmed, 2 duplicates, 2 misclassifications, and 2 missing. The 55 Overture-only POIs were separately spot-checked at 100% confirmation before promotion of the merged layer. Economic-domain enrichment is reported as a strengthened open-data opportunity layer; observed-count coverage and proxy fallback are reported through the observed-vs-proxy MAI sensitivity.

### 6.7 The Enclave Boundary Is Sharp, Not Gradual

The proposal's central scalar claim — that project-level accessibility and metropolitan capability are distinct achievements — is tested directly with a distance-banded comparison across the Ocean Park 1 boundary (`outputs/tables/boundary_discontinuity.csv`). Cells are grouped into 250-500 m bands on each side of the boundary under Scenario B.

**Table 5. SMCI_B and typology share by distance from the Ocean Park 1 boundary.**

| Band | Side | Cells | SMCI_B mean | Integrated Capability | Motorcycle Lock-in |
|---|---|---:|---:|---:|---:|
| 0-250 m | inside | 39 | 0.0929 | 89.7% | 5.1% |
| 250-500 m | inside | 22 | 0.0938 | 100.0% | 0.0% |
| 500-1000 m | inside | 9 | 0.1051 | 100.0% | 0.0% |
| 0-250 m | outside | 44 | 0.0096 | 40.9% | 31.8% |
| 250-500 m | outside | 47 | 0.0088 | 23.4% | 40.4% |
| 500-1000 m | outside | 109 | 0.0119 | 21.1% | 34.9% |

Mean SMCI_B drops by a factor of roughly **10x within the first 250 m outside the boundary** (0.0929 inside to 0.0096 outside), and the Integrated Capability share falls from 89.7% to 40.9% over the same step. The discontinuity is not a smooth decay: cells 250-1000 m outside the boundary show similar or slightly lower SMCI_B than the immediately adjacent band, indicating a step change at the project edge rather than a gradient into the surrounding city. Population living within 250 m outside the boundary (approximately 5,799 residents) already experiences Motorcycle Lock-in at nearly a third of cells, compared with 5.1% just inside.

This pattern is consistent with an enclave-like accessibility discontinuity: the planned core has much higher modeled accessibility than nearby outside cells. The cross-sectional boundary comparison does not identify the institutional cause of the discontinuity, demonstrate temporal diffusion or failure to diffuse, or establish that the project boundary itself caused the difference.

---

## 7. Discussion

**Local walkability is not sustainable mobility capability.** The pilot operationalizes, and then empirically separates, two capabilities that are routinely conflated. Ocean Park performs reasonably on neighborhood access in many cells, yet 63.0% of cells fall outside Integrated Capability and 37.0% remain in Motorcycle Lock-in even with VinBus. The framework's value is its ability to make this gap visible and locable.

**The project boundary marks an accessibility discontinuity rather than a smooth gradient.** Section 6.7 shows SMCI_B falling roughly tenfold within 250 m of crossing the Ocean Park 1 boundary, with no smooth recovery further out. This cross-sectional step-change pattern is consistent with enclave-like accessibility, while remaining insufficient to identify the governance mechanism, establish causal boundary effects, or test temporal diffusion.

**The benchmark mode matters.** Car–transit comparisons are established in accessibility research, but they do not represent the most salient competing mode in motorcycle-dependent Hanoi. RAC therefore asks how modeled walk-transit accessibility compares with modeled motorcycle accessibility. It does not estimate whether a particular resident would switch modes.

**Transit alone is not enough.** Under the VinBus network assumption, almost two-thirds of the grid has higher modeled SMCI, but the modeled motorcycle advantage persists. The unchanged group, the cells with lower time competitiveness, and the zero-access built cells show that metropolitan transit provision cannot substitute for local opportunity structure and fine-grained pedestrian connectivity. Transit provision must therefore be coupled with land-use integration rather than treated as a standalone fix. The equity dimension remains important because the Motorcycle Lock-in population share (33.9%) is nearly as large as the Integrated Capability share (34.7%).

**Zero access is analytically different from low access.** The maps and result tables should not place cells with value 0.0 into the same color class as low positive cells. Zero access means one component of the multiplicative composite is absent; low positive access means all three measured conditions exist but their joint score is weak.

**External validation.** The framework uses open data plus explicit scenario-assumed mode speeds and is designed for testing in other motorcycle-dependent cities. Its portability to Ho Chi Minh City, Bangkok, Jakarta, Bengaluru, or other settings remains a future empirical question rather than a demonstrated result.

---

## 8. Limitations

This is a single-site pilot; the goal is framework development and feasibility, not citywide or national generalization. The 462-cell extent covers Ocean Park and a 2 km buffer only.

The metropolitan index's strict primary specification includes only source-backed magnitudes; a separate coverage-oriented sensitivity specification uses proxy-backed magnitudes with explicit provenance. Economic enrichment and supply-side population weighting improve the opportunity layer, but employment remains the hardest domain unless point jobs or defensible ward-level dasymetric estimates are obtained. MAI should therefore be read as a provenance-tracked opportunity index, not as a complete census of jobs or seats.

Transit data are imperfect. Network B is the modeled 2018 conventional-transit reference network and is not current service or an observed pre-VinBus panel. Network C uses a pseudo-GTFS layer constructed from the VinBus public API. It is not a fully scheduled timetable feed, though route headway and stop data are strong enough for the stop-level routing used here.

Structural collinearity is a concern in the legacy full-RAC specification because RAC_opp shares the MAI_transit term. The promoted RAC_time primary removes that shared component; agreement with the legacy full-RAC typology is kappa = 0.906, with 30 of 462 cells relabelled.

Mode and impedance specifications omit behaviorally salient details such as fares, parking, transfer penalties, access/egress discomfort, and schedule unreliability. The transit-impedance sensitivity partially bounds this issue, but it does not replace observed mode-choice or reliability data.

Motorcycle validation is limited to 10 manual OD pairs, appropriate for pilot plausibility but not a full calibration dataset. No observed mode shares, travel diaries, or revealed commute times are used to validate the capability typology externally.

The VinBus pseudo-GTFS creates an ethics and replicability risk. The source API is public and contains no personal data, but licensing and terms-of-service uncertainty remain. Derived route tables should be replaced with official GTFS if VinBus publishes one.

---

## 9. Conclusion

We have developed and piloted a dual-scale, mode-competitive accessibility framework that distinguishes neighborhood access, metropolitan access, and modeled competitiveness against motorcycle access rather than car access. Applied to Vinhomes Ocean Park, the framework estimates higher sustainable mobility capability under the VinBus network assumption than under the conventional-transit reference (mean SMCI 0.0070 versus 0.0133; 60.8% of cells higher), while 37.0% of cells containing 33.9% of residents remain classified as Motorcycle Lock-in. The more important result is distributional: 19.0% of cells remain at zero walking access, and 95.5% of those zero-access cells are built. The findings are robust to motorcycle-speed assumptions, transit-impedance penalties, normalization choices, and the legacy full-RAC specification. The study offers an integrated operationalization and a single-site empirical application; external validation is required before transferability can be claimed.

---

## References

Bantis, T., & Haworth, J. (2020). Assessing transport related social exclusion using a capabilities approach to accessibility framework: A dynamic Bayesian network approach. *Journal of Transport Geography, 84*, 102673. https://doi.org/10.1016/j.jtrangeo.2020.102673

Bruno, M., Monteiro Melo, H. P., Campanelli, B., & Loreto, V. (2024). A universal framework for inclusive 15-minute cities. *Nature Cities, 1*(10), 633-641. https://doi.org/10.1038/s44284-024-00119-4

Caprotti, F. (2014). Eco-urbanism and the eco-city, or, denying the right to the city? *Antipode, 46*(5), 1285-1303. https://doi.org/10.1111/anti.12087

Caprotti, F., Springer, C., & Harmer, N. (2015). 'Eco' for whom? Envisioning eco-urbanism in the Sino-Singapore Tianjin eco-city, China. *International Journal of Urban and Regional Research, 39*(3), 495-517. https://doi.org/10.1111/1468-2427.12233

Cugurullo, F. (2016). Urban eco-modernisation and the policy context of new eco-city projects: Where Masdar City fails and why. *Urban Studies, 53*(11), 2417-2433. https://doi.org/10.1177/0042098015588727

Đào Đức Hiếu, Đỗ Thị Tám, Nguyễn Thị Hồng Hạnh, Trương Đỗ Thuỳ Linh, & Lê Xuân Sang. (2024). Thu hồi đất để xây dựng khu đô thị: Nghiên cứu tại dự án Vinhomes Ocean Park trên địa bàn huyện Gia Lâm, thành phố Hà Nội. *Tạp chí Khoa học và Công nghệ Lâm nghiệp, 13*(3), 156-167. https://doi.org/10.55250/jo.vnuf.13.3.2024.156-167

Geurs, K. T., & van Wee, B. (2004). Accessibility evaluation of land-use and transport strategies: Review and research directions. *Journal of Transport Geography, 12*(2), 127-140. https://doi.org/10.1016/j.jtrangeo.2003.10.005

Greco, S., Ishizaka, A., Tasiou, M., & Torrisi, G. (2019). On the methodological framework of composite indices: A review of the issues of weighting, aggregation, and robustness. *Social Indicators Research, 141*, 61-94. https://doi.org/10.1007/s11205-017-1832-9

Ha, P. T. H., van den Bosch, F., Quang, N. N., & Zuidgeest, M. (2011). Urban form and accessibility to jobs: A comparison of Hanoi and Randstad metropolitan areas. *Environment and Urbanization Asia, 2*(2), 265-285. https://doi.org/10.1177/097542531100200209

Handy, S. L., & Niemeier, D. A. (1997). Measuring accessibility: An exploration of issues and alternatives. *Environment and Planning A, 29*(7), 1175-1194. https://doi.org/10.1068/a291175

Hansen, W. G. (1959). How accessibility shapes land use. *Journal of the American Institute of Planners, 25*(2), 73-76. https://doi.org/10.1080/01944365908978307

Japan International Cooperation Agency (JICA). (2007). *The comprehensive urban development programme in Hanoi capital city of Vietnam (HAIDEP)*. JICA / Hanoi People's Committee.

Joss, S., Tomozeiu, D., & Cowley, R. (2011). Eco-cities: The mainstreaming of urban sustainability - key characteristics and driving factors. *International Journal of Sustainable Development and Planning, 6*(3), 268-285. https://doi.org/10.2495/SDP-V6-N3-268-285

Kaszczyszyn, P., & Sypion-Dutkowska, N. (2019). Walking access to public transport stops for city residents: A comparison of methods. *Sustainability, 11*(14), 3758. https://doi.org/10.3390/su11143758

Khuat, V. H. (2006). *Traffic management in motorcycle dependent cities* (Doctoral dissertation). Darmstadt University of Technology.

Kieu, M., Comber, A., Nguyen Thi Thuy, H., Bui Quang, T., Hoang Huu, P., & Malleson, N. (2024). An open dataset on individual perceptions of transport policies. *Scientific Data, 11*(1), 104. https://doi.org/10.1038/s41597-024-02950-9

Kieu, M., Wanjau, E., Comber, A., Bratkova, K., Nguyen Thi Thuy, H., Bui Quang, T., Hoang Huu, P., & Malleson, N. (2023). Factors affecting perceptions in transport—A deep dive into the motorbike ban in Hanoi, Vietnam. *Case Studies on Transport Policy, 11*, 100958. https://doi.org/10.1016/j.cstp.2023.100958

Labbé, D., & Boudreau, J.-A. (2011). Understanding the causes of urban fragmentation in Hanoi: The case of new urban areas. *International Development Planning Review, 33*(3), 273-291. https://doi.org/10.3828/idpr.2011.15

Labbé, D., & Boudreau, J.-A. (2015). Local integration experiments in the new urban areas of Hanoi. *South East Asia Research, 23*(2), 245-262. https://doi.org/10.5367/sear.2015.0259

Liao, Y., Gil, J., Pereira, R. H. M., Yeh, S., & Verendel, V. (2020). Disparities in travel time between car and transit: Spatiotemporal patterns in cities. *Scientific Reports, 10*, 4056. https://doi.org/10.1038/s41598-020-61077-0

Logan, T. M., Hobbs, M. H., Conrow, L. C., Reid, N. L., Young, R. A., & Anderson, M. J. (2022). The x-minute city: Measuring the 10, 15, 20-minute city and an evaluation of its use for sustainable urban design. *Cities, 131*, 103924. https://doi.org/10.1016/j.cities.2022.103924

Moreno, C., Allam, Z., Chabaud, D., Gall, C., & Pratlong, F. (2021). Introducing the "15-Minute City": Sustainability, resilience and place identity in future post-pandemic cities. *Smart Cities, 4*(1), 93-111. https://doi.org/10.3390/smartcities4010006

Munda, G., & Nardo, M. (2009). Noncompensatory/nonlinear composite indicators for ranking countries: A defensible setting. *Applied Economics, 41*(12), 1513-1523. https://doi.org/10.1080/00036840601019364

OECD/European Union/EC-JRC. (2008). *Handbook on constructing composite indicators: Methodology and user guide*. OECD Publishing. https://doi.org/10.1787/9789264043466-en

Pereira, R. H. M., Saraiva, M., Herszenhut, D., Braga, C. K. V., & Conway, M. W. (2021). r5r: Rapid realistic routing on multimodal transport networks with R5 in R. *Findings*. https://doi.org/10.32866/001c.21262

Psyllidis, A., Gao, S., Hu, Y., Kim, E-K., McKenzie, G., Purves, R., Yuan, M., & Andris, C. (2022). Points of Interest (POI): A commentary on the state of the art, challenges, and prospects for the future. *Computational Urban Science, 2*(1), 20. https://doi.org/10.1007/s43762-022-00047-w

Shatkin, G. (2008). The city and the bottom line: Urban megaprojects and the privatization of planning in Southeast Asia. *Environment and Planning A, 40*(2), 383-401. https://doi.org/10.1068/a38439

Son, H. T., Zhang, J., & Fujiwara, A. (2012). Developing a toolbox for calculating motorcycle emission and the difference of CO2 from motorcycle for each type of road in Hanoi. *International Journal of Environmental Science and Development, 3*(5), 412-416. https://doi.org/10.7763/IJESD.2012.V3.257

Stępniak, M., Pritchard, J. P., Geurs, K. T., & Goliszek, S. (2019). The impact of temporal resolution on public transport accessibility measurement: Review and case study in Poland. *Journal of Transport Geography, 75*, 8-24. https://doi.org/10.1016/j.jtrangeo.2019.01.007

Vecchio, G., & Martens, K. (2021). Accessibility and the capabilities approach: A review of the literature and proposal for conceptual advancements. *Transport Reviews, 41*(6), 833-854. https://doi.org/10.1080/01441647.2021.1931551

Vingroup. (2021a, April 8). *VinBus chính thức vận hành* [VinBus officially begins operation]. https://vingroup.net/vi/tin-tuc-su-kien/bai-viet/2324/vinbus-chinh-thuc-van-hanh-

Vingroup. (2021b, December 2). *Xe buýt điện VinBus chính thức tham gia mạng lưới vận tải hành khách công cộng* [Electric VinBus buses officially join the public passenger transport network]. https://vingroup.net/vi/tin-tuc-su-kien/bai-viet/2449/xe-buyt-dien-vinbus-chinh-thuc-tham-gia-

VinBus. (n.d.). *Mạng lưới tuyến* [Route network]. Retrieved 2026, from https://vinbus.vn/gioi-thieu/mang-luoi-tuyen

Vinhomes. (n.d.). *Tổng quan dự án Vinhomes Ocean Park* [Vinhomes Ocean Park project overview]. Retrieved 2026, from https://vinhomes.vn/vi/tong-quan-du-an-vinhomes-ocean-park

Vu Anh Tuan. (2015). Mode choice behavior and modal shift to public transport in developing countries—the case of Hanoi City. *Journal of the Eastern Asia Society for Transportation Studies, 11*(0), 473-487. https://doi.org/10.11175/easts.11.473

---

*Data, code, formulas, and validation outputs are maintained in the project repository (`src/`, `outputs/`, `docs/`). All indices are implemented and unit-tested in `src/accessibility.py` and the pipeline test suite. Pilot results derive from `data/processed/pilot_metrics.csv`.*

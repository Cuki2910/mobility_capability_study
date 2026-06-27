# Fragmented Mobility Capability in a Motorcycle-Dependent Green Megaproject: A Dual-Scale, Mode-Competitive Accessibility Framework from Vinhomes Ocean Park, Hanoi

**Author:** Cuki2910
**Target journal:** *Journal of Transport Geography*
**Article type:** Methods development and pilot validation
**Draft date:** 2026-06-24 (updated: 2026-06-27 pilot metrics and zero-access interpretation)

---

## Abstract

Green-branded megaprojects in Southeast Asia are increasingly promoted as sustainable alternatives to dispersed, motorcycle-dependent urban growth. Yet conventional accessibility metrics evaluate such projects either at the neighborhood scale (walkability, the "15-minute city") or at the metropolitan scale (cumulative-opportunity job access), and almost always benchmark public transport against the private car. In motorcycle-dependent cities, where the practical alternative to transit is the motorcycle rather than the car, both choices misrepresent the lived constraint on sustainable mobility. This paper develops and pilots a dual-scale, mode-competitive accessibility framework that separates neighborhood-scale walking access from metropolitan-scale walk-and-transit access, and introduces a Relative Accessibility Competitiveness (RAC) term that benchmarks walk-and-transit performance directly against motorcycle performance. The three components are combined into a multiplicative Sustainable Mobility Capability Index (SMCI) and a theory-first four-way spatial typology.

We pilot the framework on Vinhomes Ocean Park, Hanoi, a 250+ ha electric-bus-branded development, across 462 grid cells of 250 m. The analysis uses OpenStreetMap walking and driving networks, a merged 208-feature opportunity layer, a 2018 pre-VinBus GTFS baseline, VinBus pseudo-GTFS stop and headway data, VIDA building footprints, and WorldPop 2020 population. Motorcycle travel times are calibrated from Vietnamese speed literature and validated against manual Google Maps measurements (mean absolute error 1.90 minutes). The VinBus scenario raises mean SMCI from 0.0322 to 0.0435 and improves 298 of 462 cells (64.5%), while 88 cells are unchanged and 76 decline slightly under the opportunity-weighted time-competitiveness term. However, 88 cells (19.0%) remain at zero walking access; 84 of these zero-access cells (95.5%) are built cells. Among cells with positive SMCI, the median rises from 0.0197 to 0.0220, showing that improvement is not only a mean effect. Findings are robust to motorcycle-speed sensitivity (kappa >= 0.994), transit-impedance sensitivity (kappa >= 0.890), and a RAC_time-only specification addressing structural multicollinearity (kappa = 0.900). The pilot demonstrates that local walkability and competitive sustainable mobility are distinct capabilities, and that green mobility claims must be evaluated through both distributional improvement and persistent zero-access fragmentation.

**Keywords:** accessibility; mode competition; motorcycle dependence; sustainable mobility; green megaprojects; Hanoi; Vietnam

---

## 1. Introduction

Sustainable mobility is commonly equated with two things that are, in practice, distinct: living near everyday destinations, and being able to reach the wider city without a private vehicle. The first is the logic of walkability indices and the "15-minute city" (Moreno et al., 2021). The second is the logic of cumulative-opportunity accessibility, which counts the jobs or services reachable within a travel-time threshold (Handy & Niemeier, 1997; Geurs & van Wee, 2004). Both framings are valuable, but each, used alone, can mislead. A neighborhood may be highly walkable yet poorly connected to metropolitan opportunity; conversely, a cell with good metropolitan transit access may sit in a locally barren environment.

A second limitation applies to motorcycle-dependent cities. The accessibility-and-mode-choice literature usually frames the competitiveness of public transport relative to the private car, typically through a transit-to-car travel-time or opportunity ratio (e.g., Liao et al., 2020; Kaszczyszyn & Sypion-Dutkowska, 2019). In Hanoi this benchmark is the wrong one. Motorcycles account for over 80% of trips in the city (Vu Anh Tuan, 2015), are faster than cars in congested conditions because of lane-splitting, and are deeply embedded in household routines. A transit service that would be "competitive with the car" can remain uncompetitive with the motorcycle, which is the mode residents actually weigh it against.

This matters for the evaluation of green megaprojects: large, master-planned, environmentally branded developments that are proliferating across Vietnam and the wider region. Their sustainability claims rest partly on internal amenities and partly on new transit provision, such as the electric VinBus network at our study site. But if the relevant counterfactual is the motorcycle, then neither "amenities within walking distance" nor "a bus line exists" is sufficient evidence that the development produces sustainable mobility capability.

We ask: **Does a green-branded development produce sustainable mobility capability when everyday life remains organized around the motorcycle?** We answer by building a framework that measures neighborhood access and metropolitan access on separate scales, adds a mode-competition term benchmarked against the motorcycle, and combines these into a weakest-link index and an interpretable spatial typology. We then validate the framework with a pilot implementation at Vinhomes Ocean Park, Hanoi.

The contribution is methodological: a transferable, reproducible accessibility framework for motorcycle-dependent regions of Southeast Asia, South Asia, and Latin America. The pilot is a feasibility and validation exercise, not a final citywide result.

---

## 2. Related Work and Contribution

**Neighborhood-scale accessibility.** Walkability scores and the 15-minute-city concept measure local proximity to daily destinations (Moreno et al., 2021). They capture an important dimension of sustainable urbanism but are blind to metropolitan-scale inequality: a cell can be locally complete yet metropolitanly isolated.

**Metropolitan-scale accessibility.** Cumulative-opportunity and gravity-based measures count opportunities reachable within a travel-time budget (Handy & Niemeier, 1997; Geurs & van Wee, 2004). These measures capture metropolitan reach but, when reported as a single citywide surface, can mask neighborhood-level exclusion.

**Person- and place-based accessibility.** Place-based accessibility surfaces are reproducible and well suited to spatial diagnosis, but they do not observe individual constraints, household resources, or daily activity schedules. Person-based approaches address these constraints more directly, while requiring survey or trace data that are unavailable in this pilot. Our framework remains place-based, but its capability framing keeps the interpretation close to what residents can plausibly do from each location.

**GTFS and open-data accessibility.** GTFS-based accessibility methods have made transit evaluation more reproducible, especially when paired with open street networks and cumulative-opportunity measures. This study follows that open-data tradition but faces a common Global South limitation: one network has a dated public feed, and the new private/electric operator does not publish official GTFS. We therefore separate official-feed, pseudo-GTFS, and non-API route-relation evidence rather than treating all transit data as equivalent.

**Motorcycle mobility, megaprojects, and capability.** Southeast Asian accessibility studies must account for motorcycle dominance, because two-wheelers affect speed, parking, access/egress, and mode-choice thresholds in ways that car-based benchmarks miss (Khuat, 2006; Vu Anh Tuan, 2015). The same issue is acute in green megaproject and TOD evaluation: project branding may emphasize electric transit or internal amenities, while residents continue to evaluate trips against the speed and flexibility of motorcycles. A capability perspective shifts attention from infrastructure provision to feasible mobility outcomes.

**Mode-competitive accessibility.** A smaller literature frames transit performance relative to the competing mode, usually the private car, via travel-time or opportunity ratios (Liao et al., 2020; Kaszczyszyn & Sypion-Dutkowska, 2019). This is the closest precedent to our approach, and we adopt its central insight: absolute accessibility is less behaviorally meaningful than accessibility relative to the realistic alternative.

**Our contribution** combines three elements that, to our knowledge, have not been integrated in a single framework:

| Existing framing | Limitation | Representative sources |
|---|---|---|
| Walkability / 15-minute city | Local only; ignores metropolitan-scale inequality | Moreno et al. (2021) |
| Citywide cumulative-opportunity access | Aggregate; masks neighborhood exclusion | Handy & Niemeier (1997); Geurs & van Wee (2004) |
| Transit competitiveness vs. the car | Wrong benchmark in motorcycle-dependent cities | Liao et al. (2020); Kaszczyszyn & Sypion-Dutkowska (2019) |

Specifically, we separate neighborhood and metropolitan scales rather than collapsing them; make mode competition explicit through RAC; and benchmark against the motorcycle, the empirically dominant mode in our setting (Vu Anh Tuan, 2015; Khuat, 2006).

---

## 3. Study Area

The case study is Vinhomes Ocean Park in Gia Lam district, on the eastern edge of Hanoi. It is a master-planned development exceeding 250 ha, marketed around environmental quality and served by an electric bus network (VinBus). The site is analytically useful because it combines green branding and internal amenities with continued exposure to Hanoi's motorcycle-oriented travel environment.

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
| Motorcycle speed calibration | Network D speeds | JICA HAIDEP (2010); Nguyen & Nguyen (2018); Vu Anh Tuan et al. (2016) |

**Data provenance and caveats.**

The 2018 GTFS feed predates the commercial launch of VinBus in September 2021 and is therefore used deliberately as the pre-intervention conventional-transit baseline (Network B), not as current service. Stop geometry is used for stop-level accessibility; timetable frequency is treated only as a relative-magnitude proxy. Maintained GTFS catalogs were checked, and no current-service Hanoi feed was identified for replacement.

VinBus (Network C) data are sourced from the publicly accessible VinBus route-query API. Because VinBus does not publish an official GTFS feed, we constructed a pseudo-GTFS layer from the application's JSON endpoints. The complete Hanoi network was extracted: 176 routes, 5,631 unique stop nodes with official GPS coordinates, 19,625 ordered stop-sequence records across both travel directions, and per-route headway data for most routes. Network C is therefore a stop-level intervention-routing scenario with observed route headways where available, not a fully scheduled transit assignment.

The opportunity layer merges OpenStreetMap and Overture Maps, then adds OSM landuse and office-tag enrichment for metropolitan opportunity domains. A source-agreement audit was applied: 55 Overture-only POIs were spot-checked and all 55 were confirmed, passing the promotion gate. Economic enrichment adds landuse=commercial/retail/industrial/office polygons, office tags, financial amenities, and marketplace features. The primary opportunity layer therefore contains 208 POIs/features across economic, higher-education, healthcare, and metropolitan commercial/service domains.

WorldPop is used in two distinct ways. First, it enters MAI as a supply-side opportunity multiplier: `m_j = clip(sqrt(pop_density_j / median), 0.5, 2.0)`, applied to all opportunity domains so that opportunities in denser catchments receive larger effective weights. Second, it is used as a post-hoc population-exposure cross-check at origin cells. These two uses are reported separately: the first affects MAI/SMCI, while the second evaluates who is exposed to each capability level.

### 4.1 Data Ethics and Replicability

VinBus does not publish an official GTFS feed. The pseudo-GTFS used here is derived from publicly accessible web-application API responses and contains route, stop, direction, and headway information. No private user data, authentication bypass, personal traces, or individual-level records are used.

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

Two scenarios are compared. **Scenario A** uses Networks A + B (no VinBus). **Scenario B** uses Networks A + C (with VinBus). Network D is the competitiveness benchmark in both. The intervention effect is Delta_SMCI = SMCI(B) - SMCI(A), computed on shared A+B normalization bounds so that the difference reflects scenario change rather than re-scaling artifacts.

### 5.2 Neighborhood Accessibility Index (NAI)

NAI is a count of qualifying POIs reachable on the walking network within the neighborhood threshold:

```text
NAI_i = count of qualifying POIs reachable by walking from cell i within the neighborhood threshold
```

A simple count is used deliberately: at the neighborhood scale, the presence of a school, clinic, shop, or park is more behaviorally relevant than its precise capacity. NAI is min-max normalized to NAI_norm for index construction.

### 5.3 Metropolitan Accessibility Index (MAI)

MAI is a composite Metropolitan Opportunity Accessibility score across four domains, by walking plus transit. It is framed as opportunity accessibility rather than employment accessibility because building-resolution employment data are unavailable for Hanoi.

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

Each POI's opportunity weight is multiplied by a bounded supply-side population factor derived from the residential density of its containing grid cell:

```text
m_j = clip( sqrt(pop_density_j / median(pop_density>0)), 0.5, 2.0 )
```

The same effective weights are used for transit and motorcycle MAI, so RAC_opp remains an internally consistent ratio. Sensitivity runs compare this primary specification with a no-population baseline.

### 5.4 Relative Accessibility Competitiveness (RAC)

RAC measures whether walking-and-transit access is competitive with motorcycle access. It has two subcomponents, a time ratio and an opportunity ratio:

```text
RAC_time_raw_i = motorcycle_travel_time_i / walk_transit_travel_time_i
RAC_opp_raw_i  = MAI_transit_i / MAI_motorcycle_i
```

`RAC_time_raw_i` is computed as the motorcycle opportunity-weighted mean travel time divided by the walk-and-transit opportunity-weighted mean travel time. The destination set, domain weights, POI opportunity weights, and 60-minute cutoff are identical to the MAI calculation. Origins with no reachable weighted destination receive the 60-minute cutoff. For Network B, timing uses the 2018 GTFS stop-proximity proxy; for Network C, timing uses pseudo-GTFS stop routing with access walk, wait, line-haul, and egress components. The pipeline writes `moto_mean_opp_time_min`, `wt_A_mean_opp_time_min`, and `wt_B_mean_opp_time_min` for auditability.

`MAI_transit_i` is the composite metropolitan opportunity score by walk-and-transit; `MAI_motorcycle_i` is the same composite computed over the motorcycle network, using identical domain weights and decay. Each raw subcomponent is min-max normalized, and the composite is their geometric mean:

```text
RAC_i = sqrt(RAC_time_i * RAC_opp_i)
```

The geometric mean is intentional: a service that is fast but reaches few opportunities, or reaches many but slowly, should not score as strongly competitive. Both subcomponents must be high for RAC to be high.

### 5.5 Motorcycle Network Calibration

Motorcycles in Hanoi are frequently faster than cars in congestion because of lane-splitting, so Network D must not assume car-equivalent speeds (Khuat, 2006). Per-road-class motorcycle speeds are calibrated from Vietnamese-specific literature: JICA HAIDEP (2010) for arterial and ring-road speeds, Nguyen & Nguyen (2018) for primary/secondary urban streets, and Vu Anh Tuan et al. (2016) for tertiary and residential streets. Manual Android Google Maps checks provide a plausibility validation rather than the primary calibration source.

### 5.6 Sustainable Mobility Capability Index (SMCI)

SMCI is multiplicative: a weakest-link index.

```text
SMCI_i = NAI_norm_i * MAI_norm_i * RAC_norm_i
```

A cell scores high only if it has local walkability, metropolitan access, and competitive sustainable mobility simultaneously; strength in one dimension cannot compensate for near-absence in another. Scenario comparisons use shared A+B normalization bounds throughout so that Delta_SMCI is a clean scenario difference.

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

### 6.1 The Intervention Improves Capability, But Zero-Access Cells Must Be Separated

Across 462 cells, the VinBus scenario raises mean SMCI from **0.0322 (Scenario A) to 0.0435 (Scenario B)**, a mean Delta_SMCI of **+0.0113**. The global mean is not the primary interpretive statistic because the multiplicative SMCI is zero-inflated: if NAI, MAI, or RAC is zero, SMCI is zero. We therefore report zero-access cells separately and compute distributional summaries for cells with positive capability.

The improvement is broad but spatially uneven: **298 cells (64.5%) improve, 88 are unchanged, and 76 decline slightly** once the RAC_time component is defined as an opportunity-weighted travel-time ratio. The unchanged cells are primarily zero-access cells. Declines are interpreted cautiously: VinBus increases opportunity access for many cells, but the time-competitiveness term can fall where additional reachable opportunities have longer weighted walk-transit times than the motorcycle benchmark.

**Table 3. Pilot summary (Scenario B unless noted).**

| Metric | Value |
|---|---:|
| Grid cells | 462 |
| Mean SMCI, Scenario A | 0.0322 |
| Mean SMCI, Scenario B | 0.0435 |
| Mean Delta_SMCI | 0.0113 |
| Cells improved / unchanged / declined | 298 / 88 / 76 |
| Share improved | 64.5% |
| Zero-NAI cells | 88 (19.0%) |
| Positive-cell median SMCI, Scenario A | 0.0197 |
| Positive-cell median SMCI, Scenario B | 0.0220 |

Among cells with positive SMCI, the median rises from **0.0197** in Scenario A to **0.0220** in Scenario B. This confirms that the change is not only a mean effect caused by a few high-access cells. The unchanged group is also substantively meaningful: these are cells where adding metropolitan transit access does not overcome missing neighborhood walking access or very weak local opportunity structure.

### 6.2 Spatial Fragmentation Persists Under the Intervention

Even with VinBus, the Scenario B typology is sharply divided (Table 4). **166 cells (35.9%) remain in Motorcycle Lock-in**, exactly matching the 166 cells in Integrated Capability, with 65 cells each in the Fragmented and Transit-Dependent types. For comparison, Scenario A places 155 cells each in Integrated and Motorcycle Lock-in and 76 each in the intermediate types; the intervention relabels **84 of 462 cells** (18.2%).

**Table 4. Typology distribution by scenario.**

| Typology | Scenario A (cells) | Scenario B (cells) | Scenario B (% cells) |
|---|---:|---:|---:|
| Integrated Capability | 155 | 166 | 35.9% |
| Fragmented Capability | 76 | 65 | 14.1% |
| Transit-Dependent | 76 | 65 | 14.1% |
| Motorcycle Lock-in | 155 | 166 | 35.9% |

The persistence of a large Motorcycle Lock-in class under the intervention is the central substantive finding: a green megaproject with a functioning electric-bus network still leaves more than a third of its grid in a condition where neither local access nor transit competitiveness is strong.

### 6.3 Population Exposure: The Equity Reading Is Slightly Worse Than the Cell Average

Cell averages still require an exposure check. Using WorldPop 2020 (estimated study-area population approximately 78,816; all 462 cells non-zero), the **population-weighted mean SMCI_B is 0.0423 versus the unweighted 0.0435**, a small downward bias of 2.7%. The rank correlation between cell population and SMCI_B is near zero (Spearman rho = -0.017, p = 0.711), so population is roughly evenly spread across capability levels.

By population share, the **Motorcycle Lock-in type houses the largest resident group at 33.4%**, ahead of Integrated Capability (31.1%), Fragmented Capability (19.6%), and Transit-Dependent (16.0%). The largest single group of residents therefore lives where sustainable mobility capability is weakest, even though the population-weighted and unweighted means are close.

### 6.4 Zero-Access Cells Are Genuinely Built and Populated

The pilot has **88 zero-NAI cells (19.0%)**, and the same 88 cells have SMCI_B = 0 because the index is multiplicative. This is not a lake-and-park artifact: VIDA building footprints are present in **455 of 462 cells (98.5%)**, and **84 of the 88 zero-NAI cells are built**, housing about **11,798 residents (15.0% of the pilot population)**. Zero inflation thus reflects under-served built-up areas, which is a substantive caution for interpretation rather than a data error. These cells should be reported as a separate zero-access category rather than absorbed into the lowest positive quantile.

### 6.5 Robustness

**Headway assumptions (Network C).** VinBus route data provide observed per-route headways for most routes, with a fallback headway used only where route frequencies are absent. Sensitivity tests show that fallback-headway choices do not materially alter the study-area classification: **the typology partition is invariant (Cohen's kappa = 1.00)** across the tested fallback scenarios.

**Structural multicollinearity (MAI vs. RAC).** Because RAC_opp shares its numerator (MAI_transit) with MAI, the two are collinear by construction. In the primary specification VIF is high (NAI 2.67, MAI 8.21, RAC 7.90). Replacing the full RAC composite with RAC_time alone removes the shared term and brings both within the conventional threshold (MAI 3.25, RAC_time 1.86). The typology agreement between the primary and RAC_time-only specifications is **Cohen's kappa = 0.900 (32 of 462 cells relabelled)**. The full-RAC specification is retained as primary, with RAC_time-only reported as a robustness disclosure.

**Motorcycle speed sensitivity.** Three Network D calibration scenarios were tested. Slower congested motorcycle speeds raise mean SMCI_B to 0.0486; faster lane-splitting lowers it to 0.0410. Typology agreement remains near-perfect in both cases (**kappa = 0.994; 2 of 462 cells relabelled**), indicating that the classification is not driven by a narrow motorcycle-speed assumption.

**Transit impedance sensitivity.** Behavioral penalties were applied only to walk-transit travel times, leaving MAI opportunity weights unchanged. Conservative penalties reduce mean SMCI_B to 0.0342 and pessimistic penalties to 0.0269; typology agreement remains high (**kappa = 0.933 and 0.890**, respectively). This is a behavioral-realism sensitivity, not observed mode-choice validation.

**Supply-side population weighting.** Adding the WorldPop-derived supply-side multiplier to MAI relabels only 8 of 462 cells relative to the no-population baseline (**kappa = 0.976**). Population weighting therefore improves the defensibility of opportunity magnitudes without driving the typology result.

**Index form.** Against an additive alternative SMCI_add = (NAI_norm + MAI_norm + RAC_norm)/3, the multiplicative SMCI ranking holds strongly but not trivially. A geometric-mean alternative is deliberately not used as a robustness check, because it is a monotonic transform of the product and would yield rho = 1.0 by construction.

**RAC normalization.** Comparing plain min-max against log(1+x) followed by min-max normalization of the RAC subcomponents yields identical typologies (kappa = 1.00) and near-identical SMCI rankings (rho = 0.9999), confirming insensitivity to the modest right-skew of RAC.

### 6.6 Validation

**Motorcycle travel times.** Ten named origin-destination pairs measured manually in the Android Google Maps app give a mean absolute error of **1.90 minutes** and a bias of **-1.04 minutes**, i.e., the calibrated model is slightly optimistic relative to the consumer app. This is a plausibility check; calibrated network times remain the primary basis because Google TWO_WHEELER API coverage for Vietnam is not relied upon.

**POI quality.** A 20-record spot-check of the initial POI layer found 14 confirmed, 2 duplicates, 2 misclassifications, and 2 missing. The 55 Overture-only POIs were separately spot-checked at 100% confirmation before promotion of the merged layer. Economic-domain enrichment is reported as a strengthened open-data proxy, not as direct employment measurement.

---

## 7. Discussion

**Local walkability is not sustainable mobility capability.** The pilot operationalizes, and then empirically separates, two capabilities that are routinely conflated. Ocean Park performs reasonably on neighborhood access in many cells, yet 64.1% of cells fall outside Integrated Capability and 35.9% remain in Motorcycle Lock-in even with VinBus. The framework's value is its ability to make this gap visible and locable.

**The benchmark mode matters.** Standard transport models benchmark transit against the car. Doing so in Hanoi would overstate transit competitiveness, because the car is slower than the motorcycle in congestion. By benchmarking against the motorcycle, RAC reframes the question from "does a bus exist?" to "would a rational motorcyclist switch?", a more demanding and more policy-relevant test.

**Transit alone is not enough.** VinBus improves almost two-thirds of the grid, but it does not dissolve motorcycle advantage. The unchanged group, the declined time-competitiveness cells, and the zero-access built cells show that metropolitan transit provision cannot substitute for local opportunity structure and fine-grained pedestrian connectivity. Transit provision must therefore be coupled with land-use integration, not treated as a standalone fix, and the equity dimension should be central because the largest resident group sits in the weakest typology.

**Zero access is analytically different from low access.** The maps and result tables should not place cells with value 0.0 into the same color class as low positive cells. Zero access means one component of capability is absent; low positive access means capability exists but is weak. This distinction is central to the interpretation of a weakest-link index.

**Transferability.** The framework requires open data plus literature-calibrated mode speeds. It is therefore portable to other motorcycle-dependent cities, such as Ho Chi Minh City, Bangkok, Jakarta, and Bengaluru, where the car-benchmark assumption similarly fails.

---

## 8. Limitations

This is a single-site pilot; the goal is framework development and feasibility, not citywide or national generalization. The 462-cell extent covers Ocean Park and a 2 km buffer only.

The metropolitan index remains proxy-based. Economic enrichment and supply-side population weighting improve the opportunity layer, but the paper still does not observe employment counts, enrollment counts, or service capacities directly. MAI should therefore be read as a capacity-scaled opportunity index grounded in open spatial proxies, not as a census of jobs or seats.

Transit data are imperfect. Network B is a 2018 pre-VinBus baseline, deliberately retained as the pre-intervention conventional-transit benchmark. Network C uses a pseudo-GTFS layer constructed from the VinBus public API. It is not a fully scheduled timetable feed, though route headway and stop data are strong enough for the stop-level routing used here.

Structural multicollinearity between MAI and RAC is inherent to the design; it is disclosed and bounded via the RAC_time-only specification (kappa = 0.900) rather than eliminated.

Mode and impedance specifications omit behaviorally salient details such as fares, parking, transfer penalties, access/egress discomfort, and schedule unreliability. The transit-impedance sensitivity partially bounds this issue, but it does not replace observed mode-choice or reliability data.

Motorcycle validation is limited to 10 manual OD pairs, appropriate for pilot plausibility but not a full calibration dataset. No observed mode shares, travel diaries, or revealed commute times are used to validate the capability typology externally.

The VinBus pseudo-GTFS creates an ethics and replicability risk. The source API is public and contains no personal data, but licensing and terms-of-service uncertainty remain. Derived route tables should be replaced with official GTFS if VinBus publishes one.

---

## 9. Conclusion

We have developed and piloted a dual-scale, mode-competitive accessibility framework that distinguishes neighborhood access, metropolitan access, and, critically, competitiveness against the motorcycle rather than the car. Applied to Vinhomes Ocean Park, the framework shows that an electric-bus-branded green megaproject improves sustainable mobility capability on average (mean SMCI 0.0322 to 0.0435; 64.5% of cells improved) while leaving a persistent Motorcycle Lock-in condition that covers 35.9% of cells and 33.4% of residents. The more important result is distributional: 19.0% of cells remain at zero walking access, and 95.5% of those zero-access cells are built. The findings are robust to motorcycle-speed assumptions, transit-impedance penalties, normalization choices, and a multicollinearity-corrected specification. The framework is open, reproducible, and transferable to the many cities where the realistic alternative to transit is two wheels, not four. Full citywide application is the next step.

---

## References

Geurs, K. T., & van Wee, B. (2004). Accessibility evaluation of land-use and transport strategies: Review and research directions. *Journal of Transport Geography, 12*(2), 127-140. https://doi.org/10.1016/j.jtrangeo.2003.10.005

Handy, S. L., & Niemeier, D. A. (1997). Measuring accessibility: An exploration of issues and alternatives. *Environment and Planning A, 29*(7), 1175-1194. https://doi.org/10.1068/a291175

Japan International Cooperation Agency (JICA). (2010). *The comprehensive urban development programme in Hanoi capital city (HAIDEP)*. JICA / Hanoi People's Committee.

Kaszczyszyn, P., & Sypion-Dutkowska, N. (2019). Walking access to public transport stops for city residents: A comparison of methods. *Sustainability, 11*(14), 3758. https://doi.org/10.3390/su11143758

Khuat, V. H. (2006). *Traffic management in motorcycle dependent cities* (Doctoral dissertation). Darmstadt University of Technology.

Liao, Y., Gil, J., Pereira, R. H. M., Yeh, S., & Verendel, V. (2020). Disparities in travel time between car and transit: Spatiotemporal patterns in cities. *Scientific Reports, 10*, 4056. https://doi.org/10.1038/s41598-020-61077-0

Moreno, C., Allam, Z., Chabaud, D., Gall, C., & Pratlong, F. (2021). Introducing the "15-Minute City": Sustainability, resilience and place identity in future post-pandemic cities. *Smart Cities, 4*(1), 93-111. https://doi.org/10.3390/smartcities4010006

Nguyen, X. L., & Nguyen, H. T. (2018). Operating speed of motorcycles on urban streets in Hanoi. *Journal of the Eastern Asia Society for Transportation Studies, 12*, 1421-1435.

Vu Anh Tuan. (2015). Mode choice behavior and modal shift to public transport in developing countries: The case of Hanoi city. *Journal of the Eastern Asia Society for Transportation Studies, 11*, 473-487.

Vu Anh Tuan, Nguyen, H., & Pham, T. (2016). Motorcycle traffic characteristics in Hanoi. *Transportation Research Procedia, 15*, 651-662.

---

*Data, code, formulas, and validation outputs are maintained in the project repository (`src/`, `outputs/`, `docs/`). All indices are implemented and unit-tested in `src/accessibility.py` and the pipeline test suite (70 passing tests). Pilot results derive from `data/processed/pilot_metrics.csv`.*

> **Reference-verification note (delete before submission).** The following citations were confirmed against live sources during drafting: Geurs & van Wee (2004), Handy & Niemeier (1997), Moreno et al. (2021), Liao et al. (2020), and the Vietnamese motorcycle-speed sources used in calibration (JICA HAIDEP 2010; Nguyen & Nguyen 2018; Vu Anh Tuan et al. 2016). The following should be re-verified for exact volume/page/DOI before submission: Kaszczyszyn & Sypion-Dutkowska (2019), Khuat (2006), and Vu Anh Tuan (2015).

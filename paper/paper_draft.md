# Fragmented Mobility Capability in a Motorcycle-Dependent Green Megaproject: A Dual-Scale, Mode-Competitive Accessibility Framework from Vinhomes Ocean Park, Hanoi

**Author:** Cuki2910
**Target journal:** *Journal of Transport Geography*
**Article type:** Methods development and pilot validation
**Draft date:** 2026-06-24 (updated: merged POI layer promoted to primary)

---

## Abstract

Green-branded megaprojects in Southeast Asia are increasingly promoted as sustainable alternatives to dispersed, motorcycle-dependent urban growth. Yet conventional accessibility metrics evaluate such projects either at the neighborhood scale (walkability, the "15-minute city") or at the metropolitan scale (cumulative-opportunity job access), and almost always benchmark public transport against the *private car*. In motorcycle-dependent cities, where the practical alternative to transit is the motorcycle rather than the car, both choices misrepresent the lived constraint on sustainable mobility. This paper develops and pilots a dual-scale, mode-competitive accessibility framework that (i) separates neighborhood-scale walking access from metropolitan-scale walk-and-transit access, and (ii) introduces a **Relative Accessibility Competitiveness (RAC)** term that benchmarks walk-and-transit performance directly against motorcycle performance. The three components are combined into a multiplicative **Sustainable Mobility Capability Index (SMCI)** and a theory-first four-way spatial typology. We pilot the framework on Vinhomes Ocean Park, Hanoi — a 250+ ha electric-bus-branded development — across 462 grid cells of 250 m, using OpenStreetMap walking and driving networks, a merged OpenStreetMap + Overture Maps point-of-interest layer, a 2018 pre-VinBus GTFS baseline, OpenStreetMap VinBus route geometry, VIDA building footprints, and WorldPop 2020 population, with motorcycle travel times calibrated from Vietnamese-specific speed literature and validated against manual Google Maps measurements (mean absolute error 1.90 minutes). The VinBus intervention raises mean SMCI from 0.045 to 0.092 and improves 288 of 462 cells (62.3%) with zero declines, yet 167 cells (36.1%) remain in a *Motorcycle Lock-in* typology housing 34.2% of the estimated population. Findings are robust to headway assumptions (typology Cohen's κ = 1.00 across 10–30 minute headways) and to a RAC_time-only specification addressing structural multicollinearity (κ = 0.871). The pilot demonstrates that local walkability and competitive sustainable mobility are distinct, separately measurable capabilities, and that a green megaproject can deliver the former while failing to deliver the latter.

**Keywords:** accessibility; mode competition; motorcycle dependence; sustainable mobility; green megaprojects; Hanoi; Vietnam

---

## 1. Introduction

Sustainable mobility is commonly equated with two things that are, in practice, distinct: living near everyday destinations, and being able to reach the wider city without a private vehicle. The first is the logic of walkability indices and the "15-minute city" (Moreno et al., 2021). The second is the logic of cumulative-opportunity accessibility, which counts the jobs or services reachable within a travel-time threshold (Handy & Niemeier, 1997; Geurs & van Wee, 2004). Both framings are valuable, but each, used alone, can mislead. A neighborhood may be highly walkable yet poorly connected to metropolitan opportunity; conversely, a cell with good metropolitan transit access may sit in a locally barren environment.

A second, more specific limitation applies to motorcycle-dependent cities. The accessibility-and-mode-choice literature consistently frames the competitiveness of public transport relative to the **private car**, typically through a transit-to-car travel-time or opportunity ratio (e.g., Liao et al., 2020; Kaszczyszyn & Sypion-Dutkowska, 2019). In Hanoi this benchmark is the wrong one. Motorcycles account for over 80% of trips in the city (Vu Anh Tuan, 2015), are faster than cars in congested conditions because of lane-splitting, and are deeply embedded in household routines. A transit service that would be "competitive with the car" can remain entirely uncompetitive with the motorcycle, which is the mode residents actually weigh it against.

This matters for the evaluation of **green megaprojects** — large, master-planned, environmentally branded developments that are proliferating across Vietnam and the wider region. Their sustainability claims rest partly on internal amenities and partly on new transit provision (such as the electric VinBus network at our study site). But if the relevant counterfactual is the motorcycle, then neither "amenities within walking distance" nor "a bus line exists" is sufficient evidence that the development produces sustainable mobility capability.

We therefore ask: **Does a green-branded development produce sustainable mobility capability when everyday life remains organized around the motorcycle?** We answer it by building a framework that (1) measures neighborhood access and metropolitan access on separate scales; (2) adds a mode-competition term benchmarked against the motorcycle, not the car; and (3) combines these into a single weakest-link index and an interpretable spatial typology. We then validate the framework with a full pilot implementation at Vinhomes Ocean Park, Hanoi.

The contribution is primarily methodological: a transferable, reproducible accessibility framework for the roughly 1.5 billion people in motorcycle-dependent regions of Southeast Asia, South Asia, and Latin America. The pilot is a feasibility and validation exercise, not a final citywide result.

---

## 2. Related Work and Contribution

**Neighborhood-scale accessibility.** Walkability scores and the 15-minute-city concept measure local proximity to daily destinations (Moreno et al., 2021). They capture an important dimension of sustainable urbanism but are, by construction, blind to metropolitan-scale inequality: a cell can be locally complete yet metropolitanly isolated.

**Metropolitan-scale accessibility.** Cumulative-opportunity and gravity-based measures count opportunities reachable within a travel-time budget (Handy & Niemeier, 1997; Geurs & van Wee, 2004). The 30-minute threshold is a standard convention in regional accessibility planning. These measures capture metropolitan reach but, when reported as a single citywide surface, can mask neighborhood-level exclusion.

**Mode-competitive accessibility.** A smaller literature frames transit performance *relative* to the competing mode, usually the private car, via travel-time or opportunity ratios (Liao et al., 2020; Kaszczyszyn & Sypion-Dutkowska, 2019). This is the closest precedent to our approach, and we adopt its central insight — that absolute accessibility is less behaviorally meaningful than accessibility relative to the realistic alternative.

**Our contribution** combines three elements that, to our knowledge, have not been integrated in a single framework:

| Existing framing | Limitation | Representative sources |
|---|---|---|
| Walkability / 15-minute city | Local only; ignores metropolitan-scale inequality | Moreno et al. (2021) |
| Citywide cumulative-opportunity access | Aggregate; masks neighborhood exclusion | Handy & Niemeier (1997); Geurs & van Wee (2004) |
| Transit competitiveness vs. the **car** | Wrong benchmark in motorcycle-dependent cities | Liao et al. (2020); Kaszczyszyn & Sypion-Dutkowska (2019) |

Specifically, we (1) separate the neighborhood and metropolitan scales rather than collapsing them; (2) make mode competition explicit through the RAC term; and (3) benchmark against the **motorcycle**, the empirically dominant mode in our setting (Vu Anh Tuan, 2015; Khuat, 2006).

---

## 3. Study Area

The case study is **Vinhomes Ocean Park** in Gia Lam district, on the eastern edge of Hanoi. It is a master-planned development exceeding 250 ha, marketed around environmental quality and served by an electric bus network (VinBus). The site is analytically useful precisely because it combines strong green branding and internal amenities with continued exposure to Hanoi's motorcycle-oriented travel environment — the tension this framework is designed to detect.

The analysis uses a **250 m grid** covering Ocean Park and an approximately 2 km buffer, yielding **462 grid cells**. This resolution distinguishes intra-development variation while remaining computationally tractable for network-based routing. The pilot extent is deliberately bounded; citywide application is future work (Section 8).

---

## 4. Data

All data are open or manually collected. Table 1 summarizes sources and status.

**Table 1. Data sources.**

| Source | Role | Status in pilot |
|---|---|---|
| OpenStreetMap walking network | Network A; NAI routing | 6,846 nodes / 20,024 edges |
| OpenStreetMap driving network | Network D (motorcycle) base | 1,401 nodes / 3,408 edges |
| OpenStreetMap + Overture Maps POIs | Neighborhood and metropolitan opportunities | Merged layer: 161 POIs (7 in both sources, 99 OSM-only, 55 Overture-only) |
| 2018 Hanoi GTFS (World Bank, CC-BY 4.0) | Network B pre-VinBus transit baseline | 224 routes; 7,670 stops; service dates 2018 |
| VinBus official API (vbcore-api.vinbus.vn) | Network C VinBus stops + schedule | 176 routes; 5,631 stops with GPS coordinates; per-route observed headway 5–48 min (mean 16.2 min, median 15.0 min); pseudo-GTFS layer (routes.txt, stops.txt, stop_times.txt, frequencies.txt) |
| VIDA building footprints | Built-cell mask; population cross-check | 41,816 footprints at confidence ≥ 0.70 |
| WorldPop 2020 raster | Population exposure cross-check | ~92.77 m resolution; adequate for 250 m grid |
| Manual Google Maps motorcycle checks | Network D validation | 10 named origin–destination pairs |
| Motorcycle speed calibration | Network D speeds | JICA HAIDEP (2010); Nguyen & Nguyen (2018); Vu Anh Tuan et al. (2016) |

**Data provenance and caveats.**

The **2018 GTFS feed predates the commercial launch of VinBus (September 2021)** and is therefore used deliberately as the *pre-intervention* conventional-transit baseline (Network B), not as current service. Stop geometry is used for stop-level accessibility; timetable frequency is treated only as a relative-magnitude proxy. Maintained GTFS catalogs (MobilityDatabase, TUMI Datahub) were checked; MobilityDatabase returned no Hanoi feed, and TUMI Hanoi candidates require license and service-date verification and are reserved for future current-service sensitivity analysis.

**VinBus (Network C) data are sourced from the publicly accessible VinBus route-query API** (maps.vinbus.vn; backend: vbcore-api.vinbus.vn). Because VinBus does not publish an official GTFS feed, we constructed a pseudo-GTFS layer by reverse-engineering the application's JSON endpoints, which return AES-256-CBC-encrypted payloads decryptable with the key issued by the same API. The complete Hà Nội network was extracted: 176 routes, 5,631 unique stop nodes with official GPS coordinates, 19,625 ordered stop-sequence records across both travel directions, and per-route published headway data for 160 routes (frequencies.txt). Headways range from 5 to 48 minutes (mean 16.2 min, median 15.0 min), replacing the previously assumed uniform 15-minute baseline used in earlier drafts. Stop coordinates were cross-validated against OSM VinBus platform nodes (spatial join at 200 m threshold). Network C is therefore a stop-level *intervention-routing* scenario with per-route observed headway and network-routed bus-speed assumptions (Section 5.3), not a fully scheduled transit assignment. Sensitivity to the bus-speed assumption is tested directly (Section 6.3).

**The POI layer merges OpenStreetMap and Overture Maps, and incorporates building footprint area scaling to represent opportunity size.** A source-agreement audit was applied: 55 Overture-only POIs were spot-checked and all 55 were confirmed, passing the promotion gate, so the merged layer (161 POIs: 7 in both sources, 99 OSM-only, 55 Overture-only) is the primary POI input. To represent opportunity scale, POI locations were matched to building footprint geometries (150/161 POIs, 93% matched within 25 m). Opportunity weights are scaled dynamically based on the building footprint area, proxying student capacities for schools, bed counts for healthcare facilities, and office sizes for economic/employment nodes. These physical-scale enhancements upgrade the index from a simple presence/absence proxy to a proxy-enhanced capacity-scaled framework.

**WorldPop is used as a post-hoc population-exposure cross-check**, evaluating SMCI exposure against population density (Spearman ρ = -0.0413, bias -7.9% for pop-weighted SMCI_B). Gridded population statistics are reported in validation sections to verify spatial equity and capability distribution across typologies.

---

## 5. Methods

The framework is implemented in tested Python (`src/accessibility.py`; 45 passing unit tests). All formulas below are the single source of truth as implemented in code.

### 5.1 Networks and scenarios

Four networks are defined:

- **Network A — walking:** access to nearby neighborhood opportunities on foot.
- **Network B — walking + existing transit:** 2018 pre-VinBus GTFS baseline.
- **Network C — walking + existing transit + VinBus:** stop-level VinBus routing using official API data (176 routes, 5,631 stops, per-route observed headway from published frequencies).
- **Network D — motorcycle:** OSM driving network calibrated to motorcycle speeds (Section 5.5).

Two scenarios are compared. **Scenario A** uses Networks A + B (no VinBus). **Scenario B** uses Networks A + C (with VinBus). Network D is the competitiveness benchmark in both. The intervention effect is ΔSMCI = SMCI(B) − SMCI(A), computed on **shared A+B normalization bounds** so that the difference reflects real scenario change rather than re-scaling artifacts.

### 5.2 Neighborhood Accessibility Index (NAI)

NAI is a count of qualifying POIs reachable on the walking network within the neighborhood threshold:

```text
NAI_i = count of qualifying POIs reachable by walking from cell i within the neighborhood threshold
```

A simple count — not a gravity or decay function — is used deliberately: at the neighborhood scale, the *presence* of a school, clinic, shop, or park is more behaviorally relevant than its precise distance or capacity. NAI is min–max normalized to NAI_norm for index construction.

### 5.3 Metropolitan Accessibility Index (MAI)

MAI is a composite **Metropolitan Opportunity Accessibility** score across four domains, by walking plus transit. It is framed as opportunity accessibility rather than employment accessibility because building-resolution employment data are unavailable for Hanoi (Geurs & van Wee, 2004).

```text
MAI_i = 0.40·A_econ + 0.20·A_edu + 0.20·A_health + 0.20·A_commerce
```

For each domain k:

```text
A_{i,k} = Σ_j ( opportunity_weight_{j,k} · f(t_ij) )
```

with a thresholded linear time-decay function:

```text
f(t) = 1                if t ≤ 30 min
     = (60 − t) / 30    if 30 < t ≤ 60 min
     = 0                if t > 60 min
```

The 30-minute full-value threshold follows standard cumulative-opportunity practice (Handy & Niemeier, 1997); the linear taper to 60 minutes is an interpretable middle ground between a hard binary cutoff and a full gravity specification. Sensitivity runs use equal weights (0.25 each) and a job-heavy specification (0.50/0.15/0.15/0.20). MAI is min–max normalized to MAI_norm.

### 5.4 Relative Accessibility Competitiveness (RAC)

RAC measures whether walking-and-transit access is competitive with motorcycle access. It has two subcomponents — a time ratio and an opportunity ratio:

```text
RAC_time_raw_i = motorcycle_travel_time_i / walk_transit_travel_time_i
RAC_opp_raw_i  = MAI_transit_i / MAI_motorcycle_i
```

`MAI_transit_i` is the composite metropolitan opportunity score by walk-and-transit (Section 5.3); `MAI_motorcycle_i` is the **same composite computed over the motorcycle network**, using identical domain weights and decay function so the ratio is dimensionally consistent. Each raw subcomponent is min–max normalized, and the composite is their geometric mean:

```text
RAC_i = sqrt( RAC_time_i · RAC_opp_i )
```

The geometric mean is intentional: a service that is fast but reaches few opportunities, or reaches many but slowly, should not score as strongly competitive. Both subcomponents must be high for RAC to be high.

Note that benchmarking the opportunity term against `MAI_motorcycle` — rather than the car — is the framework's core methodological move. In a motorcycle-dependent city this is the behaviorally relevant comparison (Vu Anh Tuan, 2015).

### 5.5 Motorcycle network calibration

Motorcycles in Hanoi are frequently *faster* than cars in congestion because of lane-splitting, so Network D must not assume car-equivalent speeds (Khuat, 2006). Per-road-class motorcycle speeds are calibrated from Vietnamese-specific literature: JICA HAIDEP (2010) for arterial and ring-road speeds, Nguyen & Nguyen (2018) for primary/secondary urban streets, and Vu Anh Tuan et al. (2016) for tertiary and residential streets. Calibrated speeds range from ~45 km/h on motorways to ~9 km/h on living streets, with lane-splitting multipliers applied to lower-class streets where gap-exploitation is feasible.

### 5.6 Sustainable Mobility Capability Index (SMCI)

The SMCI is multiplicative — a weakest-link index:

```text
SMCI_i = NAI_norm_i · MAI_norm_i · RAC_norm_i
```

A cell scores high only if it has local walkability, metropolitan access, **and** competitive sustainable mobility simultaneously; strength in one dimension cannot compensate for near-absence in another. Scenario comparisons use shared A+B normalization bounds throughout (MAI, RAC subcomponents, RAC composite, and SMCI components) so that ΔSMCI is a clean scenario difference.

### 5.7 Typology

Each cell is classified by a **theory-first** two-axis split rather than by unsupervised clustering, so that the four conceptual types are guaranteed. First a Metropolitan Competitiveness Score is computed:

```text
MCS_i = sqrt( MAI_norm_i · RAC_norm_i )
```

Cells are then split on rank-based medians of NAI and MCS. Rank-based (not value-based) medians are used so that the four-way partition is preserved even when MCS has a mass point at zero.

**Table 2. Typology definitions.**

| NAI | MCS | Typology | Interpretation |
|---|---|---|---|
| High | High | Integrated Capability | Local access and metropolitan competitiveness both present |
| High | Low | Fragmented Capability | Locally walkable but metropolitan sustainable mobility weak |
| Low | High | Transit-Dependent | Metropolitan access despite weak local access |
| Low | Low | Motorcycle Lock-in | Neither local access nor transit competitiveness strong |

---

## 6. Results

### 6.1 The intervention improves capability but does not transform it

Across 462 cells, the VinBus intervention raises mean SMCI from **0.045 (Scenario A) to 0.092 (Scenario B)**, a mean ΔSMCI of **+0.047**. The improvement is broad but not universal: **288 cells (62.3%) improve, 174 are unchanged, and none decline.** The absence of declines follows directly from the shared A+B normalization: a cell that gains VinBus stop access in Scenario B cannot score below its Scenario A value on a common scale.

**Table 3. Pilot summary (Scenario B unless noted).**

| Metric | Value |
|---|---:|
| Grid cells | 462 |
| Mean SMCI, Scenario A | 0.045 |
| Mean SMCI, Scenario B | 0.092 |
| Mean ΔSMCI | 0.047 |
| Cells improved / unchanged / declined | 288 / 174 / 0 |
| Share improved | 62.3% |
| Zero-NAI cells | 116 (25.1%) |

The roughly two-fold rise in mean SMCI confirms that VinBus delivers real accessibility gains, but the absolute levels remain low: most cells stay in the lower range of the index.

### 6.2 Spatial fragmentation persists under the intervention

Even with VinBus, the Scenario B typology is sharply divided (Table 4). **167 cells (36.1%) remain in Motorcycle Lock-in**, exactly matching the 167 cells in Integrated Capability, with 64 cells each in the Fragmented and Transit-Dependent types. For comparison, Scenario A (no VinBus) places 125 cells each in Integrated and Motorcycle Lock-in and 106 each in the intermediate types; the intervention relabels **162 of 462 cells** (35.1%), predominantly upgrading intermediate cells toward Integrated Capability.

**Table 4. Typology distribution by scenario.**

| Typology | Scenario A (cells) | Scenario B (cells) | Scenario B (% cells) |
|---|---:|---:|---:|
| Integrated Capability | 125 | 167 | 36.1% |
| Fragmented Capability | 106 | 64 | 13.9% |
| Transit-Dependent | 106 | 64 | 13.9% |
| Motorcycle Lock-in | 125 | 167 | 36.1% |

The persistence of a large Motorcycle Lock-in class under the intervention is the central substantive finding: a green megaproject with a functioning electric-bus network still leaves more than a third of its grid in a condition where neither local access nor transit competitiveness is strong.

### 6.3 Population exposure: the equity reading is worse than the cell average

Cell averages understate the lived experience. Using WorldPop 2020 (estimated study-area population ≈ 78,816; all 462 cells non-zero), the **population-weighted mean SMCI_B is 0.083 versus the unweighted 0.092 — a downward bias of 10.3%.** The rank correlation between cell population and SMCI_B is weakly negative (Spearman ρ = −0.050, p = 0.288), i.e., population is roughly evenly spread across capability levels with no compensating concentration in high-SMCI cells.

By population share, the **Motorcycle Lock-in type houses the largest resident group at 34.2%**, ahead of Integrated Capability (31.7%), Fragmented Capability (19.0%), and Transit-Dependent (15.1%). The largest single group of residents therefore lives where sustainable mobility capability is weakest.

### 6.4 Zero-access cells are genuinely residential

A quarter of cells (116; 25.1%) have NAI = 0 and hence SMCI_B = 0. This is not a lake-and-park artifact: VIDA building footprints are present in **455 of 462 cells (98.5%)**, and **112 of the zero-NAI cells are built**, housing about **16,758 residents (21.3% of the pilot population)**. Zero inflation thus reflects genuinely under-served built-up areas, which is a substantive caution for interpretation rather than a data error.

### 6.5 Robustness

**Headway assumptions (Network C).** Because VinBus lacks a public timetable, wait time is modeled as headway/2 under a random-arrival assumption, with a 15-minute baseline headway from published VinBus schedules. Across optimistic (10 min), baseline (15 min), and pessimistic (30 min) headways, mean SMCI_B varies only between 0.094 and 0.097 and the improved-cell share between 46.1% and 52.4%. Critically, **the typology partition is invariant: Cohen's κ = 1.00 against the baseline in all scenarios.** Headway affects magnitudes, not the classification.

**Structural multicollinearity (MAI vs. RAC).** Because RAC_opp shares its numerator (MAI_transit) with MAI, the two are collinear by construction. In the primary specification VIF is high (NAI 2.16, MAI 19.33, RAC 20.21). Replacing the full RAC composite with RAC_time alone removes the shared term and brings both within the conventional threshold (MAI 4.53, RAC_time 3.86). The typology agreement between the primary and RAC_time-only specifications is **Cohen's κ = 0.871 (42 of 462 cells relabelled)**, and all relabelling occurs within NAI tiers — the NAI axis drives the partition. The full-RAC specification is retained as primary, with the RAC_time-only run reported as a robustness disclosure.

**Index form.** Against an additive alternative SMCI_add = (NAI_norm + MAI_norm + RAC_norm)/3, the multiplicative SMCI ranking holds strongly but not trivially: **Spearman ρ = 0.847**. (A geometric-mean alternative is deliberately *not* used as a robustness check, because it is a monotonic transform of the product and would yield ρ = 1.0 by construction.)

**RAC normalization.** Comparing plain min–max against log(1+x)→min–max normalization of the RAC subcomponents yields identical typologies (κ = 1.00) and near-identical SMCI rankings (ρ = 0.9999), confirming insensitivity to the modest right-skew of RAC.

### 6.6 Validation

**Motorcycle travel times.** Ten named origin–destination pairs measured manually in the Android Google Maps app give a mean absolute error of **1.90 minutes** and a bias of **−1.04 minutes**, i.e., the calibrated model is slightly optimistic relative to the consumer app. This is a plausibility check; calibrated network times remain the primary basis (the Google TWO_WHEELER API is not relied upon, as its Vietnam coverage is unconfirmed).

**POI quality.** A 20-record spot-check of the POI layer found 14 confirmed, 2 duplicates, 2 misclassifications, and 2 missing — an adequate pilot uncertainty estimate that is reported rather than concealed. The 55 Overture-only POIs were separately spot-checked at 100% confirmation before promotion of the merged layer.

---

## 7. Discussion

**Local walkability is not sustainable mobility capability.** The pilot operationalizes, and then empirically separates, two capabilities that are routinely conflated. Ocean Park performs reasonably on neighborhood access in many cells, yet roughly 70% of cells fall outside Integrated Capability, and a third remain in Motorcycle Lock-in even with VinBus. The framework's value is precisely its ability to make this gap visible and locable.

**The benchmark mode matters.** Standard transport models benchmark transit against the car. Doing so in Hanoi would overstate transit competitiveness, because the car is slower than the motorcycle in congestion. By benchmarking against the motorcycle, RAC reframes the question from "does a bus exist?" to "would a rational motorcyclist switch?" — a far more demanding and more policy-relevant test.

**Transit alone is not enough.** VinBus never harms accessibility and improves half the grid, but it does not dissolve motorcycle advantage. The benefit concentrates along served corridors and stops; off-corridor residents gain little. The policy implication is that transit provision must be coupled with land-use integration, not treated as a standalone fix — and that the equity dimension (the largest resident group sits in the weakest typology) should be central to evaluation.

**Transferability.** The framework requires only open data (OSM networks and POIs, an open GTFS or route geometry, open building footprints, open population rasters) plus literature-calibrated mode speeds. It is therefore portable to other motorcycle-dependent cities — Ho Chi Minh City, Bangkok, Jakarta, Bengaluru — where the car-benchmark assumption similarly fails.

---

## 8. Limitations

This is a **single-site pilot**; the goal is framework development and feasibility, not citywide or national generalization. The 462-cell extent covers Ocean Park and a 2 km buffer only.

The **metropolitan index is proxy-level.** No university or office/employment nodes exist in the pilot POI set, so the economic domain uses commercial-density proxy and the higher-education domain is zero throughout. Stronger metropolitan claims require integrating employment, enrollment, building, nighttime-light, or population proxies, or explicitly retaining the proxy label.

**Transit data are imperfect.** Network B is a 2018 pre-VinBus baseline, deliberately retained as the pre-intervention conventional-transit benchmark. Network C uses a pseudo-GTFS layer constructed from the VinBus public API (176 routes, 5,631 stops, per-route observed headway); it is not a fully scheduled timetable feed, and bus-speed assumptions remain. Bus-speed sensitivity and the typology robustness check (Section 6.3) show that the typology partition is stable.

**Structural multicollinearity** between MAI and RAC is inherent to the design; it is disclosed and bounded via the RAC_time-only specification (κ = 0.888) rather than eliminated.

**Motorcycle validation is limited** to 10 manual OD pairs — appropriate for pilot plausibility but not a full calibration dataset.

---

## 9. Conclusion

We have developed and piloted a dual-scale, mode-competitive accessibility framework that distinguishes neighborhood access, metropolitan access, and — critically — competitiveness against the motorcycle rather than the car. Applied to Vinhomes Ocean Park, the framework shows that an electric-bus-branded green megaproject meaningfully improves sustainable mobility capability (mean SMCI 0.045 → 0.092; 62.3% of cells improved, none declined) while leaving a persistent Motorcycle Lock-in condition that covers 36.1% of cells and 34.2% of residents. The findings are robust to headway and normalization assumptions and to a multicollinearity-corrected specification. The framework is open, reproducible, and transferable to the many cities where the realistic alternative to transit is two wheels, not four. Full citywide application is the next step.

---

## References

Geurs, K. T., & van Wee, B. (2004). Accessibility evaluation of land-use and transport strategies: Review and research directions. *Journal of Transport Geography, 12*(2), 127–140. https://doi.org/10.1016/j.jtrangeo.2003.10.005

Handy, S. L., & Niemeier, D. A. (1997). Measuring accessibility: An exploration of issues and alternatives. *Environment and Planning A, 29*(7), 1175–1194. https://doi.org/10.1068/a291175

Japan International Cooperation Agency (JICA). (2010). *The comprehensive urban development programme in Hanoi capital city (HAIDEP)*. JICA / Hanoi People's Committee.

Kaszczyszyn, P., & Sypion-Dutkowska, N. (2019). Walking access to public transport stops for city residents: A comparison of methods. *Sustainability, 11*(14), 3758. https://doi.org/10.3390/su11143758

Khuat, V. H. (2006). *Traffic management in motorcycle dependent cities* (Doctoral dissertation). Darmstadt University of Technology.

Liao, Y., Gil, J., Pereira, R. H. M., Yeh, S., & Verendel, V. (2020). Disparities in travel time between car and transit: Spatiotemporal patterns in cities. *Scientific Reports, 10*, 4056. https://doi.org/10.1038/s41598-020-61077-0

Moreno, C., Allam, Z., Chabaud, D., Gall, C., & Pratlong, F. (2021). Introducing the "15-Minute City": Sustainability, resilience and place identity in future post-pandemic cities. *Smart Cities, 4*(1), 93–111. https://doi.org/10.3390/smartcities4010006

Nguyen, X. L., & Nguyen, H. T. (2018). Operating speed of motorcycles on urban streets in Hanoi. *Journal of the Eastern Asia Society for Transportation Studies, 12*, 1421–1435.

Vu Anh Tuan. (2015). Mode choice behavior and modal shift to public transport in developing countries — The case of Hanoi city. *Journal of the Eastern Asia Society for Transportation Studies, 11*, 473–487.

Vu Anh Tuan, Nguyen, H., & Pham, T. (2016). Motorcycle traffic characteristics in Hanoi. *Transportation Research Procedia, 15*, 651–662.

---

*Data, code, formulas, and validation outputs are maintained in the project repository (`src/`, `outputs/`, `docs/`). All indices are implemented and unit-tested in `src/accessibility.py` (45 passing tests). Pilot results derive from `data/processed/pilot_metrics.csv`.*

> **Reference-verification note (delete before submission).** The following citations were confirmed against live sources during drafting: Geurs & van Wee (2004), Handy & Niemeier (1997), Moreno et al. (2021), Liao et al. (2020), and the Vietnamese motorcycle-speed sources used in calibration (JICA HAIDEP 2010; Nguyen & Nguyen 2018; Vu Anh Tuan et al. 2016). The following should be re-verified for exact volume/page/DOI before submission: Kaszczyszyn & Sypion-Dutkowska (2019), Khuat (2006), and Vu Anh Tuan (2015) — these were located by title/author but their full bibliographic details were not independently confirmed in this draft.

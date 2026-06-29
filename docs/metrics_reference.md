# Metrics Reference — Formulas, Thresholds, and Theory Support

Single reference for every metric in the study: what it is, the exact formula, the
thresholds/parameters that define it, the source of truth in code, and the theoretical
framework that justifies it.

This is a **reference document**, not a tutorial. The authoritative implementation is
`src/accessibility.py` (index formulas) and `src/accessibility_inputs.py` /
`src/routing.py` (input construction). If a formula here disagrees with the code, the
code wins — fix this file. Last synced: 2026-06-29 (strict observed MAI, 77 tests).

Convention: cell index `i`, opportunity/POI index `j`, domain index `k`,
travel time `t_ij` in minutes unless stated.

---

## 0. Metric map

| Metric | Scale | Type | Feeds into | Code |
|---|---|---|---|---|
| **NAI** | Neighborhood | Count | SMCI, typology axis 1 | `routing.reachable_counts_and_mean_time` |
| **MAI** | Metropolitan | Magnitude-weighted | RAC_opp, MCS, SMCI | `routing.composite_mai_from_graph` |
| **RAC_time** | Mode-competitive | Time ratio | RAC, RAC_time-only contingency | `accessibility_inputs` (opp-weighted times) |
| **RAC_opp** | Mode-competitive | Opportunity ratio | RAC | `accessibility_inputs._safe_ratio` |
| **RAC** | Mode-competitive | Geometric mean | MCS, SMCI | `accessibility.compute_rac` |
| **MCS** | Composite | Geometric mean | Typology axis 2 | `accessibility.metropolitan_competitiveness_score` |
| **SMCI** | Composite | Multiplicative | Headline result, Δ | `accessibility.compute_smci` |
| **SMCI_additive** | Composite | Additive | Robustness only | `accessibility.compute_smci_additive` |
| **Typology** | Classification | 2×2 rank split | Headline result | `accessibility.theory_first_typology` |

---

## 1. NAI — Neighborhood Accessibility Index

**What it measures.** Local walking access to daily destinations — *presence* of everyday
functions within a walkable catchment.

**Formula.**
```text
NAI_i = | { j : t_ij^walk <= T_walk } |
```
Count of qualifying POIs reachable from cell `i` on the walking network within the
neighborhood time threshold. Count-based, not magnitude-weighted (Decision #7).

**Thresholds / parameters.**
| Parameter | Value | Source |
|---|---|---|
| `T_walk` (neighborhood cutoff) | 15 min (≈800 m walk at 80 m/min) | `build_accessibility_inputs.py --walking-threshold-m 800` |
| Walking speed | 1.333 m/s (80 m/min) | `routing.py` access cutoff |
| Routing | Dijkstra shortest path on OSM walk graph | `routing.reachable_counts_and_mean_time` |

**Why count, not gravity (Decision #7).** At the neighborhood scale the relevant question
is binary-ish — *is there a school / clinic / shop within walking distance?* A kiosk and a
supermarket both satisfy "daily needs nearby," so presence matters more than magnitude. A
gravity/decay weighting here would smuggle metropolitan-scale logic into a local measure.

**Theory support.**
- **15-minute city / walkability** — local proximity to daily destinations as a dimension
  of sustainable urbanism (Moreno et al., 2021). NAI operationalizes the "local completeness"
  axis the framework deliberately separates from metropolitan reach.
- **Cumulative-opportunity accessibility** — counting opportunities within a travel-time
  budget (Handy & Niemeier, 1997). NAI is the count-based, walk-only special case.

---

## 2. MAI — Metropolitan Accessibility Index (Metropolitan Opportunity Accessibility)

**What it measures.** Walking-and-transit access to *metropolitan* opportunities, weighted
by the magnitude of each opportunity. Four domains, fixed domain weights.

**Per-domain access.**
```text
A_i,k = sum_j  w_j,k * f(t_ij)
```
- `w_j,k` = opportunity weight of destination `j` in domain `k` (Section 2.2)
- `f(t)` = time-decay function (Section 2.1)

**Composite.**
```text
MAI_i = 0.40 * A_i,economic
      + 0.20 * A_i,higher_education
      + 0.20 * A_i,tertiary_healthcare
      + 0.20 * A_i,metro_commercial
```

**Two MAI surfaces are computed** with identical domains/weights/decay but different
networks, so they are commensurable for RAC_opp:
- `MAI_transit` — walk + transit network (Network B for Scenario A, Network C for Scenario B)
- `MAI_motorcycle` — Network D (motorcycle)

Source of truth: `accessibility.MAI_DOMAIN_WEIGHTS`, `routing.composite_mai_from_graph`.

### 2.1 Time-decay function f(t)

```text
f(t) = 1                if t <= 30 min          (full weight)
     = (60 - t) / 30   if 30 < t <= 60 min     (linear taper)
     = 0                if t > 60 min           (out of reach)
```
| Parameter | Value | Code |
|---|---|---|
| `t_full` (full weight cutoff) | 30 min | `accessibility.time_decay_linear` |
| `t_zero` (zero cutoff) | 60 min | `accessibility.time_decay_linear` |

Thresholded-linear decay (Decision #12 / #15): full weight to 30 min, linear to zero at
60 min. Chosen over a continuous exponential for transparency and a defensible metropolitan
commuting horizon.

### 2.2 Opportunity weights w_j,k — STRICT OBSERVED (primary, Decision #21)

Each destination's weight is a measured magnitude, converted to a within-domain weight and
**clipped** so no single facility dominates its domain (discipline carried from Decision #18).

```text
healthcare:  w = clip(beds / 50,          0.4, 30.0)
higher_ed:   w = clip(enrollment / 1000,  0.5, 20.0)
economic:    w = clip(jobs / 500,         0.1,  5.0)
commercial:  w = clip(gla_m2 / 1000,      0.1, 25.0)
```

| Domain | Unit | Reference (→ w≈1.0) | Lower cap | Upper cap |
|---|---|---|---|---|
| tertiary_healthcare | staffed beds | 50 (district clinic) | 0.4 | 30.0 |
| higher_education | enrollment | 1000 (secondary school) | 0.5 | 20.0 |
| economic | jobs | 500 (SME cluster) | 0.1 | 5.0 |
| metro_commercial | m² GLA | 1000 | 0.1 | 25.0 |

Source of truth: `accessibility_inputs.OBSERVED_OPPORTUNITY_REFS`.

**Economic ref=500 / cap=5.0 is deliberate.** A 30,000-worker industrial park otherwise hits
the cap and floods the 0.40-weighted economic domain (the #18 failure mode). ref=500 keeps a
typical SME park in [0.1, 1.0] and the cap holds the largest zone at 5.0.

### 2.3 Provenance hierarchy & source tiers

Strict mode (`--opportunity-basis observed_strict`) assigns a magnitude through a strict
hierarchy and **excludes** any included-domain POI with no measurable magnitude (no tag-only
proxy fallback). Tiers, strongest first:

| Tier | Meaning | Pilot count |
|---|---|---:|
| `observed_point` | Named facility, citable count | 2 |
| `official_source` | National standard by facility type (MOET class size, MOH commune beds) | 25 |
| `facility_source` | Facility website/report | 13 |
| `geometry_measured` | Floorspace = footprint × levels × usable fraction | 80 |
| `manual_checked` | Sector-standard estimate, reviewed | 57 |
| `observed_dasymetric_weak` | Employment density × area (areal interpolation) | 23 |
| *excluded* | Point-only service/transport, no magnitude | 8 (not in MAI) |

Source of truth: `accessibility_inputs.OBSERVED_SOURCE_VALUES`, audit trail in
`data/interim/poi_observed_audit.csv`. Schema columns: `obs_magnitude`, `obs_unit`,
`obs_source_tier`, `obs_confidence`, `obs_audit_status`, `include_in_mai`, `exclusion_reason`.

Alternative bases for sensitivity: `--opportunity-basis proxy` (legacy tag/area weights,
regression baseline) and `--opportunity-basis observed` (hybrid: observed where available,
proxy fallback otherwise).

### 2.4 Supply-side population multiplier (Decision #19)

Each opportunity weight is scaled by the residential density of the cell containing it (an
opportunity in a denser catchment serves a larger market):
```text
m_j = clip( sqrt(pop_density_j / median(pop_density>0)), 0.5, 2.0 )
w_eff_j = w_j * m_j
```
| Parameter | Value | Code |
|---|---|---|
| lower bound | 0.5 | `accessibility_inputs.population_supply_multiplier` |
| upper bound | 2.0 | same |
| centering | median of positive densities | same |

`sqrt` damps the signal; median-centering keeps a typical-density opportunity at ~1.0. The
same `w_eff` enters transit and motorcycle MAI so RAC_opp stays consistent. Toggle with
`--no-pop-weighting`. No-pop sensitivity: κ=0.976, 8/462 relabelled.

**Theory support (MAI overall).**
- **Cumulative-opportunity / gravity accessibility** — opportunities reachable within a
  travel-time budget, optionally decay-weighted (Hansen, 1959; Handy & Niemeier, 1997;
  Geurs & van Wee, 2004). MAI is a domain-composite cumulative measure with linear decay.
- **Opportunity-magnitude weighting** — counting "an opportunity" as one unit ignores that a
  hospital ≠ a clinic. Weighting by observed magnitude (jobs, beds, enrollment, GLA) follows
  the supply-side tradition in the cumulative-accessibility literature (Geurs & van Wee, 2004).
- **Place-based, not person-based** — MAI is a reproducible place-based surface; it does not
  observe individual constraints (paper §2). Framed as *opportunity* accessibility, not an
  employment census (Decision #15).

---

## 3. RAC — Relative Accessibility Competitiveness

**What it measures.** Whether walking + transit can *compete with the motorcycle* — the
empirically dominant mode in Hanoi, not the car. The framework's core conceptual contribution.

### 3.1 RAC_time — time competitiveness

```text
RAC_time_raw_i = moto_mean_opp_time_i / walk_transit_mean_opp_time_i
```
Ratio of motorcycle opportunity-weighted mean travel time to walk-transit opportunity-weighted
mean travel time, over the **same** MAI opportunity set, domain weights, POI weights, and
60-min cutoff (Decision #20). Higher = transit time-competitive. Cells with no reachable
weighted destination receive the cutoff.

Audit columns: `moto_mean_opp_time_min`, `wt_A_mean_opp_time_min`, `wt_B_mean_opp_time_min`.

### 3.2 RAC_opp — opportunity competitiveness

```text
RAC_opp_raw_i = MAI_transit_i / MAI_motorcycle_i
```
Ratio of two commensurable composite MAI scores (Decision #15). Higher = transit reaches a
larger share of weighted metropolitan opportunity relative to the motorcycle. Denominator
floored at the 5th percentile of positive `MAI_motorcycle` to prevent blow-up in isolated
drive-graph cells.

### 3.3 RAC composite

```text
RAC_i = sqrt( RAC_time_norm_i * RAC_opp_norm_i )
```
Both sub-indices are min-max normalized on shared Scenario A+B bounds (Section 6), then
combined as a **geometric mean**.

| Parameter | Value | Code |
|---|---|---|
| Combination | geometric mean | `accessibility.compute_rac` |
| Normalization | shared A+B min-max | `accessibility.compute_rac_shared` |
| RAC_opp denominator floor | 5th pct of positive MAI_moto | `accessibility_inputs` `_moto_floor` |

**Why geometric mean.** A mode is not competitive if it is fast but reaches almost nothing,
or reaches much but is too slow. The geometric mean forces *both* sub-indices to be non-trivial
— a near-zero on either pulls RAC down. (Same weakest-link logic as SMCI.)

**Theory support.**
- **Mode-competitive accessibility** — performance relative to the competing mode via
  travel-time or opportunity ratios (Liao et al., 2020; Kaszczyszyn & Sypion-Dutkowska, 2019).
  RAC adopts the central insight: *absolute accessibility is less behaviorally meaningful than
  accessibility relative to the realistic alternative.*
- **Motorcycle as the benchmark** — in motorcycle-dependent cities the competitor to transit
  is the two-wheeler, not the car (Khuat, 2006; Vu Anh Tuan, 2015). Benchmarking against the
  car (the usual choice) would mis-specify the competitive frontier.

---

## 4. MCS — Metropolitan Competitiveness Score

**What it measures.** A single metropolitan axis combining opportunity *level* (MAI) and mode
*competitiveness* (RAC). Used **only** for typology classification, not for SMCI.

```text
MCS_i = sqrt( MAI_norm_i * RAC_norm_i )
```
Geometric mean of normalized MAI and RAC (shared A+B bounds). Source of truth:
`accessibility.metropolitan_competitiveness_score`.

**Why separate from SMCI.** SMCI is the three-dimensional headline (local + metro + competitive).
MCS collapses the two metropolitan dimensions into one axis so the typology can be a clean 2×2
(NAI × MCS). Geometric mean again: a cell with high opportunity but no competitiveness should
not score as "metropolitanly strong."

---

## 5. SMCI — Sustainable Mobility Capability Index

**What it measures.** The headline metric. Joint presence of (1) local walking access,
(2) metropolitan opportunity access, and (3) mode competitiveness — a **weakest-link** index.

**Primary (multiplicative).**
```text
SMCI_i = NAI_norm_i * MAI_norm_i * RAC_norm_i
```
All three components min-max normalized. Any component near zero collapses the index — that is
the intended "capability requires all three at once" semantics.

**Scenario delta (shared scale, Decision #11).**
```text
Delta_SMCI_i = SMCI_B_i - SMCI_A_i
```
Computed on common Scenario A+B normalization bounds, **not** from separately normalized
scenario scores (Decision #11 — separate scaling produced artificial declines).

**Robustness alternative (additive, NOT geometric).**
```text
SMCI_additive_i = (NAI_norm_i + MAI_norm_i + RAC_norm_i) / 3
```
| Parameter | Value | Code |
|---|---|---|
| Primary combination | product (multiplicative) | `accessibility.compute_smci` |
| Robustness combination | mean (additive) | `accessibility.compute_smci_additive` |
| Normalization | min-max, shared A+B for Δ | `accessibility.norm01[_with_bounds]` |

**Why additive, not geometric, for robustness (Decision #4).** `(NAI*MAI*RAC)^(1/3)` is a
monotonic transform of the product → Spearman ρ = 1.0 by construction → tests nothing.
The *additive* form allows compensation across dimensions and is the genuine robustness contrast.
Guarded by `tests/test_accessibility.py::test_geometric_mean_check_is_vacuous`.

**Theory support.**
- **Capability approach to mobility** — shifts evaluation from infrastructure *provision* to
  feasible mobility *outcomes* (paper §2). SMCI asks what a resident can plausibly do from a
  location, not what is nominally built nearby.
- **Multi-dimensional / weakest-link composition** — sustainable mobility requires local access
  *and* metropolitan reach *and* a competitive sustainable mode simultaneously; a multiplicative
  index encodes non-substitutability across the three dimensions.

---

## 6. Normalization & shared-scale rule

All composite inputs are min-max normalized to [0, 1]:
```text
norm01(x) = (x - min(x)) / (max(x) - min(x))          (0 if max==min)
```
**Scenario comparison rule (Decision #11).** MAI, each RAC sub-component, and the RAC composite
are normalized on **shared Scenario A+B bounds** before MCS / SMCI / Δ. This makes Δ_SMCI a
clean scenario contrast rather than a change in relative position between two different scales.
Source: `accessibility.shared_minmax`, `norm01_with_bounds`; applied in `pilot.compute_pilot_metrics`.

---

## 7. Typology — theory-first 2×2 classification

**What it measures.** Four interpretable mobility-capability types from two axes: neighborhood
access (NAI) and metropolitan competitiveness (MCS).

**Rule.** Rank-based median split on each axis (NOT value `>= median`):
```text
NAI_high_i = rank(NAI_i)  >= n/2
MCS_high_i = rank(MCS_i)  >= n/2
```

| NAI | MCS | Typology | Meaning |
|---|---|---|---|
| High | High | **Integrated Capability** | Local access + metropolitan competitiveness both present |
| High | Low | **Fragmented Capability** | Local access exists, metropolitan sustainable mobility weak |
| Low | High | **Transit-Dependent** | Metropolitan access despite weak local access |
| Low | Low | **Motorcycle Lock-in** | Both weak |

| Parameter | Value | Code |
|---|---|---|
| Split | rank-based median (ordinal) | `accessibility.theory_first_typology` |
| Primary classifier | theory-first 2×2 | same |
| Robustness classifier | k-means (cross-check only) | reported, not primary |

**Why rank-based, not value-based (Decision #2).** When MCS has a mass point at 0 (e.g.
GTFS-missing baseline where MAI_A=0 everywhere collapses MCS_A), `>= np.median()` cannot split
the tie and the 4-typology guarantee breaks. Rank-based ordering always yields exactly 4 cells
by construction. With continuous data the two are equivalent.

**Why theory-first, not pure k-means (Decision #2).** Unconstrained k-means has no reason to
return exactly the 4 named types (could give 3/5/6). The framework is built around 4 conceptual
types, so the primary classifier is theory-driven; k-means is a robustness cross-check, with
disagreement *reported*, not resolved by tuning k.

**Theory support.** The 2×2 is the operational form of the dual-scale + mode-competitive thesis:
neighborhood completeness (NAI / 15-minute-city axis) is explicitly crossed with metropolitan
competitiveness (MCS = MAI × RAC), so "locally complete but metropolitanly isolated"
(Fragmented Capability) becomes a distinct, namable outcome rather than being averaged away.

---

## 8. Validation & robustness diagnostics

| Diagnostic | Definition / threshold | Code | Purpose |
|---|---|---|---|
| **VIF** | Variance inflation; flag if > 5 | `validation.collinearity_check` | MAI/RAC collinearity (structural, Decision #3) |
| **RAC_time-only contingency** | Drop RAC_opp; RAC = RAC_time only | `pilot.compute_pilot_metrics` | VIF remedy when full-RAC VIF > 5 |
| **Cohen's κ** | Typology agreement between specs | `pilot.typology_kappa` | Robustness of classification |
| **Spearman ρ** | SMCI rank agreement between specs | `scipy.stats.spearmanr` | Robustness of ranking |
| **Additive SMCI** | `(NAI+MAI+RAC)/3` | `accessibility.compute_smci_additive` | Compensatory robustness contrast |
| **Built-cell / zero-access audit** | Footprint presence in zero-NAI cells | `built_population_zero_access_audit.py` | Is zero-access an open-space artifact? |
| **Population-weighted SMCI** | residents × SMCI (demand-side) | `compute_population_weighted_smci.py` | Equity cross-check (sensitivity only) |
| **Motorcycle speed sensitivity** | slow/fast lane-splitting scenarios | `motorcycle_speed_sensitivity.py` | Network D robustness |
| **Transit impedance sensitivity** | conservative/pessimistic wait+access penalties | `transit_impedance_sensitivity.py` | Network B/C robustness |

**Thresholds in use.** VIF > 5 = high (conventional); κ ≥ 0.8 = strong agreement; ρ ≥ 0.95
= ranking preserved. Current strict-mode values: VIF(MAI)=10.23, VIF(RAC)=11.12 (full-RAC);
VIF(MAI)=2.93, VIF(RAC_time)=2.02 (RAC_time-only); primary vs RAC_time-only κ=0.9125, ρ=0.9889,
28/462 relabelled.

**Theory support.**
- VIF / collinearity diagnostics — standard regression-diagnostic practice; here motivated by
  the *structural* overlap between MAI and RAC_opp (they share MAI_transit), so collinearity is
  expected, not incidental (Decision #3).
- Sensitivity-first reporting — the additive contrast (Decision #4), shared-scale Δ (Decision #11),
  and RAC_time-only contingency (Decision #3) are all designed to test the headline rather than
  defend it.

---

## 9. Parameter quick-reference

| Parameter | Symbol | Value | Where |
|---|---|---|---|
| Neighborhood walk cutoff | `T_walk` | 15 min (~800 m) | NAI |
| Walk speed | — | 80 m/min (1.333 m/s) | NAI, transit access |
| Decay full-weight cutoff | `t_full` | 30 min | MAI decay |
| Decay zero cutoff | `t_zero` | 60 min | MAI decay |
| Motorcycle MAI cutoff | — | 20 min (~3000 m base) | RAC denominator |
| Domain weights | — | 0.40 / 0.20 / 0.20 / 0.20 | MAI composite |
| Healthcare ref / caps | — | 50 beds / [0.4, 30] | obs weight |
| Higher-ed ref / caps | — | 1000 enroll / [0.5, 20] | obs weight |
| Economic ref / caps | — | 500 jobs / [0.1, 5.0] | obs weight |
| Commercial ref / caps | — | 1000 m² / [0.1, 25] | obs weight |
| Pop multiplier bounds | `m_j` | [0.5, 2.0], sqrt, median-centered | supply weighting |
| VinBus headway (default) | — | 15 min (T_wait = headway/2) | Network C |
| Bus line-haul speed | — | 20 km/h | Network C |
| VIF flag threshold | — | 5.0 | validation |
| Typology split | — | rank-based median (2×2) | classification |

---

## 10. References (theory support)

- Geurs, K. T., & van Wee, B. (2004). Accessibility evaluation of land-use and transport
  strategies: Review and research directions. *Journal of Transport Geography, 12*(2), 127–140.
  https://doi.org/10.1016/j.jtrangeo.2003.10.005
- Handy, S. L., & Niemeier, D. A. (1997). Measuring accessibility: An exploration of issues
  and alternatives. *Environment and Planning A, 29*(7), 1175–1194. https://doi.org/10.1068/a291175
- Hansen, W. G. (1959). How accessibility shapes land use. *Journal of the American Institute
  of Planners, 25*(2), 73–76. https://doi.org/10.1080/01944365908978307
- Kaszczyszyn, P., & Sypion-Dutkowska, N. (2019). Walking access to public transport stops for
  city residents: A comparison of methods. *Sustainability, 11*(14), 3758.
  https://doi.org/10.3390/su11143758
- Khuat, V. H. (2006). *Traffic management in motorcycle dependent cities* (Doctoral
  dissertation). Darmstadt University of Technology.
- Liao, Y., Gil, J., Pereira, R. H. M., Yeh, S., & Verendel, V. (2020). Disparities in travel
  time between car and transit: Spatiotemporal patterns in cities. *Scientific Reports, 10*,
  4056. https://doi.org/10.1038/s41598-020-61077-0
- Moreno, C., Allam, Z., Chabaud, D., Gall, C., & Pratlong, F. (2021). Introducing the
  "15-Minute City": Sustainability, resilience and place identity in future post-pandemic
  cities. *Smart Cities, 4*(1), 93–111. https://doi.org/10.3390/smartcities4010006
- Nguyen, X. L., & Nguyen, H. T. (2018). Operating speed of motorcycles on urban streets in
  Hanoi. *Journal of the Eastern Asia Society for Transportation Studies, 12*, 1421–1435.
- Vu Anh Tuan. (2015). Mode choice behavior and modal shift to public transport in developing
  countries: The case of Hanoi city. *Journal of the Eastern Asia Society for Transportation
  Studies, 11*, 473–487.
- Vu Anh Tuan, Nguyen, H., & Pham, T. (2016). Motorcycle traffic characteristics in Hanoi.
  *Transportation Research Procedia, 15*, 651–662.
- Japan International Cooperation Agency (JICA). (2010). *The comprehensive urban development
  programme in Hanoi capital city (HAIDEP)*. JICA / Hanoi People's Committee.

**Cross-references in repo:** formula source of truth `src/accessibility.py`; input
construction `src/accessibility_inputs.py`, `src/routing.py`; decision rationale
`docs/decisions.md` (#2 typology, #3 VIF, #4 additive, #7 NAI count, #11 shared-scale,
#12/#15 MAI, #18 domain caps, #19 population, #20 RAC_time, #21 observed hierarchy);
methodology prose `proposal/proposal_v7.md` §8–10 and `paper/paper_draft.md` §2, §5–6.

# Metrics Reference — Formulas, Thresholds, and Theory Support

Single reference for every metric in the study: what it is, the exact formula, the
thresholds/parameters that define it, the source of truth in code, and the theoretical
framework that justifies it.

This is a **reference document**, not a tutorial. The authoritative implementation is
`src/accessibility.py` (index formulas) and `src/accessibility_inputs.py` /
`src/routing.py` (input construction). If a formula here disagrees with the code, the
code wins — fix this file. Last synced: 2026-07-01 (strict observed MAI + RAC_time
promoted to primary per Decision #22; NAI threshold under localized audit per Decision #26;
full-RAC retained as robustness; 77 tests).
For a plain-language Vietnamese explanation, see `docs/metrics_explained_vi.md`.

Convention: cell index `i`, opportunity/POI index `j`, domain index `k`,
travel time `t_ij` in minutes unless stated.

---

## Terminology — base concepts (defined, with sources)

Domain terms used throughout this study, each grounded in a citable definition so the
metrics build on established constructs rather than ad-hoc usage.

| Term | Definition (as used here) | Source |
|---|---|---|
| **Point of Interest (POI)** | A proxy for a real-world location (e.g. restaurant, school, clinic), usually represented as a geometric point entity, carrying a name and a hierarchically organized category. In this study each POI `j` is one opportunity destination. | Psyllidis et al. (2022) |
| **POI category / urban function** | The type label organizing POIs hierarchically (e.g. health → hospital); the basis for assigning each POI to one of the four MAI opportunity domains. | Psyllidis et al. (2022) |
| **Accessibility** | The extent to which the land-use–transport system enables individuals to reach activities/opportunities; a place-based measure of *reachable opportunity*, not realized travel. | Geurs & van Wee (2004) |
| **Cumulative-opportunity accessibility** | Count (or weighted sum) of opportunities reachable within a fixed travel-time/distance budget. NAI is the count-based, walk-only special case; MAI the magnitude-weighted, multimodal case. | Handy & Niemeier (1997) |
| **Walkability / 15-minute access** | Local proximity to daily destinations reachable on foot; current pilot primary is an 800 m / 10-minute pedestrian shed (Decision #27), with 1200 m / 15 min reported as an optimistic upper-bound sensitivity from the 600/800/1000/1200 m threshold audit. | Moreno et al. (2021); Bruno et al. (2024); Tran et al. (2015) |
| **TOD / transit-oriented development** | Planning logic that concentrates mixed-use development around high-quality transit access. In this study TOD is treated as a planning claim to be audited through realized accessibility, not as an automatic sustainability outcome. | Calthorpe (1993); Cervero & Kockelman (1997) |
| **Green megaproject / mega green city** | Large master-planned development marketed through environmental design, amenities, and infrastructure provision. In this study the "green" claim is tested through local access, metropolitan access, and motorcycle-relative competitiveness. | Shatkin (2008); Joss et al. (2011); Caprotti (2014, 2015); Cugurullo (2016) |
| **Network distance / travel time** | Shortest-path distance or model-estimated time along the actual routable network (OSM graph via Dijkstra), not straight-line ("as-the-crow-flies") distance and not observed GPS duration for every OD pair. `t_ij` is the estimated network travel time from cell `i` to POI `j`. | (routing convention; `routing.py`, `accessibility_inputs.py`) |
| **Catchment** | The set of POIs `j` whose network travel time from cell `i` falls within the relevant threshold `{ j : t_ij <= T }`. | (operational, this study) |
| **Mode-competitive accessibility** | Accessibility of one mode expressed *relative to* a competing mode (here walk+transit vs motorcycle) rather than in absolute terms. | Liao et al. (2020) |

POI provenance and source tiers specific to this study's opportunity magnitudes are in §2.3.

---

## Framing — TOD and green-megaproject audit

The project is not only asking whether Ocean Park has parks, shops, bus stops, or green branding.
It asks whether those features combine into *sustainable mobility capability* under Hanoi's
motorcycle-dominant conditions.

- **TOD logic.** TOD theory links compact mixed use and transit access, but the metric test here is
  stricter: a TOD-like environment must also make walking and transit competitive with motorcycles.
- **Green megaproject logic.** Eco-city / green-megaproject literature warns that sustainability can
  remain a branding or planning claim unless social and mobility outcomes are measured. SMCI turns
  that critique into an accessibility audit.
- **Operational implication.** `Integrated Capability` is not assigned because an area is branded
  green or transit-served. It is assigned only when NAI and MCS are both high relative to the study
  area, where MCS combines metropolitan access and motorcycle-relative competitiveness.

---

## 0. Metric map

| Metric | Scale | Type | Feeds into | Code |
|---|---|---|---|---|
| **NAI** | Neighborhood | Count | SMCI, typology axis 1 | `routing.reachable_counts_and_mean_time` |
| **MAI** | Metropolitan | Magnitude-weighted | RAC_opp, MCS, SMCI | `routing.composite_mai_from_graph` |
| **RAC_time** | Mode-competitive | Time ratio | **RAC primary, MCS, SMCI** | `accessibility_inputs` (opp-weighted times) |
| **RAC_opp** | Mode-competitive | Opportunity ratio | RAC_full (legacy) | `accessibility_inputs._safe_ratio` |
| **RAC** | Mode-competitive | RAC_time (primary) / full=geom. mean (legacy) | MCS, SMCI | `pilot.compute_pilot_metrics` |
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
| `T_walk` (neighborhood cutoff) | primary 800 m / 10 min (Decision #27); 1200 m / 15 min reported as optimistic upper-bound sensitivity | Decisions #26/#27; `build_accessibility_inputs.py --walking-threshold-m` (default 800) |
| Walking speed | 1.333 m/s (80 m/min) | Yang et al. (2023); `routing.py` access cutoff |
| Routing | Dijkstra shortest path on OSM walk graph | `routing.reachable_counts_and_mean_time` |

**Why count, not gravity (Decision #7).** At the neighborhood scale the relevant question
is binary-ish — *is there a school / clinic / shop within walking distance?* A kiosk and a
supermarket both satisfy "daily needs nearby," so presence matters more than magnitude. A
gravity/decay weighting here would smuggle metropolitan-scale logic into a local measure.

**Theory support.**
- **15-minute city / walkability** — local proximity to daily destinations as a dimension
  of sustainable urbanism (Moreno et al., 2021). NAI operationalizes the "local completeness"
  axis the framework deliberately separates from metropolitan reach.
- **Inclusive 15-minute accessibility** — recent large-scale work treats 15-minute access to
  essential services as an inclusion/equity question, not only an urban-design slogan
  (Bruno et al., 2024).
- **Threshold localization** — 15-minute community-life-circle studies often implement
  15 minutes as 1200 m at 80 m/min walking speed, but Decision #26 requires this project to
  localize the cutoff for Hanoi rather than import that distance mechanically.
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

**Domain-weight provenance (0.40/0.20/0.20/0.20).** These are a **theory-informed prior**
(employment-centrality tradition: economic access weighted highest), not raw revealed-demand weights.
`scripts/derive_mai_weights_utm.py` derives a sensitivity scheme from the open UTM-Hanoi
transport-policy perception dataset (Kieu et al., 2024; OSF DOI 10.17605/OSF.IO/497US).
The filled input is `data/raw/utm_hanoi_trip_purpose.csv`: work 15,145, education 4,494,
shopping 1,922, leisure 934, visit 3,176, and caring 435 (`N=26,106`). The MAI-domain
mapping is work→economic, education→higher_education, shopping→metro_commercial, and
caring→tertiary_healthcare; leisure/visit are excluded before renormalization because they
do not map cleanly to the four MAI opportunity domains. The resulting `utm_derived` weights
are economic 0.6885, higher education 0.2043, tertiary healthcare 0.0198, and metro commercial
0.0874, written to `data/interim/mai_weights_utm_derived.csv` and available in
`MAI_DOMAIN_WEIGHTS["utm_derived"]`. Current `default` remains the smoothed prior above.
HAIDEP 2010 trip-purpose shares were **not** usable (raw distribution behind JICA licensing).
The healthcare weight stays survey-*informed*, not survey-*derived*: the survey has no health-trip
purpose, so `caring` is an imperfect proxy and the 0.20 default floor reflects
essential-but-low-frequency access.
**Robustness:** typology is stable across weight schemes (metric audit — equal/job_heavy/econ_light
all κ≥0.92), so the headline does not hinge on the exact prior.

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
| higher_education | enrollment | 1000 (mid-size education campus/reference facility) | 0.5 | 20.0 |
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

Operationally, `RAC_time` uses network-based estimated travel times, not observed trip
durations for every OD pair:
- walking time = OSM walk-graph shortest path with walking speed assumptions;
- motorcycle time = OSM drive-graph shortest path with literature-calibrated motorcycle speeds;
- Scenario A walk-transit time = 2018 Hanoi GTFS pre-VinBus stop-proxy timing;
- Scenario B walk-transit time = VinBus pseudo-GTFS stop routing with access, wait, line-haul,
  and egress components.

Motorcycle time is externally spot-checked against 10 Android Google Maps two-wheeler OD
pairs: MAE = 1.90 min, MAPE = 22.17%, MBE = -1.04 min, RMSE = 2.20 min
(`outputs/validation/travel_time_validation_report.md`). This supports comparative
accessibility analysis but is not a full GPS/real-time validation dataset.

### 3.2 RAC_opp — opportunity competitiveness

```text
RAC_opp_raw_i = MAI_transit_i / MAI_motorcycle_i
```
Ratio of two commensurable composite MAI scores (Decision #15). Higher = transit reaches a
larger share of weighted metropolitan opportunity relative to the motorcycle. Denominator
floored at the 5th percentile of positive `MAI_motorcycle` to prevent blow-up in isolated
drive-graph cells.

### 3.3 RAC composite — RAC_time primary (Decision #22)

**Primary RAC = RAC_time alone.**

```text
RAC_i = RAC_time_norm_i
```

RAC_time is min-max normalized on shared Scenario A+B bounds (Section 6) and used directly as
the RAC component of MCS / SMCI. Promoted to primary because full-RAC carries a structural
MAI/RAC_opp collinearity (both share MAI_transit) that pushes VIF above the conventional
threshold; dropping RAC_opp brings max VIF from 10.04 to 3.82 while preserving the typology
(κ=0.9116, ρ=0.9824, 28/462 relabelled — Decision #22/#23 metric audit).

**Legacy full-RAC (robustness, retained).**

```text
RAC_full_i = sqrt( RAC_time_norm_i * RAC_opp_norm_i )
```

Both sub-indices min-max normalized on shared A+B bounds, combined as a **geometric mean**.
Kept as `RAC_full_A/B` and `SMCI_B_full_rac_legacy` for the robustness comparison, not in the
headline.

| Parameter | Value | Code |
|---|---|---|
| Primary RAC | RAC_time only | `pilot.compute_pilot_metrics` |
| Legacy full RAC | geometric mean of RAC_time, RAC_opp | `accessibility.compute_rac_shared` then `pilot.compute_pilot_metrics` stores `RAC_full_A/B` |
| Normalization | shared A+B min-max | `accessibility.compute_rac_shared`, then primary override in `pilot.compute_pilot_metrics` |
| RAC_opp denominator floor | 5th pct of positive MAI_moto | `accessibility_inputs` `_moto_floor` |

**Why geometric mean (legacy rationale).** A mode is not competitive if it is fast but reaches
almost nothing, or reaches much but is too slow. The geometric mean forces *both* sub-indices to
be non-trivial — a near-zero on either pulls RAC down. (Same weakest-link logic as SMCI.) The
primary spec drops RAC_opp purely to remove the structural collinearity, not because the
weakest-link logic is wrong.

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
All three components min-max normalized; `RAC_norm` is the primary RAC (= RAC_time, Decision #22).
Any component near zero collapses the index — that is the intended "capability requires all three
at once" semantics. Current pilot (800 m NAI primary, Decision #27): SMCI_A=0.0070, SMCI_B=0.0133,
mean Delta=0.0063, 281/462 improved (60.8%), 88 unchanged, 93 declined; typology_B 171/171/60/60.

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
- **Capability and transport justice** — shifts evaluation from infrastructure *provision* to
  feasible mobility *outcomes* (Sen, 1999; Pereira et al., 2017). SMCI asks what a resident
  can plausibly do from a location, not what is nominally built nearby.
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
| **Full-RAC robustness** | RAC = geom. mean(RAC_time, RAC_opp); legacy | `pilot.compute_pilot_metrics` | Robustness vs promoted RAC_time primary (Decision #22) |
| **Cohen's κ** | Typology agreement between specs | `pilot.typology_kappa` | Robustness of classification |
| **Spearman ρ** | SMCI rank agreement between specs | `scipy.stats.spearmanr` | Robustness of ranking |
| **Additive SMCI** | `(NAI+MAI+RAC)/3` | `accessibility.compute_smci_additive` | Compensatory robustness contrast |
| **Built-cell / zero-access audit** | Footprint presence in zero-NAI cells | `built_population_zero_access_audit.py` | Is zero-access an open-space artifact? |
| **Population-weighted SMCI** | residents × SMCI (demand-side) | `compute_population_weighted_smci.py` | Equity cross-check (sensitivity only) |
| **Travel-time validation** | 10 manual Google Maps Android two-wheeler OD pairs; MAE < 3 min | `travel_time_validation_report.md` | Plausibility check for Network D motorcycle time |
| **Motorcycle speed sensitivity** | slow/fast lane-splitting scenarios | `motorcycle_speed_sensitivity.py` | Network D robustness |
| **Transit impedance sensitivity** | conservative/pessimistic wait+access penalties | `transit_impedance_sensitivity.py` | Network B/C robustness |

**Thresholds in use.** VIF > 5 = a conservative collinearity flag (O'Brien, 2007);
κ ≥ 0.8 = strong agreement (Landis & Koch, 1977); ρ ≥ 0.95 = ranking preserved.
Current strict-mode values: **primary RAC_time** VIF(MAI)=3.82,
VIF(RAC)=1.92 (both below threshold); legacy full-RAC VIF(MAI)=10.04, VIF(RAC)=9.89 (high,
structural). Promoted RAC_time vs legacy full-RAC: κ=0.9116, ρ=0.9824, 28/462 relabelled
(Decision #22 metric audit, `outputs/validation/metric_variant_audit.md`).

Travel-time validation is deliberately framed as a plausibility check, not as proof of exact
trip-time prediction. Current motorcycle spot-check performance is MAE=1.90 min against 10
manual Android Google Maps two-wheeler OD pairs, below the 3.0 min research threshold used in
`outputs/validation/travel_time_validation_report.md`.

**Theory support.**
- VIF / collinearity diagnostics — standard regression-diagnostic practice; here motivated by
  the *structural* overlap between MAI and RAC_opp (they share MAI_transit), so collinearity is
  expected, not incidental (Decision #3).
- Sensitivity-first reporting — the additive contrast (Decision #4), shared-scale Δ (Decision #11),
  and the legacy full-RAC robustness comparison (Decisions #3, #22) are all designed to test the
  headline rather than defend it. RAC_time was promoted from contingency to primary once the
  metric audit confirmed it removes the structural collinearity while preserving the typology.

---

## 9. Parameter quick-reference

| Parameter | Symbol | Value | Where |
|---|---|---|---|
| Neighborhood walk cutoff | `T_walk` | primary 800 m / 10 min (Decision #27); 1200 m / 15 min as optimistic upper-bound sensitivity | NAI |
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

- Bruno, M., Melo, H. P. M., Campanelli, B., & Loreto, V. (2024). A universal framework
  for inclusive 15-minute cities. *Nature Cities*. https://doi.org/10.1038/s44284-024-00119-4
- Calthorpe, P. (1993). *The next American metropolis: Ecology, community, and the American dream*.
  Princeton Architectural Press.
- Caprotti, F. (2014). Eco-urbanism and the eco-city, or, denying the right to the city?
  *Antipode, 46*(5), 1285-1303. https://doi.org/10.1111/anti.12087
- Caprotti, F. (2015). Eco for whom? Envisioning eco-urbanism in the Sino-Singapore
  Tianjin Eco-city, China. *International Journal of Urban and Regional Research, 39*(3),
  495-517. https://doi.org/10.1111/1468-2427.12233
- Cervero, R., & Kockelman, K. (1997). Travel demand and the 3Ds: Density, diversity, and design.
  *Transportation Research Part D: Transport and Environment, 2*(3), 199-219.
  https://doi.org/10.1016/S1361-9209(97)00009-6
- Cugurullo, F. (2016). Urban eco-modernisation and the policy context of new eco-city projects:
  Where Masdar City fails and why. *Urban Studies, 53*(11), 2417-2433.
  https://doi.org/10.1177/0042098015588727
- Geurs, K. T., & van Wee, B. (2004). Accessibility evaluation of land-use and transport
  strategies: Review and research directions. *Journal of Transport Geography, 12*(2), 127–140.
  https://doi.org/10.1016/j.jtrangeo.2003.10.005
- Handy, S. L., & Niemeier, D. A. (1997). Measuring accessibility: An exploration of issues
  and alternatives. *Environment and Planning A, 29*(7), 1175–1194. https://doi.org/10.1068/a291175
- Hansen, W. G. (1959). How accessibility shapes land use. *Journal of the American Institute
  of Planners, 25*(2), 73–76. https://doi.org/10.1080/01944365908978307
- Japan International Cooperation Agency (JICA). (2010). *The comprehensive urban development
  programme in Hanoi capital city (HAIDEP)*. JICA / Hanoi People's Committee.
- Joss, S., Tomozeiu, D., & Cowley, R. (2011). Eco-cities: The mainstreaming of urban
  sustainability - key characteristics and driving factors. *International Journal of
  Sustainable Development and Planning, 6*(3), 268-285.
  https://doi.org/10.2495/SDP-V6-N3-268-285
- Kaszczyszyn, P., & Sypion-Dutkowska, N. (2019). Walking access to public transport stops for
  city residents: A comparison of methods. *Sustainability, 11*(14), 3758.
  https://doi.org/10.3390/su11143758
- Kieu, M., Comber, A., Nguyen Thi Thuy, H., Bui Quang, T., Hoang Huu, P., & Malleson, N.
  (2024). An open dataset on individual perceptions of transport policies. *Scientific Data*.
  https://doi.org/10.1038/s41597-024-02950-9
- Khuat, V. H. (2006). *Traffic management in motorcycle dependent cities* (Doctoral
  dissertation). Darmstadt University of Technology.
- Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical
  data. *Biometrics, 33*(1), 159–174. https://doi.org/10.2307/2529310
- Liao, Y., Gil, J., Pereira, R. H. M., Yeh, S., & Verendel, V. (2020). Disparities in travel
  time between car and transit: Spatiotemporal patterns in cities. *Scientific Reports, 10*,
  4056. https://doi.org/10.1038/s41598-020-61077-0
- Moreno, C., Allam, Z., Chabaud, D., Gall, C., & Pratlong, F. (2021). Introducing the
  "15-Minute City": Sustainability, resilience and place identity in future post-pandemic
  cities. *Smart Cities, 4*(1), 93–111. https://doi.org/10.3390/smartcities4010006
- Nguyen, X. L., & Nguyen, H. T. (2018). Operating speed of motorcycles on urban streets in
  Hanoi. *Journal of the Eastern Asia Society for Transportation Studies, 12*, 1421–1435.
- O'Brien, R. M. (2007). A caution regarding rules of thumb for variance inflation factors.
  *Quality & Quantity, 41*, 673–690. https://doi.org/10.1007/s11135-006-9018-6
- Psyllidis, A., Gao, S., Hu, Y., Kim, E-K., McKenzie, G., Purves, R., Yuan, M., & Andris, C.
  (2022). Points of Interest (POI): A commentary on the state of the art, challenges, and
  prospects for the future. *Computational Urban Science, 2*(1), 20.
  https://doi.org/10.1007/s43762-022-00047-w
- Pereira, R. H. M., Schwanen, T., & Banister, D. (2017). Distributive justice and equity
  in transportation. *Transport Reviews, 37*(2), 170–191.
  https://doi.org/10.1080/01441647.2016.1257660
- Sen, A. (1999). *Development as freedom*. Oxford University Press.
- Shatkin, G. (2008). The city and the bottom line: Urban megaprojects and the privatization
  of planning in Southeast Asia. *Environment and Planning A, 40*(2), 383-401.
  https://doi.org/10.1068/a38439
- Vu Anh Tuan. (2015). Mode choice behavior and modal shift to public transport in developing
  countries: The case of Hanoi city. *Journal of the Eastern Asia Society for Transportation
  Studies, 11*, 473–487.
- Vu Anh Tuan, Nguyen, H., & Pham, T. (2016). Motorcycle traffic characteristics in Hanoi.
  *Transportation Research Procedia, 15*, 651–662.
- Yang, Y., Qian, Y., Zeng, J., Wei, X., & Yang, M. (2023). Walkability measurement of
  15-minute community life circle in Shanghai. *Land, 12*(1), 153.
  https://doi.org/10.3390/land12010153

**Cross-references in repo:** formula source of truth `src/accessibility.py`; input
construction `src/accessibility_inputs.py`, `src/routing.py`; decision rationale
`docs/decisions.md` (#2 typology, #3 VIF, #4 additive, #7 NAI count, #11 shared-scale,
#12/#15 MAI, #18 domain caps, #19 population, #20 RAC_time, #21 observed hierarchy,
#22 RAC_time primary promotion, #26 localized NAI threshold audit);
methodology prose `proposal/proposal_v7.md` §8–10 and `paper/paper_draft.md` §2, §5–6.

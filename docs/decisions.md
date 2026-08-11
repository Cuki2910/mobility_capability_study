# Decision Log

Why things are the way they are — read this before changing the methodology,
so settled debates don't get silently re-opened.

1. **DEC-001 — Single case study (Vinhomes Ocean Park only), not two.**
   A second site (Vinhomes Smart City) was proposed as a "reproducibility
   appendix" in an earlier draft and was cut. Running a second full site
   roughly doubles data collection and computation; explicitly deferred to
   future work to keep this feasible as one paper/thesis.

2. **DEC-002 — Classification is theory-first (median split), not pure k-means.**
   k-means run with no theoretical constraint has no reason to produce
   exactly the 4 named typologies the framework is built around (could
   return 3, 5, 6 clusters). Primary specification: median-split NAI x
   Metropolitan Competitiveness Score (MCS = geometric mean of normalized
   MAI, RAC) -> exactly 4 cells by construction. k-means is kept only as a
   robustness cross-check, with disagreement reported, not resolved by
   tuning k until it matches.

   **Implementation note (2026-06-21):** median split uses rank-based ordering,
   not value-based `>= np.median()`, so the 4-typology guarantee holds even
   when MCS has a large point mass at 0 (e.g. GTFS-missing pilot where
   baseline MAI_A = 0 for all cells collapses MCS_A to 0 everywhere).
   With continuous real-data MCS the two approaches are equivalent. The
   rank split is the more general and correct implementation of "median split"
   in the presence of ties at a mass point.

3. **DEC-003 — MAI and RAC are expected to be collinear — this is structural, not just empirical.**
   RAC_opp's numerator (opportunities reachable via walk+transit) is the
   same quantity used to build MAI. Motorcycle accessibility (RAC_opp's
   denominator) is expected to vary relatively little across a
   motorcycle-dependent city. Confirmed on synthetic data with a plausible
   correlation structure: VIF(MAI)=9.4, VIF(RAC)=11.2 (pilot run,
   2026-06-21) — both over the conventional threshold of 5. Contingency:
   report RAC using RAC_time only if real-data VIF is also high.

   **Earlier corridor-proxy run (2026-06-22):** Pilot real-data VIF was high and
   motivated the RAC_time-only contingency. This result is superseded by the stop-routing
   primary output below, but it remains useful provenance for why the contingency exists.
   Updated stop-routing + merged-POI primary output (2026-06-23): VIF(MAI)=16.92,
   VIF(RAC)=17.94. RAC_time-only sensitivity gives kappa=0.888, Spearman rho=0.993,
   and 36/462 cells relabelled. In the RAC_time-only specification, VIF(MAI)=4.78
   and VIF(RAC_time)=4.32, both below 5. Primary full-RAC specification is retained.
   Full output: `outputs/validation/rac_time_only_summary.md`.

4. **DEC-004 — Do NOT use a geometric-mean alternative to validate the multiplicative SMCI.**
   SMCI_geo = (NAI*MAI*RAC)^(1/3) is a monotonic transform of
   SMCI_mult = NAI*MAI*RAC. Spearman rank correlation between them is
   mathematically guaranteed to be 1.0 — this was caught by actually
   running the numbers (pilot, 2026-06-21), not by reading the proposal
   text. Use the ADDITIVE alternative, (NAI+MAI+RAC)/3, for the real
   robustness comparison. See tests/test_accessibility.py::test_geometric_mean_check_is_vacuous.

5. **DEC-005 — Motorcycle travel time is NOT the same as default OSM driving speed.**
   [*Partially superceded by DEC-030: lane-splitting as a speed-advantage mechanism is not
   directly verified by audited sources; see DEC-030 for current calibration provenance.*]
   Network D must apply explicit per-road-class speed assumptions, not assume car-equivalent
   speeds. The basis is scenario-calibrated assumptions informed by Hanoi motorcycle-speed
   literature rather than verified class-specific literature values.

6. **DEC-006 — Validation against Google Maps is secondary, not foundational.**
   [*Partially superceded by DEC-030: 'literature-calibrated' overstates the current
   provenance; see DEC-030 for correct characterization.*]
   Scenario-assumed motorcycle speeds are the primary basis for Network D travel times;
   Google Maps validation is a plausibility cross-check only.
   The model must not depend on an API that may not cover the study area.

7. **DEC-007 — NAI is count-based; MAI is magnitude-weighted.**
   A single OSM POI can represent an office tower or a kiosk. For daily
   neighborhood activities, presence/proximity matters more than size, so
   NAI counts facilities. For metropolitan opportunities (jobs, enrollment),
   volume is the conventional definition of "opportunity," so MAI uses
   proxy magnitudes (employment proxy, enrollment proxy, density score),
   not raw POI counts.

8. **DEC-008 — Why "electric bus" stays in the language even though propulsion type
   doesn't affect the accessibility math.**
   The green-vs-motorcycle-dependent tension is the paper's core hook
   (title, Introduction). Stripping "electric" to "transit intervention"
   would weaken that framing. Instead, Methods states explicitly that the
   intervention is evaluated through accessibility effects (routes, stops,
   connectivity), not propulsion or emissions effects — keeps the framing
   without overclaiming what the analysis measures.

9. **DEC-009 — The "green" dimension must be tested, not assumed.**
   NDVI and green-space accessibility are explicit variables (src/, Section
   3.5), and the Discussion plan explicitly asks whether they relate to
   SMCI/RAC at all — the paper should be able to say honestly if "green"
   turned out to be branding rather than a substantive driver.

10. **DEC-010 — 2018 Hanoi GTFS is treated as the pre-VinBus conventional transit baseline, not a data gap.**
    VinBus launched commercially in September 2021. The World Bank CC-BY feed
    (service dates 2018-01-01 to 2018-12-31, `data/raw/hanoi_gtfs.zip`) therefore
    reflects Hanoi public transit *before* the electric-bus intervention being
    studied. This makes it methodologically valid as Scenario A's Network B
    (walk + existing transit, no VinBus): it is a deliberate pre-intervention
    baseline, not an arbitrary vintage limitation.

    Stop geometry (7,670 stops) is used as-is for stop_accessibility(); the
    geometry of bus-stop infrastructure changes slowly relative to timetable
    frequency. Timetable/frequency data from the feed is used only for
    ordering magnitude, not trip-by-trip scheduling. If a post-2021 GTFS
    feed is found, re-run with it and report both vintages in Methods; the
    2018 feed remains valid as a sensitivity check.

    Implementation: `check_hanoi_gtfs.py` emits `gtfs_vintage`, `pre_vinbus_baseline`,
    and `network_b_interpretation` fields. `accessibility_inputs.py` note field
    reflects this framing.

11. **DEC-011 — Scenario A/B deltas must use shared normalization bounds.**
    The pilot originally normalized Scenario A and Scenario B separately inside
    `compute_smci()` and `compute_rac()`. That made `Delta_SMCI` partly a change
    in relative position between two different scales, not a clean scenario
    comparison. It also produced artificial declined cells even when raw Network C
    accessibility dominated Network B.

    Implementation: `src/pilot.py::compute_pilot_metrics` now computes RAC
    subcomponents on shared A+B min-max bounds, then normalizes MAI and RAC
    composite on shared A+B bounds before computing MCS, SMCI, additive SMCI,
    and Delta_SMCI. The standalone formula helpers in `src/accessibility.py`
    remain available for one-scenario diagnostics, but scenario comparison uses
    explicit shared-scale helpers. Regression test:
    `tests/test_pipeline.py::test_pilot_metrics_use_shared_scenario_scale_for_delta`.

12. **DEC-012 — Building footprints are the next data upgrade before stronger MAI claims.**
    WorldPop's resolution is adequate for the 250m grid, but gridded population
    products should not be treated as exact ground truth. For Ocean Park, the
    more immediate problem is separating built cells from lakes, parks, and
    other planned open spaces. A building-footprint layer from VIDA / Google
    Open Buildings / Microsoft / OSM directly addresses this by providing
    building count and footprint area per grid cell.

    Implementation plan: fetch or export building footprints for the pilot bbox,
    run `scripts/aggregate_building_footprints.py`, and use `building_count`,
    `building_footprint_area_m2`, and optional confidence scores as (a) a built-cell
    mask, (b) a WorldPop cross-check, and (c) a candidate MAI magnitude proxy.
    Kontur Population remains a coarse sensitivity/context layer only because
    its 400m resolution is coarser than the 250m analysis grid.

13. **DEC-013 — Overture Places supplements OSM POIs; it does not replace them.**
    Overture Places can increase POI coverage and provide an independent source,
    but coverage varies by market and category. The planned workflow is a union
    of OSM and Overture with source-agreement labels: OSM+Overture agreement =
    higher confidence; one-source-only records = targeted spot-check candidates.

14. **DEC-014 — Check maintained GTFS catalogs before final Network B wording.**
    `scripts/check_mobility_database.py --query Hanoi` checked the maintained
    MobilityDatabase CSV and found no Hanoi candidate feed in the catalog. This
    supports keeping the 2018 World Bank feed as the available pre-VinBus baseline,
    but final Methods should still mention that MobilityDatabase was checked and
    manually inspect TUMI/Datahub or official local sources before submission.

15. **DEC-015 — MAI is "Metropolitan Opportunity Accessibility", not "employment accessibility".**
    MAI v8 (2026-06-22) reframes MAI as a composite of four opportunity domains —
    economic, higher education, tertiary healthcare, metropolitan commercial/services —
    to avoid overclaiming employment counts that are not available at building resolution
    for Hanoi.

    Rationale: reviewer attack risk on "employment accessibility" without employment data
    outweighs the cost of a slightly more complex framing. "Metropolitan Opportunity
    Accessibility" is accurately described, reviewable, and consistent with the cumulative
    accessibility literature (Geurs & van Wee 2004; Kapatsila et al. 2023).

    Formula:

    ```text
    MAI_i = w_econ*A_econ + w_edu*A_edu + w_health*A_health + w_comm*A_comm
    ```

    Default weights: 0.40 / 0.20 / 0.20 / 0.20.
    Access per domain: `A_i,k = sum_j( OpportunityWeight_j,k * time_decay(t_ij) )`
    Decay: linear, 1.0 at t<=30min → 0.0 at t=60min (zero beyond 60min).
    Sensitivity runs: equal weights (0.25 each), job-heavy (0.50/0.15/0.15/0.20).

    **Weight provenance (updated 2026-06-30).** The 0.40/0.20/0.20/0.20 split is a
    theory-informed prior (employment-centrality), not raw revealed demand. To pre-empt the
    "weights look arbitrary" reviewer attack, `scripts/derive_mai_weights_utm.py` derives a
    sensitivity scheme from the open UTM-Hanoi transport-policy perception dataset (Kieu et al. 2024,
    Scientific Data; OSF 10.17605/OSF.IO/497US): observed trip-purpose shares → domains
    (work→economic, education→higher_education, shopping→metro_commercial,
    caring→tertiary_healthcare; leisure/visit excluded; renormalized). Counts are filled in
    `data/raw/utm_hanoi_trip_purpose.csv` and provenance is written to
    `data/interim/mai_weights_utm_derived.csv`; the resulting weights are economic 0.6885,
    higher_education 0.2043, tertiary_healthcare 0.0198, and metro_commercial 0.0874.
    HAIDEP 2010 shares were not usable (behind JICA licensing). Healthcare stays survey-*informed*
    not *derived* (`caring` is a proxy; survey has no health-trip purpose). Robustness already
    covers the risk: metric audit κ≥0.92 across equal/job_heavy/econ_light, so the headline does
    not hinge on the prior. Keep `utm_derived` as sensitivity unless the paper explicitly promotes it.

    RAC_opp_i = MAI_transit_i / MAI_motorcycle_i — ratio of two commensurable composite
    scores using the same decay function and domain weights. This is more principled than
    a ratio of raw POI counts.

    Double-counting in SMCI: MAI_transit appears in both MAI (absolute level) and as the
    numerator of RAC_opp (relative competitiveness). These measure different constructs:
    MAI = how much sustainable-mode metropolitan access a cell has; RAC_opp = how that
    access compares to what motorcycle achieves for the same cell. A transit-rich outer cell
    with good motorcycle coverage has equal or higher MAI but lower RAC_opp than an inner
    cell where motorcycle adds little. They are not redundant.

    Pilot limitation (original, pre-2026-06-25): the first pilot POI set (106 OSM features)
    included schools, clinics, hospitals, parks, and retail — no university campuses or
    office/employment nodes. Economic domain defaulted to a commercial-POI-density proxy
    and higher-education was near-zero. **This is now partially resolved — see Decision #18.**

16. **DEC-016 — VinBus headway assumption is 15 min (published schedule); sensitivity confirms it is not a material driver.**
    Earlier corridor-proxy Network C used no full timetable. Travel time included
    T_wait = headway / 2 (random-arrival assumption). The baseline 15 min headway comes from
    VinBus press releases for Ocean Park routes (E01, E03, OCP1). Three scenarios tested
    (optimistic 10 min / baseline 15 min / pessimistic 30 min):

    - Share of improved cells: identical at 64.07% across all scenarios.
    - Mean SMCI_B range: 0.080 (pessimistic) to 0.085 (optimistic) — <6% variation.
    - Typology kappa vs baseline: >=0.969. Headway did not materially change typology labels.

    Conclusion: the 15 min assumption is appropriate as a baseline. Headway sensitivity
    should be reported as a disclosure, not as a source of uncertainty about the main findings.
    If a real VinBus timetable is obtained, re-run with actual headways and compare.

    **Updated after stop-routing promotion (2026-06-23):** Network C now uses stop-level
    OSM VinBus route relations rather than corridor proximity. Headway sensitivity was rerun:
    mean SMCI_B is 0.0940 at 10 min, 0.0968 at 15 min, and 0.0950 at 30 min; improved-cell
    share is 52.4%, 51.9%, and 46.1% respectively. Typology kappa vs the 15 min baseline is
    1.000 for all scenarios, so headway still does not drive typology conclusions.

17. **DEC-017 — VinBus stop-level routing is primary; corridor proximity is sensitivity only.**
    The earlier Network C implementation used a corridor-proximity proxy. After confirming
    10 Ocean Park-facing OSM VinBus relations and extracting 254 unique platform/stop nodes,
    Network C now uses stop-level access: grid cell to stop by walking network, wait time,
    route stop-to-stop line-haul at a conservative bus speed, then stop to POI by walking network.

    Comparison against the corridor proxy (`outputs/validation/vinbus_routing_comparison.md`)
    found kappa=0.714, Spearman rho(SMCI_B)=0.979, Spearman rho(RAC_B)=0.586, and 94/462
    cells relabelled. This is a meaningful methodological change, so stop-level routing is
    promoted as the primary Network C representation and the corridor proxy is retained only
    as a sensitivity/proxy comparison. Full timetable-derived routing remains a future upgrade
    if a valid VinBus GTFS or equivalent feed becomes available.

18. **DEC-018 — Economic domain escaped from pure commercial-density proxy via OSM landuse + office tags (2026-06-25).**
    The original pilot had effectively one `economic` POI (a credit fund), so the 0.40
    economic domain weight was carried almost entirely by commercial fallback — a weak proxy.
    Two open-data channels (Hướng B + C) now populate the economic and higher-education domains:

    - **Hướng B (landuse polygons):** `landuse=commercial/retail/industrial/office` polygons
      are fetched (`scripts/fetch_osm_landuse.py`), area-measured, and converted to synthetic
      POIs at their centroids. Weight = `sqrt(area/1000)` bounded [0.1, 50.0] — sqrt dampens
      large industrial zones so a single KCN does not dominate the domain.
    - **Hướng C (office/financial nodes):** `office=*`, `amenity=bank/marketplace/post_office`
      are added to the fetch tag set and classified directly. `office=company/government/it/
      financial/...` → economic; `office=educational_institution/university/research` and
      name-matched lecture halls ("Giảng đường", "Đại học", ...) → higher_education.

    Merge + dedup (`scripts/merge_economic_features.py`, 30 m threshold) added 47 fresh POIs:
    **161 → 208 POIs**. Domain distribution moved from {economic: 1, higher_ed: 54} to
    **{economic: 32, higher_ed: 70, metro_commercial: 88, healthcare: 18}**.

    Three classifier bugs were found and fixed during this work (all regression-tested):
    (a) the merge dropped the `office`/`landuse` tag columns, silently sending office POIs to
    the commercial fallback; (b) `str(row.get(tag) or "")` returned the literal "nan" for
    float NaN (NaN is truthy), which forced ~121 untagged parks/gardens into the economic
    branch — fixed with a `_tag()` helper; (c) the education keyword "khoa " matched "nha khoa"
    (dentistry) and was removed.

    Effect on pilot metrics: mean SMCI_B moved from 0.0968 (commercial-proxy economic) to
    0.0845 (enriched economic), i.e. the proxy had been *inflating* SMCI. VIF(MAI) fell from
    ~19.7 to 16.0 and VIF(RAC) from ~21.6 to 15.8 — a richer economic domain is less redundant
    with RAC. Typology partition stayed 4-way and balanced (161/161/70/70). The 47 added POIs
    have a manual spot-check sheet (`outputs/validation/economic_poi_spot_check.csv`).

    Honest caveat retained: this is still OSM-tag-derived opportunity, NOT employment counts.
    The economic domain is "formal-economy access proxy", strengthened but not a census. A
    full employment layer (Vietnam Enterprise Census, nighttime lights) remains future work.

    **Over-correction caught + fixed (2026-06-25, same day):** the first enrichment used
    `sqrt(area/1000)` for landuse polygons (cap 50) and `area/1000` for office footprints
    (cap 20), ignoring the type-density base weight when area was present. A domain-decomposition
    diagnostic (`scripts/mai_domain_decomposition.py`) showed the economic domain had jumped to
    **87.3% of MAI mass and was dominant in all 462 cells** — large industrial parks (weight up
    to 33.5) swamping point POIs (weight 0.2–1.0). Fixed by: (a) lowering industrial base density
    to 0.3 (factories employ few per m²); (b) recombining `weight = base_density × sqrt(area/2000)`
    capped at 5.0, so a 1 ha office outweighs a 1 ha factory and no single polygon dominates.
    Economic MAI-mass share dropped to a plausible 54.1% (economic + commercial = formal economy),
    with higher_ed 24.7%, commercial 15.5%, healthcare 5.8%. Economic-inclusion sensitivity is
    unchanged (κ=0.865), confirming the rebalance did not disturb the typology partition.
    See `outputs/validation/mai_domain_decomposition.md`.

19. **DEC-019 — Supply-side population is integrated INTO MAI (2026-06-27), not just reported post-hoc.**
    Previously WorldPop was verified and aggregated (`data/interim/grid_worldpop.csv`) but
    population only entered analysis after the fact: `MAI_B_popweighted` and
    `scripts/compute_population_weighted_smci.py` weight already-computed SMCI by residents at
    the *origin* cell (a demand-side equity aggregate, kept as sensitivity). MAI itself was a
    pure opportunity-count/footprint proxy — the caveat a JTG reviewer would attack first.

    **Decision:** scale each POI's opportunity weight by the residential density of the grid
    cell *containing* that POI (supply-side: an opportunity sited in a denser catchment serves
    a larger market and is a more relevant metropolitan opportunity). This complements the
    building-footprint magnitude proxy (#18); it does not replace it. Applied to **all four
    domains** (user decision 2026-06-27) — simple, defensible, less arbitrary than per-domain
    scoping.

    Formula (`population_supply_multiplier`, `src/accessibility_inputs.py`):

    ```text
    m_j = clip( sqrt(pop_density_j / median(pop_density>0)), 0.5, 2.0 )
    poi_opp_weight_eff_j = poi_opp_weight_j * m_j
    ```

    The SAME effective weights flow into `mai_moto`, `mai_a`, and `mai_b`, so the
    `RAC_opp = MAI_transit / MAI_motorcycle` ratio stays internally consistent. The unweighted
    `poi_opp_weights` is retained for the no-pop sensitivity run (`--no-pop-weighting`).

    **Lessons from #18 baked into the design** (to avoid re-triggering single-domain
    over-domination): (a) `sqrt` damps the signal; (b) median-centering keeps a typical-density
    POI at multiplier ≈1.0, so weights are not globally inflated/deflated; (c) hard bounds
    [0.5, 2.0] cap any single POI's population leverage at 2×. Pilot multiplier range came out
    [0.50, 1.81], mean 0.98 (193/208 POIs matched to a cell).

    **Effect (merged 208-POI primary):** mean SMCI_B 0.0845 → 0.0881 (+4%); SMCI_A 0.0405 →
    0.0497; share improved 67.1%. MAI domain shares **unchanged** (economic 54.1 / higher_ed
    24.7 / commercial 15.5 / healthcare 5.8) — population scales all domains proportionally and
    does not reintroduce domination. Typology partition stayed balanced (160/160/71/71).
    No-pop sensitivity: **κ=0.976**, only 8/462 cells relabelled — typology highly robust.
    VIF is essentially unchanged (MAI≈20.2, RAC≈22.8) because population scales MAI and the
    RAC_opp numerator proportionally; it neither worsens nor cures the structural MAI/RAC
    collinearity, so RAC_time-only remains the VIF remedy (#3). Full report:
    `outputs/validation/population_supply_weighting_sensitivity.md`.

    Note the two population uses are now distinct and both retained: **supply-side** (this
    decision, baked into MAI, affects SMCI/typology) vs **demand-side** (`MAI_B_popweighted` /
    `compute_population_weighted_smci.py`, residents at origin, equity aggregate, sensitivity only).

20. **DEC-020 — RAC_time is opportunity-weighted and auditable (2026-06-27).**
    To remove ambiguity, `RAC_time_raw_i` is now defined as:

    ```text
    motorcycle opportunity-weighted mean travel time /
    walk-transit opportunity-weighted mean travel time
    ```

    The time mean uses the same metropolitan opportunity set, domain weights, POI opportunity
    weights, and 60-minute cutoff as MAI. Unreachable origins receive the cutoff. The pipeline
    writes `moto_mean_opp_time_min`, `wt_A_mean_opp_time_min`, and `wt_B_mean_opp_time_min`
    for auditability. Network B timing remains a 2018 GTFS stop-proxy; Network C timing uses
    pseudo-GTFS stop routing.

    Effect on current pilot metrics: mean SMCI_A=0.0322, mean SMCI_B=0.0435, 298/462 cells
    improved, 88 unchanged, and 76 declined slightly because time competitiveness can fall
    when added walk-transit reachable opportunities are slower than motorcycle-weighted access.
    This is more conservative than the earlier simple reachable-time mean and should be used
    for JTG submission.

21. **DEC-021 — MAI uses a strict source-backed opportunity hierarchy (2026-06-28; extended 2026-06-29).**
    MAI remains a four-domain Metropolitan Opportunity Accessibility measure, but destination
    weights now support direct observed/source-backed magnitudes before falling back to proxies.
    The hybrid hierarchy is: observed facility magnitude → building/area-derived proxy → tag base
    proxy. The strict hierarchy (`--opportunity-basis observed_strict`) uses only source-backed
    magnitudes or explicit POI exclusions; it does not use tag-only proxy fallback. Provenance is
    carried per POI (`opportunity_source`, `obs_source_tier`, `obs_audit_status`) and summarized per
    cell as observed-coverage shares.

    Observed transforms are within-domain and capped to avoid re-triggering Decision #18
    over-domination:

    ```text
    healthcare: weight = clip(obs_beds / 50,        0.4, 30.0)
    higher_ed:  weight = clip(obs_enrollment / 1000, 0.5, 20.0)
    economic:   weight = clip(obs_jobs / 500,        0.1,  5.0)   ← ref=500 to prevent KCN domination
    commercial: weight = clip(obs_retail_gla_m2 / 1000, 0.1, 25.0)
    ```

    The economic `ref=500` and `cap=5.0` are calibrated so that a typical SME cluster
    (50–500 jobs) lands in [0.1, 1.0] and a large industrial park (30,000 jobs) hits the cap
    rather than flooding the domain (lesson from #18). This keeps the economic domain total weight
    ratio at ~1.7x proxy, comparable to healthcare (~2.1x) and education (~1.1x).

    Source tiers: `observed_point` (named citable source), `observed_derived` (area/level
    derivation), `official_source`, `facility_source`, `geometry_measured`,
    `observed_dasymetric_weak` (density/disaggregation — must be disclosed in Methods as
    interpolation, not point truth), and `excluded_not_destination`. `proxy_area`/`proxy_tag`
    remain only for the proxy and hybrid sensitivity baselines.

    `--opportunity-basis proxy` reproduces the pre-#21 baseline exactly.
    `--opportunity-basis observed` applies the hybrid hierarchy. `--opportunity-basis
    observed_strict` applies the source-backed hierarchy and raises if any included POI still lacks
    a source-backed magnitude.

    **Full four-domain coverage achieved 2026-06-29 (`scripts/derive_all_observed.py`):**
    - tertiary_healthcare: **18/18 = 100%** (1 named hospital, commune-station MOH standard, area-derived)
    - higher_education: **70/70 = 100%** (MOET class-size standards by school type)
    - economic: **32/32 = 100%** (employment density × area by sector; point estimates for banks/markets)
    - metro_commercial: **81/81 included = 100%** (retail/GLA-derived plus measured
      park/leisure/agrarian polygon magnitudes; 7 point-only service/transport listings excluded
      from MAI with audit reasons)

    Strict observed gate (2026-06-29): `needs_source=0`, `proxy_source_tiers=0`; audit table:
    `data/interim/poi_observed_audit.csv`. After Decision #22 promoted RAC_time as primary
    and Decision #23 promoted the 1200 m NAI threshold, observed-vs-proxy sensitivity gives
    proxy SMCI_B 0.0163 → strict observed 0.0160, κ=0.9245, 24/462 cells relabelled,
    Spearman ρ=0.9950, VIF(MAI)=3.78, and VIF(RAC)=2.00. Report:
    `outputs/validation/observed_vs_proxy_sensitivity.md`.

22. **DEC-022 — RAC_time promoted to primary after reviewer-risk metric audit (2026-06-29).**
    A red-team metric audit tested NAI diversity, category-capped NAI, RAC_time-only,
    RAC_opp-only, winsorized/log normalization, additive SMCI, absolute-threshold
    typology, alternative MAI weights, alternative decay windows including exponential
    decay, top-1%/top-5% opportunity leverage, and strict-excluded-POI spatial missingness.
    Output: `outputs/validation/metric_variant_audit.md`.

    The audit selected `rac_time_only` for promotion because it directly fixes the
    MAI/RAC_opp double-counting risk. With the 1200 m / 15 min NAI threshold, max VIF
    drops from 10.04 under the legacy full-RAC composite to 3.82, while preserving the
    prior classification well (κ=0.9116, Spearman ρ=0.9824, 28/462 cells relabelled).

    Implementation: `src/pilot.py` now sets primary `RAC_A/B = RAC_time_A/B`. The
    previous full composite is retained as `RAC_full_A/B` and
    `SMCI_B_full_rac_legacy` for robustness reporting. The promoted primary strict
    observed headline is SMCI_A=0.0092, SMCI_B=0.0169, mean Delta_SMCI=0.0077,
    298/462 cells improved, 33 unchanged, 131 declined, and Scenario B typology counts
    are 170 Integrated Capability, 61 Fragmented Capability, 61 Transit-Dependent,
    and 170 Motorcycle Lock-in.

23. **DEC-023 — NAI primary threshold is 15 minutes / 1200 m (2026-06-30).**
    The neighborhood walking threshold is promoted from the earlier 800 m / ~10 min pilot
    setting to 1200 m network distance, equivalent to 15 minutes at 80 m/min. This aligns the
    NAI axis with the 15-minute-city framing used in the literature while preserving the
    same count-based NAI logic.

    **Status update 2026-07-01:** Superseded by Decisions #26 and #27. After professor feedback,
    1200 m is no longer the primary threshold: Decision #27 selects 800 m (10-minute neighborhood)
    as primary and demotes 1200 m to an optimistic 15-minute-city upper-bound sensitivity.

    Implementation: `scripts/build_accessibility_inputs.py --walking-threshold-m` defaults
    to 1200, and network-mode builders pass `walk_cutoff_min=15.0`. Sensitivity/audit scripts
    that rebuild NAI now default to the same 15-minute cutoff. The excluded-POI missingness
    audit retains its 800 m buffer because that is a separate spatial-audit radius, not the
    NAI threshold.

    Effect on current strict observed + RAC_time primary metrics: mean NAI rises to 13.47,
    zero-NAI cells fall to 33/462 (7.1%), SMCI_A=0.0092, SMCI_B=0.0169, and 298/462 cells
    improve under Scenario B. The change makes zero-access claims less overstated and more
    defensible for a paper using a 15-minute neighborhood concept.

24. **DEC-024 — Prior weights checked using UTM-Hanoi survey dataset (2026-06-30).**
    The composite MAI's prior domain weights (0.40 economic, 0.20 higher_education,
    0.20 tertiary_healthcare, 0.20 metro_commercial) were checked against the UTM-Hanoi
    transport-policy perception dataset (`N=26,106`, doi:10.1038/s41597-024-02950-9).

    The raw counts for primary trip purposes are: work (15,145 / 58.0%), education
    (4,494 / 17.2%), visit (3,176 / 12.2%), shopping (1,922 / 7.4%), leisure
    (934 / 3.6%), and caring (435 / 1.7%). The strict MAI-domain mapping used by
    `scripts/derive_mai_weights_utm.py` maps work→economic, education→higher_education,
    shopping→metro_commercial, caring→tertiary_healthcare, and excludes leisure/visit before
    renormalization. It yields `utm_derived` weights: economic 0.6885, higher_education 0.2043,
    tertiary_healthcare 0.0198, metro_commercial 0.0874.

    The decision is to retain the smoothed prior weights (0.40/0.20/0.20/0.20) as default
    rather than adopting raw revealed-demand weights. This represents a normative approach to
    accessibility (need across multiple daily functions) rather than revealed-demand weighting,
    which is endogenous to current employment concentrations. The UTM-derived scheme is kept
    as sensitivity evidence and an audit trail, not promoted to the primary specification.

25. **DEC-025 — Comparison site (planned vs unplanned) is a Paper #2 design, not a pilot add-on (2026-06-30).**
    A matched control site — Trâu Quỳ town, Gia Lâm (organic/unplanned settlement) — is adopted
    to upgrade the design from single-site descriptive to a matched-pair spatial comparison
    against Ocean Park (master-planned). This is a *counterfactual control*, distinct from the
    "reproducibility appendix" that Decision #1 deliberately cut: the purpose is to test the
    green/planning dimension (Decision #9), not to re-run the same kind of site.

    Locked design choices (full protocol: `docs/comparison_site_protocol.md`):
    - **Headline comparison uses Scenario A (no VinBus) for BOTH sites** so "planning" is not
      entangled with "the private bus line"; VinBus's marginal value stays a separate layer
      (Ocean Park ΔSMCI).
    - **Match on network distance-to-CBD over the actual Red River bridges** (±15%), area, bearing,
      and density; report every unmatched variable as a limitation. Road structure is expected to
      differ (it is part of the treatment) and is reported, not matched away.
    - **Cross-site comparison uses absolute SMCI/RAC or shared-scale pooled normalization**, NOT
      within-site typology shares (which are rank-relative — same caveat as Decision #11 shared-scale).
    - Sites rejected: Đa Tốn (inside the Ocean Park footprint), Kiêu Kỵ/Bát Tràng (too small,
      adjacent → spillover; Bát Tràng's pottery monoculture is non-representative).
    - Claim discipline: n=2 observational → report capability-surface *differences*, do NOT claim
      the master plan *causes* them.
    Bottleneck flagged: observed-opportunity magnitudes (Decision #21) must be rebuilt from scratch
    for the control site; this is the most labor-intensive step and the main coverage-bias risk.

26. **DEC-026 — NAI threshold must be localized, not imported from European 15-minute-city defaults (2026-07-01).**
    Professor feedback challenged the 1200 m / 15-minute walking catchment as too optimistic for
    Hanoi's tropical, motorcycle-dominant walking environment. Heat, humidity, sidewalk obstruction,
    crossing stress, shade availability, and motorcycle interaction mean that 15 minutes of nominal
    network distance may not represent the same pedestrian burden as in European 15-minute-city
    applications.

    Decision: retain the 15-minute city as a conceptual local-completeness frame, but demote
    1200 m from "settled primary threshold" to "upper-bound sensitivity" until a threshold-response
    audit is run. The audit must rebuild NAI and downstream metrics at 600 m, 800 m, 1000 m, and
    1200 m, then report zero-NAI cells, mean SMCI_A/B, Delta_SMCI, typology stability, and policy
    interpretation changes.

    First audit (`scripts/nai_threshold_sensitivity.py`, 2026-07-01):
    - 600 m: zero-NAI 133/462 (28.8%), mean NAI 3.56, mean SMCI_B 0.0107, kappa vs 1200 m 0.718.
    - 800 m: zero-NAI 88/462 (19.0%), mean NAI 6.09, mean SMCI_B 0.0133, kappa 0.756.
    - 1000 m: zero-NAI 58/462 (12.6%), mean NAI 9.47, mean SMCI_B 0.0148, kappa 0.837.
    - 1200 m: zero-NAI 33/462 (7.1%), mean NAI 13.47, mean SMCI_B 0.0169.

    Result: the VinBus/SMCI improvement direction survives stricter thresholds, but local
    completeness and typology labels are materially threshold-sensitive. This supports reporting
    1200 m as the optimistic upper bound and selecting a final primary cutoff on Hanoi walking
    plausibility.

    The final primary threshold should be selected based on Hanoi-sensitive plausibility and
    robustness, not on a mechanical conversion of 15 minutes at 80 m/min. If the headline insight
    holds across stricter catchments, that becomes stronger evidence. If it changes materially,
    the paper should foreground that the megaproject's apparent neighborhood completeness depends
    on an optimistic walking assumption.

27. **DEC-027 — Primary NAI threshold selected at 800 m (10-minute neighborhood) (2026-07-01).**
    Following the Decision #26 audit and professor feedback, the primary NAI walking catchment is
    set to **800 m network distance (~10 min at 80 m/min)**. 1200 m / 15 min is demoted to an
    optimistic upper-bound sensitivity.

    Rationale:
    - **Convention.** 800 m is the international "10-minute neighborhood" pedestrian shed
      (¼–½ mile walk-to-transit), whereas "15-minute city" is a multi-modal (walk+bike) frame;
      applying its 15-minute budget to walking alone stretches the catchment by cycling speed and
      mislabels it. 800 m has a walking-specific basis; 1200 m-walking does not.
    - **Vietnam evidence.** HCMC/Vietnam pedestrian-shed literature uses 800 m ≈ 10 min at 1.3 m/s
      as the urban walk catchment (HAIDEP raw trip-length is behind JICA licensing — see
      `docs/metrics_reference.md` — so 800 m is anchored on published Vietnam pedestrian-shed work,
      not HAIDEP directly). For a motorcycle-dependent city with low willingness-to-walk, 800 m is a
      generous-but-defensible walk radius; 1200 m is not.
    - **Robustness.** The four-typology structure is near-invariant across 600–1200 m (quadrant
      counts 174/57/57/174 → 171/60/60/171 → 174/57/57/174 → 170/61/61/170), so the headline does
      not hinge on the exact catchment — only the absolute SMCI level and zero-NAI share move.

    New primary metrics (strict observed + RAC_time primary, 800 m NAI):
    SMCI_A=0.0070, SMCI_B=0.0133, mean Delta_SMCI=0.0063, 281/462 improved (60.8%),
    88 unchanged, 93 declined; zero-NAI=88/462 (19.0%), mean NAI=6.09, median NAI=4;
    zero-SMCI_B=88; positive-SMCI median 0.0051→0.0081; typology_B counts
    171 Integrated Capability, 60 Fragmented Capability, 60 Transit-Dependent,
    171 Motorcycle Lock-in. Primary VIF stays well under 5 (NAI=2.26, MAI=2.93, RAC=2.05);
    legacy full-RAC remains high (MAI=9.58, RAC=9.56) and is reported as robustness only.

    Implementation: `scripts/build_accessibility_inputs.py --walking-threshold-m` defaults to 800;
    all sensitivity/audit scripts that rebuild NAI now use `walk_cutoff_min=800/80` as their primary
    baseline; `scripts/nai_threshold_sensitivity.py --reference-threshold-m` defaults to 800. The
    800 m primary reproduces `data/interim/nai_threshold_sensitivity/inputs_800m.csv` exactly
    (max abs diff 0 across all numeric columns).

28. **DEC-028 — Tay Mo / Vinhomes Smart City is a candidate west-side extension, not a replacement for the east-side control (2026-07-01).**
    The proposed Tay Mo extension is methodologically attractive because it can turn the design
    into a **double pairwise comparison**:

    - East: Vinhomes Ocean Park (planned) vs Trau Quy core (organic).
    - West: Vinhomes Smart City (planned) vs Tay Mo core (organic).

    This would test whether the planned-versus-organic capability contrast appears on both sides
    of Hanoi, rather than only around Ocean Park. It also strengthens the policy narrative from
    "one green megaproject case" toward "east-west megaproject enclave pattern."

    Status: **candidate extension only**. The user-proposed matching claims for Tay Mo (distance
    to Hoan Kiem, area, population, density, and spillover independence) must be measured with the
    same pipeline before they appear as paper facts. Use network distance over the routable OSM
    drive graph, not straight-line distance; aggregate population from WorldPop and/or official
    ward data; and separate the inherited Tay Mo core from Vinhomes Smart City cells.

    Guardrail: do not collapse Tay Mo and Smart City into one study surface. The whole point is
    the local planned/organic contrast. Mixed boundary cells should be flagged, dropped, or analyzed
    as a transition band.

    Full pre-analysis protocol: `docs/western_extension_protocol.md`.

29. **DEC-029 — 800 m NAI threshold reframed as an operational assumption, not a
    validated local standard (2026-07-27).** A literature review (OpenScience agent
    against a disposable repo clone, via a local OpenAI-compatible 9router endpoint)
    checked whether Hanoi/HCMC evidence supports 800 m as an empirically optimal
    neighborhood walking cutoff. DOIs were spot-verified against publisher/Crossref
    records before acting on this review.

    Findings: no identified Hanoi or Ho Chi Minh City study directly establishes
    800 m as an empirically optimal walking distance. Hanoi evidence (Phuong et al.
    2024, `10.1016/j.iatssr.2024.07.001`; Hoang-Tung et al. 2021,
    `10.1016/j.cstp.2020.10.002`; Nguyen et al. 2020, `10.3390/su12145773`) shows
    walking acceptability depends on street conditions, safety, transit quality, and
    motorcycle competition, not a fixed radius. Comparator evidence from
    motorcycle-taxi-dominant Bangkok (Pongprasert & Kubota 2017,
    `10.1016/j.iatssr.2017.03.003`; 2019, `10.1007/s40534-018-0170-1`) finds typical
    station-access walking distances clustering around 428-500 m, with a sharp shift
    to motorcycle-taxi use beyond 500 m. Tropical sun exposure adds measurable
    perceived walking cost even with shade (Melnikov et al. 2022,
    `10.1038/s41598-022-06383-5`).

    Decision: retain 800 m as primary — it remains a transparent, arithmetic 10-min
    x 80 m/min operational catchment, and the project's own 600-1200 m
    threshold-response audit (Decision #27) shows the four-typology structure is
    near-invariant across that range. But the proposal's prior wording overclaimed
    it as following an "international 10-minute-neighborhood pedestrian shed" and
    "Vietnam/HCMC pedestrian-shed literature" at the exact 800 m value — neither
    claim is literature-supported. `proposal/proposal_v7.md` Section 8.1, Section
    10, and Section 13 are reworded to describe 800 m as an operational assumption
    bounded by an explicit 600/1000/1200 m sensitivity range, not a validated local
    standard. No change to any computed metric, threshold value, or code.

30. **DEC-030 — Motorcycle speed calibration citations for primary/secondary/
    tertiary/residential road classes retracted as unverifiable; values retained
    as transparent modeling assumptions (2026-07-27).** A forensic citation
    audit (OpenScience agent, read-only, DOI/Crossref/publisher spot-checked)
    found that the two sources previously cited in
    `data/raw/motorcycle_speed_calibration.csv` for non-arterial road classes do
    not verifiably exist as cited:

    - "Nguyen Xuan Long & Nguyen Hoang Tu (2018), *Journal of the Eastern Asia
      Society for Transportation Studies* 12: 1421-1435" — the claimed page
      range in that EASTS volume belongs to two unrelated papers (Yen et al.,
      pp. 1414-1433; Fukumoto et al., pp. 1434-1447). No matching title, author
      pairing, or DOI was found in J-STAGE, Crossref, Google Scholar, or
      Semantic Scholar.
    - "Vu Anh Tuan et al. (2016), 'Motorcycle Traffic Characteristics in
      Hanoi', *Transportation Research Procedia* 15: 651-662" — the claimed
      page range in that volume belongs to two unrelated papers (Riggins et
      al., pp. 640-651; Ackaah & Bogenberger, pp. 652-663). No matching
      record or DOI was found.

    Decision: do not delete or silently keep these citations. The
    `primary`, `secondary`, `tertiary`, and `residential` rows in
    `data/raw/motorcycle_speed_calibration.csv` now carry an explicit
    `UNVERIFIED CITATION` provenance note referencing this entry instead of
    the retracted citations. Numeric speed/multiplier values are **unchanged**
    — this is a provenance-label correction, not a recalibration, so no
    pipeline rerun, headline number, or test was affected. `paper/paper_draft.md`
    Section 5.5 and Table 1 now describe these road classes as
    literature-informed modeling assumptions rather than directly cited
    literature values; only the `motorway`/`trunk` (JICA HAIDEP 2010) rows
    remain a literature-cited calibration.

    Follow-up (not yet done): search for a verifiable primary/secondary/
    tertiary/residential motorcycle-speed source for Hanoi or comparable
    Vietnamese cities. If found, update the CSV, paper Section 5.5, and this
    decision together in one commit. If a systematic replacement search is
    unsuccessful, consider widening `scripts/motorcycle_speed_sensitivity.py`
    bounds to reflect assumption uncertainty explicitly, and describe the
    calibration as scenario-based rather than literature-calibrated.

    **Full forensic verdict (2026-07-27, second audit by OpenScience agent):**
    All 10 CSV road classes are now classified as transparent assumptions:

    - `motorway`/`trunk` (JICA HAIDEP): HAIDEP (final March 2007, not 2010)
      provides road *design* speeds (100/80/60/40 km/h), not observed
      motorcycle travel speeds. No Table 5-3 or motorcycle observation
      confirmed. JICA removed as calibration source.
    - `living_street` (TCVN 9817:2013): that standard covers X-ray
      fluorescence analysis of iron ore and has no road or speed provisions.
      Citation retracted.
    - `DEC-005` and `DEC-006` partially superceded; lane-splitting mechanism
      not directly evidenced by any audited source.

    Verified replacement evidence (Son, Zhang & Fujiwara, 2012, DOI
    10.7763/IJESD.2012.V3.257): 65 Hanoi motorcycle GPS users, 2011;
    highway 36.6/48.5 km/h (peak/non-peak), arterial 16.2/33.6 km/h,
    residential 23.5/26.7 km/h. These are broad ranges, not OSM-class values.
    The paper provides plausibility bounds only; OSM-class mapping remains
    an unverified assumption. Added as `data/raw/motorcycle_speed_calibration.csv`
    context for `motorway`, `trunk`, `residential` rows.

    Minh, Sano & Matsumoto (2005, DOI 10.11175/easts.6.186): maneuver-specific
    passing-event speeds on motorcycle-lane/undivided Hanoi roads; not
    representative road-class means. Not used.

    Son et al. reference entry for paper/proposal:
    Son, H. T., Zhang, J., & Fujiwara, A. (2012). Developing a toolbox for
    calculating motorcycle emission and the difference of CO2 from motorcycle
    for each type of road in Hanoi. *International Journal of Environmental
    Science and Development, 3*(5), 412-416.
    https://doi.org/10.7763/IJESD.2012.V3.257

31. **DEC-031 — Production calibration is mandatory; motorcycle robustness uses primary global ±20% scenarios (2026-07-27).**
    The canonical network build now hard-fails when `data/raw/motorcycle_speed_calibration.csv`
    is absent; implicit `src/calibration.py` defaults remain library/test behavior only. The
    pipeline DAG declares the CSV and DEC-030 as dependencies, and the loader validates positive
    finite values plus `motorcycle_speed_kph = base_speed_kph × multiplier`.

    The prior speed-sensitivity artifact used proxy POIs and selective mechanism-labelled factors,
    so its baseline did not reproduce the promoted strict-observed primary. It is replaced by
    neutral global factors 0.80/1.00/1.20 applied to all calibration rows with
    `opportunity_basis=observed_strict`. The rerun baseline reproduces mean SMCI_B=0.0132898 and
    281/462 higher modeled values. Mean SMCI_B is 0.0167250 at −20% speed and 0.0110446 at +20%;
    typology is unchanged in both (kappa=1.000; 0 relabelled).

    Ten OD model times are now regenerated from the production graph and CSV before comparison
    with unchanged manual Google Maps observations. The report records calibration SHA-256 and
    routing metadata. Diagnostics are MAE=1.90 min, MAPE=22.19%, MBE=-1.04 min, RMSE=2.20 min;
    these are a small-sample plausibility check, not external calibration validation. The
    3-minute threshold is explicitly project-defined, not a literature standard.

32. **DEC-032 - Spatial diagnostics are additive validation layers, not changes to the SMCI baseline (2026-08-03).**
    Local Moran's I (LISA), boundary-permeability diagnostics, and a building-constrained
    dasymetric population sensitivity are added to strengthen the spatial interpretation of the
    Ocean Park pilot. None changes NAI, MAI, RAC, MCS, SMCI, typology, shared Scenario A/B
    normalization, or canonical headline metrics.

    The LISA protocol runs Global Moran's I and Local Moran's I for `SMCI_B`, `Delta_SMCI`,
    `NAI`, `MAI_B`, and primary `RAC_B` using 9,999 permutations, fixed seed 2026,
    row-standardized Queen weights, and Benjamini-Hochberg FDR correction. Rook and 8-nearest-
    neighbour weights are mandatory sensitivities. LISA supports claims about spatial clustering,
    not causal effects of the Ocean Park boundary.

    Permeability uses Network A and Network D only. It reports graph-edge crossings, access/barrier
    tag flags, near-boundary network-to-Euclidean detours, and fixed-seed approximate edge
    betweenness. Missing OSM restriction tags are explicitly treated as missing evidence, not proof
    of open access. The first run finds 59 walking and 31 motorcycle physical crossings, with
    median detours of 2.10 and 2.36 respectively for 39 paired near-boundary cells.

    Dasymetric allocation redistributes WorldPop only within source pixels in proportion to
    intersecting VIDA footprint area, with an area fallback for pixels without a footprint. It
    conserves the pilot total population to floating-point precision (-0.0003 people) and is used
    only for population-weighted SMCI and typology exposure sensitivity. It is not a residential
    building population estimate because footprints lack use, height, floor area, and occupancy.

33. **DEC-033 - Geometric-mean SMCI is the primary reporting scale (2026-08-10).**
    SMCI is reported as the equal-weight, per-cell geometric mean of normalized NAI, MAI, and
    RAC. The legacy product is retained in processed outputs for auditability. The two operators
    preserve zero cells and ordinal rankings exactly, so their comparison is a scale transition,
    not a robustness test. Additive SMCI remains the compensatory robustness specification and
    the minimum component remains an extreme bottleneck diagnostic. Typology remains based on
    rank-split NAI and MCS, so it is independent of the SMCI reporting operator.

# Decision Log

Why things are the way they are — read this before changing the methodology,
so settled debates don't get silently re-opened.

1. **Single case study (Vinhomes Ocean Park only), not two.**
   A second site (Vinhomes Smart City) was proposed as a "reproducibility
   appendix" in an earlier draft and was cut. Running a second full site
   roughly doubles data collection and computation; explicitly deferred to
   future work to keep this feasible as one paper/thesis.

2. **Classification is theory-first (median split), not pure k-means.**
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

3. **MAI and RAC are expected to be collinear — this is structural, not just empirical.**
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

4. **Do NOT use a geometric-mean alternative to validate the multiplicative SMCI.**
   SMCI_geo = (NAI*MAI*RAC)^(1/3) is a monotonic transform of
   SMCI_mult = NAI*MAI*RAC. Spearman rank correlation between them is
   mathematically guaranteed to be 1.0 — this was caught by actually
   running the numbers (pilot, 2026-06-21), not by reading the proposal
   text. Use the ADDITIVE alternative, (NAI+MAI+RAC)/3, for the real
   robustness comparison. See tests/test_accessibility.py::test_geometric_mean_check_is_vacuous.

5. **Motorcycle travel time is NOT the same as default OSM driving speed.**
   Lane-splitting means motorcycles are often faster than cars in
   congested Hanoi traffic. Network D must apply a literature-derived
   speed-adjustment factor, not assume car-equivalent speeds.

6. **Validation against Google Maps is secondary, not foundational.**
   Literature-calibrated motorcycle speeds are the primary basis for
   Network D travel times, specifically because Google's programmatic
   TWO_WHEELER routing is unconfirmed for Vietnam (see docs/data_sources.md).
   The model must not depend on an API that may not cover the study area.

7. **NAI is count-based; MAI is magnitude-weighted.**
   A single OSM POI can represent an office tower or a kiosk. For daily
   neighborhood activities, presence/proximity matters more than size, so
   NAI counts facilities. For metropolitan opportunities (jobs, enrollment),
   volume is the conventional definition of "opportunity," so MAI uses
   proxy magnitudes (employment proxy, enrollment proxy, density score),
   not raw POI counts.

8. **Why "electric bus" stays in the language even though propulsion type
   doesn't affect the accessibility math.**
   The green-vs-motorcycle-dependent tension is the paper's core hook
   (title, Introduction). Stripping "electric" to "transit intervention"
   would weaken that framing. Instead, Methods states explicitly that the
   intervention is evaluated through accessibility effects (routes, stops,
   connectivity), not propulsion or emissions effects — keeps the framing
   without overclaiming what the analysis measures.

9. **The "green" dimension must be tested, not assumed.**
   NDVI and green-space accessibility are explicit variables (src/, Section
   3.5), and the Discussion plan explicitly asks whether they relate to
   SMCI/RAC at all — the paper should be able to say honestly if "green"
   turned out to be branding rather than a substantive driver.

10. **2018 Hanoi GTFS is treated as the pre-VinBus conventional transit baseline, not a data gap.**
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

11. **Scenario A/B deltas must use shared normalization bounds.**
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

12. **Building footprints are the next data upgrade before stronger MAI claims.**
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

13. **Overture Places supplements OSM POIs; it does not replace them.**
    Overture Places can increase POI coverage and provide an independent source,
    but coverage varies by market and category. The planned workflow is a union
    of OSM and Overture with source-agreement labels: OSM+Overture agreement =
    higher confidence; one-source-only records = targeted spot-check candidates.

14. **Check maintained GTFS catalogs before final Network B wording.**
    `scripts/check_mobility_database.py --query Hanoi` checked the maintained
    MobilityDatabase CSV and found no Hanoi candidate feed in the catalog. This
    supports keeping the 2018 World Bank feed as the available pre-VinBus baseline,
    but final Methods should still mention that MobilityDatabase was checked and
    manually inspect TUMI/Datahub or official local sources before submission.

15. **MAI is "Metropolitan Opportunity Accessibility", not "employment accessibility".**
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

16. **VinBus headway assumption is 15 min (published schedule); sensitivity confirms it is not a material driver.**
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

17. **VinBus stop-level routing is primary; corridor proximity is sensitivity only.**
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

18. **Economic domain escaped from pure commercial-density proxy via OSM landuse + office tags (2026-06-25).**
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

19. **Supply-side population is integrated INTO MAI (2026-06-27), not just reported post-hoc.**
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

20. **RAC_time is opportunity-weighted and auditable (2026-06-27).**
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

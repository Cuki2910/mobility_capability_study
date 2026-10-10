# CLAUDE.md

Context file for Claude Code (or any future session) working in this repo.
Read this fully before writing or changing code or the proposal.

## Authority and change review

This file describes the working/published baseline, not constraints on future ideas. The user's latest direction supersedes older methodology instructions and plans. Old prompts and plans are retained in Git history; proposed unfinished work lives in `docs/roadmap.md` and is not adopted methodology. Prepare requested changes, update affected implementation and tests, then present `.agent/change_review.md` and request confirmation after each batch. Keep status `PENDING_USER_CONFIRMATION` until the user replies; passing checks does not ratify a design. Never revert to an old idea just to satisfy stale instructions. Separate draft methods, published results, and dated history.

## What this project is

Research proposal + analysis pipeline for: *"Fragmented Mobility Capability
in Motorcycle-Dependent Green Megaprojects: A Dual-Scale and
Mode-Competitive Accessibility Framework from Vietnam"* (target: Journal of
Transport Geography). Case study: Vinhomes Ocean Park, Hanoi.

**Core hypothesis:** High neighborhood accessibility alone is insufficient
to generate integrated sustainable mobility capability when Relative
Accessibility Competitiveness (RAC) — walking-and-transit accessibility
relative to motorcycle accessibility â€” remains low.

Full methodology: `proposal/proposal_v7.md` (Markdown, the only retained proposal). This CLAUDE.md is a map to
the repo and a record of decisions, not a replacement for reading Sections 7-10
of the proposal before touching the analysis code.

## Glossary (used everywhere in code â€” match these names exactly)

| Term | Meaning |
|---|---|
| **NAI** | Neighborhood Accessibility Index â€” count-based, walking threshold |
| **MAI** | Metropolitan Accessibility Index â€” magnitude-weighted, walk+transit threshold |
| **RAC** | Relative Accessibility Competitiveness - primary uses RAC_time; legacy full-RAC = geometric mean of RAC_time and RAC_opp retained as robustness |
| **MCS** | Metropolitan Competitiveness Score â€” geometric mean of normalized MAI and RAC; used for classification only |
| **SMCI** | Sustainable Mobility Capability Index = (NAI_norm × MAI_norm × RAC_norm)^(1/3), the primary equal-weight geometric mean; legacy product retained for audit |
| **Network A/B/C/D** | Walking / Walking+existing transit / Walking+existing transit+VinBus / Motorcycle |
| **Scenario A/B** | A = Networks A+B (no VinBus). B = Networks A+C (with VinBus). ΔSMCI = SMCI(B) − SMCI(A) |
| Four typologies | Integrated Capability, Fragmented Capability, Transit-Dependent, Motorcycle Lock-in |

Exact formulas: `src/accessibility.py` (implemented, tested) â€” this is the
single source of truth for these formulas, not the proposal prose.
If you change a formula, update both the code and corresponding methods of the
proposal in the same commit.

Scenario A/B comparisons use shared A+B normalization bounds in `src/pilot.py`.
Do not compute Delta_SMCI from separately normalized scenario scores.

## Number-consistency rule (IMPORTANT)

When any headline metric changes (SMCI_A/B, Delta_SMCI, improved/unchanged/declined
shares, typology counts, VIF, kappa/rho, zero-NAI counts, pytest count, POI counts),
update **every** place it appears in the same change — do not leave stale copies:

1. Re-run the generators, don't hand-edit outputs:
   `run_pilot_metrics.py` → `make_validation_report.py` → `make_supervisor_memo.py`
   → `project_self_audit.py` (memo/audit read CSVs; if you forget, they silently keep
   old numbers). For test count, run `pytest tests/` and use the actual pass count.
2. Update the prose copies by hand: CLAUDE.md "Current status" section + Known
   constraints, `proposal/proposal_v7.md` results, `docs/decisions.md`, and the
   relevant memory file(s) under the auto-memory dir (`pilot-current-numbers.md`).
3. Dated history lines (e.g. "Decision #19 ... Pytest: 70 tests pass") record what was
   true *then* — leave them; only fix current-facing/forward-looking numbers.
4. After editing, grep for the OLD value across the repo to confirm no stragglers.

## Repo structure

```
proposal/              proposal_v7.md is the only retained proposal (Markdown).
data/raw/               immutable, as-downloaded. Nothing in here is hand-edited.
data/interim/           cleaned/aligned data (calibrated networks, built grid).
data/processed/         analysis-ready per-grid-cell table (NAI, MAI, RAC, SMCI, typology).
src/                    reusable formulas and pipeline functions. Import, don't duplicate.
  accessibility.py        NAI/MAI/RAC/SMCI/classification formulas â€” DONE, tested.
  networks.py              network construction â€” implemented; loads GraphML, applies calibration.
  calibration.py           motorcycle speed calibration â€” implemented, cited from literature.
  validation.py            VIF check, validation helpers â€” DONE.
  routing.py               Dijkstra-based NAI/MAI/RAC inputs from GraphML â€” DONE.
  accessibility_inputs.py  proxy and network input builders â€” DONE.
scripts/                one-off executable scripts that call src/.
  fetch_osm_data.py        run on a machine with real internet access (NOT this sandbox).
notebooks/              exploratory work only. Promote anything reusable into src/.
tests/                  pytest. Run before trusting any change to src/accessibility.py.
outputs/                figures/tables/results for the paper. Gitignored except structure.
docs/
  data_sources.md          status of every data source â€” CHECK BEFORE ASSUMING DATA EXISTS.
  decisions.md             why things are the way they are â€” READ BEFORE CHANGING METHODOLOGY.
```

## Before doing anything else

1. Read `docs/data_sources.md`. VinBus OSM relations are confirmed (39 found); Hanoi GTFS is present as a 2018 pre-VinBus baseline for Network B.
2. Read `docs/decisions.md`. Several things that look like they could be
   "simplified" (theory-first classification, rank-based median split,
   single-site scope, the additive-not-geometric robustness check) were
   deliberately chosen after finding a problem with the alternative. Don't
   revert them without re-reading why.

## Running things

```bash
pip install -r requirements.txt

# On a machine with real internet access (this sandbox cannot reach OSM servers):
python scripts/fetch_osm_data.py
python scripts/fetch_hanoi_gtfs.py   # optional: rerun only if replacing the 2018 pre-VinBus baseline feed
python scripts/check_mobility_database.py --query Hanoi

# Pipeline (run in order):
# build defaults are now the canonical primary spec: --opportunity-basis observed_strict
# + --pois data/interim/merged_pois_observed.gpkg + --walking-threshold-m 800 (no need to
# pass them). Published results use the scale recorded in the headline snapshot. For the legacy proxy baseline
# pass BOTH `--opportunity-basis proxy --pois data/interim/merged_pois.gpkg`.
python scripts/build_accessibility_inputs.py --mode network --gtfs-status baseline_limited
python scripts/run_pilot_metrics.py
python scripts/make_validation_report.py
python scripts/make_supervisor_memo.py
python scripts/make_pilot_maps.py

# Sensitivity runs (no extra data needed):
python scripts/rac_scaling_sensitivity.py
python scripts/rac_time_only_sensitivity.py

# WorldPop aggregation (raster already local):
python scripts/aggregate_worldpop_by_grid.py
python scripts/compute_population_weighted_smci.py

# Requires internet — run on a real machine:
python scripts/fetch_building_footprints.py
python scripts/fetch_overture_pois.py
python scripts/merge_poi_sources.py   # after fetch_overture_pois.py

# Anywhere:
pytest tests/ -v   # report the actual result in the current change review
```

## Known constraints / gotchas

- **No internet access to OSM/Overpass from this sandbox.** Data-fetching
  scripts are written but must be run on a real machine.
- **VinBus has no official GTFS available.** Network C uses the already crawled
  and QC'd pseudo-GTFS from public VinBus API responses:
  `data/raw/vinbus_pseudo_gtfs_fixed/` (176 routes / 5,631 stops). Treat this
  as the primary Network C source; "official GTFS missing" does not mean the
  VinBus data collection is incomplete.
- **Google Maps TWO_WHEELER mode at the API level is unconfirmed for
  Vietnam** â€” don't design any step that depends on bulk/automated
  motorcycle routing via the API. See `docs/data_sources.md`.
  Manual spot-check template: `outputs/validation/manual_motorcycle_validation_template.csv`
  (10 pre-filled OD pairs with lat/lon for Ocean Park area).
- **Hanoi GTFS is present locally as a 2018 pre-VinBus baseline.** Network B is `baseline_limited` by vintage, not missing: stop geometry is used for stop_accessibility(), while timetable service is reported as a pre-intervention limitation.
- **theory_first_typology uses rank-based split**, not `>= np.median()`, to
  guarantee 4 typologies even when MCS has a mass point at 0. See decision #2.
- **MAI and RAC are expected to be correlated by construction** when RAC_opp is
  included, not just by chance — see decision #3. Always run VIF check
  (`src/validation.py::collinearity_check`) before trusting the 4-way
  classification on new data. Current primary RAC_time spec is below threshold
  (VIF(MAI)=2.93, VIF(RAC)=2.05 at the 800 m NAI primary); legacy full-RAC
  remains high (VIF(MAI)=9.58, VIF(RAC)=9.56) and is reported as robustness.
- **Current RAC primary (2026-06-29, Decision #22):** RAC_time is promoted to
  primary. Legacy full-RAC is retained as `RAC_full_A/B` and
  `SMCI_B_full_rac_legacy`. At the 800 m / 10 min NAI primary threshold
  (Decision #27), primary VIF(MAI)=2.93, VIF(RAC)=2.05; legacy full-RAC
  VIF(MAI)=9.58, VIF(RAC)=9.56.
- **Delta_SMCI must be shared-scale.** Scenario A/B normalization uses common
  A+B bounds for MAI, RAC subcomponents, and RAC composite before MCS/SMCI.
  Separate per-scenario min-max scaling produces artificial declines.
- **Building footprints are the next real data upgrade.** Use VIDA / Google Open
  Buildings / Microsoft / OSM footprints to separate built cells from lake/park
  cells and cross-check WorldPop before making strong MAI/population claims.
- **Overture Places supplements OSM POIs; do not replace OSM.** Use union plus
  source-agreement labels for confidence and spot-check sampling.
- **Motorcycle speed assumptions** are explicit scenario-calibrated values, not verified
  OSM-class literature estimates. Son et al. (2012) provides broad Hanoi GPS speed ranges
  for highway/arterial/residential contexts; mapping those ranges to OSM classes remains
  an assumption. JICA HAIDEP and two miscited articles are not calibration sources. See
  `data/raw/motorcycle_speed_calibration.csv` and DEC-030 in `docs/decisions.md`.

## Current status (update this section as the project progresses)

**Local data recovery (2026-10-10):** Lost local inputs were downloaded again; see `docs/data_recovery.md`. Fresh OSM/VinBus/Overture layers differ from the historical pilot. Overture release 2026-09-23.1 has 1,707 unchecked supplement POIs; historical review completion below does not transfer. WorldPop is a valid Ocean Park subset. Published headline outputs remain historical; recovered metrics use published accessibility exports, not the new sources.

**SMCI scale migration (2026-08-11):** The canonical cell-level primary is the equal-weight geometric mean: mean SMCI_A=0.1470, SMCI_B=0.1711, and Delta_SMCI=+0.0242. Product-scale values retained elsewhere in dated history or unrerun sensitivity prose are legacy audit values, not current headlines. See `outputs/validation/smci_scale_transition.md` and `outputs/validation/scenario_uncertainty_envelope_status.md`.

- [x] Proposal text finalized at v7 (`proposal/proposal_v7.md`): theory-RAC consistency,
  classification logic, collinearity check, VIF contingency executed, RAC scaling sensitivity,
  additive robustness robustness (ρ=0.803), Section 3.8 additive fix, validation hierarchy resolved.
- [x] Analysis formulas (`src/accessibility.py`) implemented and tested; report current test results in the change review.
- [x] Deterministic core DAG + JSON/SQLite provenance implemented (`config/pipeline.json`,
  `scripts/run_research_pipeline.py`, `src/provenance.py`). Current graph covers core inputs,
  pilot metrics, VIF, population weighting, headline snapshot, and self-audit. Publication
  sensitivities, tables, figures, document consistency, and boundary analysis are not yet graphed.
- [x] OSM check for existing VinBus route relations (39 found 2026-06-21;
  `data/raw/vinbus_overpass_relations.json`).
- [x] VinBus Overpass geometry dump for Ocean Park-facing refs (`E01,E02,E03,E10,OCP1,OCP2`);
  `data/raw/vinbus_overpass_relations_geom.json`.
- [x] Real OSM data fetch: 462 grid cells, 106 POIs (`data/interim/pilot_data_manifest.json`).
- [x] Motorcycle speed calibration CSV with JICA/literature citations:
  `data/raw/motorcycle_speed_calibration.csv`.
- [x] Network-v1 accessibility inputs: Dijkstra NAI + motorcycle travel times from GraphML,
  VinBus pseudo-GTFS (API-scraped, 176 routes / 5,631 stops / per-route headway 5–48 min)
  for MAI_B/RAC_B. OSM Overpass routing retained as sensitivity.
  `data/interim/pilot_accessibility_inputs.csv`.
- [x] Pilot metrics (network-v1 + pseudo-GTFS + **merged POIs primary**): 4 typologies confirmed in Scenario B,
  shared-scale Delta_SMCI, additive robustness rho~0.824, high MAI/RAC VIF flagged.
  SMCI_A=0.0449, SMCI_B=0.0920, 288/462 improved (62.3%), 0 declined (original commercial-proxy run;
  superseded — current 800 m primary numbers are SMCI_A=0.0070, SMCI_B=0.0133 in Decision #27 below).
  `data/processed/pilot_metrics.csv`, `outputs/pilot_summary.csv`.
- [x] Validation outputs: VIF flags, correlation matrix, robustness summary.
  `outputs/validation/`. Distribution diagnostics now explain SMCI zero inflation and delta groups.
  Motorcycle spot-check template pre-filled with 10 OD pairs.
- [x] Self-audit report generated by `scripts/project_self_audit.py` at `outputs/project_self_audit.md`.
- [x] POI audit + spot-check: `outputs/poi_audit.md`, `data/interim/poi_spot_check.csv`; 20/20 records reviewed (14 confirmed, 2 duplicate, 2 misclassified, 2 missing/unverified).
- [x] Download Hanoi GTFS â€” World Bank CC-BY 4.0, 1.51 MB, Jun 2020 vintage (224 routes, 7,670 stops).
  `data/raw/hanoi_gtfs.zip`. Status = `baseline_limited` (service dates 2018, stop geometry valid).
  MAI_A now nonzero for 162/462 cells using stop proximity. Network B timetable is old, so status
  remains `baseline_limited`; stop geometry is still used for `stop_accessibility()`.
- [x] Verify WorldPop using actual raster: `data/raw/worldpop/vnm_ppp_2020.tif`, ~92.77m metadata resolution, adequate for 250m grid.
- [x] RAC scaling sensitivity (`scripts/rac_scaling_sensitivity.py`): κ=1.0 (minmax vs log), ρ=0.9999.
  `outputs/validation/rac_scaling_summary.md`.
- [x] RAC_time-only VIF contingency (`scripts/rac_time_only_sensitivity.py`): κ=0.871, 42/462 relabelled.
  `outputs/validation/rac_time_only_summary.md`. Superseded by Decision #22: RAC_time primary retained; full-RAC robustness kept.
- [x] WorldPop aggregation by grid cell (`scripts/aggregate_worldpop_by_grid.py`) →
  `data/interim/grid_worldpop.csv` (462 cells, total pop ~78,816, all cells non-zero).
  Population-weighted SMCI_B = 0.0825 vs unweighted 0.0920 (bias −10.3%, ρ = −0.0496).
  34.2% of population in Motorcycle Lock-in cells. `outputs/validation/population_weighted_smci.md`.
- [x] Fetch/aggregate building footprints: `scripts/fetch_building_footprints.py` fetched
  41,816 VIDA footprints at confidence >=0.70 to `data/raw/building_footprints.gpkg`;
  `scripts/aggregate_building_footprints.py` wrote `data/interim/grid_building_footprints.gpkg`
  (455/462 cells built, 30,988 grid-intersecting footprints, ~3.53M m2 footprint area).
  Use this as built-cell mask + WorldPop cross-check before stronger zero-NAI claims.
- [x] Check MobilityDatabase maintained catalog for Hanoi GTFS candidates: 0 hits.
  TUMI/Datahub checked 2026-06-23: Hanoi Morning/Midday/Afternoon GTFS candidates exist,
  but require license/service-date checks and should be current-service/time-of-day sensitivity only.
  See `outputs/validation/gtfs_catalog_check.md`.
- [x] Overture Places POI supplement: `scripts/fetch_overture_pois.py` wrote
  `data/raw/overture_pois.gpkg` (62 places); `scripts/merge_poi_sources.py` wrote
  `data/interim/merged_pois.gpkg` + `outputs/poi_merge_summary.md` (161 merged POIs:
  7 `both`, 99 `osm_only`, 55 `overture_only`). The 55 Overture-only POIs were user-confirmed
  (100% confirmed, gate PASS 2026-06-24). **Merged POI layer promoted to primary** (2026-06-24).
  Pipeline now uses `data/interim/merged_pois.gpkg` (161 POIs) as primary POI source.
  OSM-only (106 POIs) retained as sensitivity in `outputs/validation/merged_poi_sensitivity.md`.
- [x] Overture POI gate evaluator: `scripts/evaluate_overture_gate.py` wrote
  `outputs/validation/overture_gate_result.md`. Current verdict = PASS: 55/55 confirmed,
  no severe category bias.
- [x] **Economic domain enrichment (2026-06-25, Decision #18):** `scripts/fetch_osm_landuse.py`
  fetched landuse polygons + `office=*` + `amenity=bank/marketplace` (50 candidates);
  `scripts/merge_economic_features.py` deduped (30 m) and added 47 fresh POIs →
  **161 → 208 POIs**. Domain distribution {economic: 1→32, higher_ed: 54→70}. Three
  classifier bugs fixed + regression-tested (office-column drop, NaN-tag truthiness, "nha khoa"
  false positive). MAI/RAC VIF dropped to 16.0/15.8 (from 19.7/21.6). mean SMCI_B 0.0968→0.0845
  (commercial proxy had inflated it). Spot-check sheet: `outputs/validation/economic_poi_spot_check.csv`.
- [x] Built/population zero-access audit: `outputs/validation/built_population_zero_access.md`.
  Building footprints are present in 455/462 cells; with the 800 m / 10 min NAI primary threshold,
  **88 zero-NAI cells** (19.0%) remain, including 84 built zero-NAI cells containing ~11,798
  residents (15.0% of pilot population). Zero inflation is not simply lake/park/open-space; at the
  1200 m optimistic upper bound it falls to 33 cells (7.1%).
- [x] Merged-POI sensitivity: `outputs/validation/merged_poi_sensitivity.md`.
  Overture gate PASS. Merged POIs reduce zero-NAI cells to 116/462 (vs 166 OSM-only).
  Build default is still OSM-only (106 POIs); merged layer is sensitivity only until promoted.
- [x] VinBus stop-routing comparison: `outputs/validation/vinbus_routing_comparison.md`.
  OSM stop-level Network C (254 nodes) previously primary; now demoted to sensitivity.
- [x] VinBus API scrape → pseudo-GTFS: `data/raw/vinbus_pseudo_gtfs_fixed/` (176 routes /
  5,631 stops / per-route headway 5–48 min, median 15 min). OCP1/OCP2 headway imputed at
  10 min. `scripts/fix_vinbus_gtfs.py` applies quality fixes. This is now the primary
  Network C geometry source in `build_network_accessibility_inputs`.
- [x] Headway sensitivity rerun with pseudo-GTFS: kappa=1.000 across all 3 fallback-headway
  scenarios (observed per-route headway dominates; fallback doesn't affect study-area routes).
  `outputs/headway_sensitivity_summary.csv`.
- [x] Supervisor review package + maps: `outputs/supervisor_package.md`, `outputs/supervisor_memo.md`,
  and `outputs/maps/` (SVG quick-look maps plus GeoPackage/GeoJSON map layers for NAI, MAI_B,
  RAC_B, SMCI_B, Delta_SMCI, and typology_B).
- [x] Manual motorcycle spot-check: 10/10 Android Google Maps pairs measured, MAE ~1.90 min.
- [x] Proposal v7 (`proposal/proposal_v7.md`): additive robustness, shared-scale Delta_SMCI,
  VIF contingency executed, RAC scaling sensitivity, Section 3.8 fix, current pilot caveats.
  Updated 2026-06-25: MAI proxy-escaped using building footprint matching (150/161 POIs, 93% matched).
  Historical product-scale numbers (Decision #27): SMCI_A=0.0070, SMCI_B=0.0133, 60.8% improved,
  pop-weighted SMCI_B=0.0129 (bias −3.2%), 33.9% population in Motorcycle Lock-in. Pytest: 85 tests pass.
- [x] Travel time validation and sensitivity analysis scripts implemented and reports generated:
  - Travel time MAE is 1.90 minutes against Google Maps checks (PASS < 3.0 min).
  - Parameter sensitivity typology classification is highly stable (weights Kappa >= 0.98, decay thresholds Kappa >= 0.83).
- [x] **Supply-side population integrated INTO MAI (2026-06-27, Decision #19):** each POI's
  opportunity weight scaled by residential density of its containing cell —
  `m_j = clip(sqrt(pop_density_j/median), 0.5, 2.0)`, applied to all 4 domains, same weights
  into mai_moto/mai_a/mai_b so RAC_opp stays consistent. Pilot multiplier [0.50, 1.81], mean 0.98
  (193/208 POIs matched). MAI is no longer a pure proxy — population is a first-class input, not
  post-hoc. **New numbers: SMCI_A=0.0497, SMCI_B=0.0881, 67.1% improved.** Domain shares unchanged
  (54.1/24.7/15.5/5.8 — no #18-style domination). No-pop sensitivity κ=0.976 (8/462 relabelled).
  VIF unchanged (MAI≈20.2, RAC≈22.8) — pop scales numerator+MAI proportionally; RAC_time-only
  remains the VIF remedy. Demand-side `MAI_B_popweighted` retained as separate equity sensitivity.
  Toggle via `--no-pop-weighting`. Report: `outputs/validation/population_supply_weighting_sensitivity.md`.
  Superseded headline numbers after RAC_time audit fix in Decision #20 below. Pytest: 70 tests pass.
- [x] **RAC_time reproducibility fix + reviewer-risk sensitivity checks (2026-06-27, Decision #20):**
  `RAC_time_raw_i` now uses motorcycle opportunity-weighted mean travel time divided by
  walk-transit opportunity-weighted mean travel time over the same MAI opportunity set, domain
  weights, POI weights, and 60-min cutoff. Audit columns are written:
  `moto_mean_opp_time_min`, `wt_A_mean_opp_time_min`, `wt_B_mean_opp_time_min`.
  New primary metrics: SMCI_A=0.0322, SMCI_B=0.0435, 298/462 improved (64.5%),
  88 unchanged, 76 declined slightly, zero-NAI=88. RAC_time-only sensitivity:
  kappa=0.900, 32/462 relabelled, VIF(MAI)=3.25 and VIF(RAC_time)=1.86. Motorcycle
  global ±20% motorcycle-speed sensitivity is stable (kappa=1.000, 0 relabelled in both scenarios); transit impedance sensitivity
  remains acceptable but shows expected SMCI decline under conservative/pessimistic penalties.
  Reports: `outputs/validation/motorcycle_speed_sensitivity.md`,
  `outputs/validation/transit_impedance_sensitivity.md`. Pytest: 70 tests pass.
- [x] **Strict source-backed MAI hierarchy populated for pilot (2026-06-29, Decision #21):**
  `src/accessibility_inputs.py` has `classify_poi_opportunity(row, opportunity_basis=...)`.
  `scripts/derive_all_observed.py` filled all four domains in `data/interim/merged_pois_observed.gpkg`:
  healthcare 18/18 (100%), higher_ed 70/70 (100%), economic 32/32 (100%), commercial/services
  81/81 included (100%) with 7 point-only service/transport listings explicitly excluded from MAI.
  `--opportunity-basis observed_strict` now requires source-backed magnitudes or explicit exclusion;
  current gate: `needs_source=0`, `proxy_source_tiers=0`. Audit:
  `data/interim/poi_observed_audit.csv`. economic REF calibrated to 500 jobs (cap=5.0, Decision #18
  discipline) to prevent KCN domination. Strict observed-vs-proxy sensitivity: SMCI_B
  0.0435→0.0500, κ=0.876, 40/462 relabelled, Spearman ρ=0.991. VIF(MAI)=10.23, VIF(RAC)=11.12
  (slightly higher than proxy; RAC_time-only contingency #3 remains the VIF remedy).
  **Current after Decision #22 + 1200 m NAI threshold:** promoted RAC_time primary gives
  proxy SMCI_B 0.0163 -> strict observed 0.0160, kappa=0.9245, 24/462 relabelled,
  Spearman rho=0.9950, VIF(MAI)=3.78, VIF(RAC)=2.00.
  Source tiers:
  `official_source`, `facility_source`, `geometry_measured`, `observed_point`,
  `observed_derived`, `observed_dasymetric_weak`, `excluded_not_destination`.
  Report: `outputs/validation/observed_vs_proxy_sensitivity.md`.
- [x] **Reviewer-risk metric audit + primary RAC promotion (2026-06-29, Decision #22):**
  `scripts/metric_variant_audit.py` tested NAI diversity/capped NAI, RAC_time-only,
  RAC_opp-only, winsor/log normalization, additive SMCI, absolute-threshold typology,
  MAI weight/decay sensitivity, exponential decay, top-1/top-5 opportunity leverage,
  and strict-excluded-POI spatial missingness. Winner: RAC_time primary because max VIF
  drops while preserving legacy full-RAC labels. Current promoted strict metrics at the
  800 m / 10 min NAI primary (Decision #27): SMCI_A=0.0070, SMCI_B=0.0133, mean Delta=0.0063,
  281/462 improved, 88 unchanged, 93 declined; typology_B counts 171 Integrated Capability,
  60 Fragmented Capability, 60 Transit-Dependent, 171 Motorcycle Lock-in. Primary VIF(MAI)=2.93,
  VIF(RAC)=2.05; legacy full-RAC retained as `RAC_full_A/B` and `SMCI_B_full_rac_legacy`
  (VIF(MAI)=9.58, VIF(RAC)=9.56).
- [x] **NAI threshold localized to 800 m after professor review (2026-07-01, Decisions #26/#27):**
  Professor flagged 1200 m / 15 min as too optimistic for tropical, motorcycle-dominant Hanoi
  walking. **Primary NAI threshold is now 800 m (10-minute neighborhood, ~10 min at 80 m/min)**,
  used as a transparent operational assumption rather than a locally validated cutoff — no
  Hanoi/HCMC study independently establishes 800 m as empirically optimal (Decision #29);
  1200 m / 15 min is demoted to optimistic upper-bound
  sensitivity. Threshold audit (`outputs/validation/nai_threshold_sensitivity.md`): zero-NAI
  33/462 (1200 m) → 88/462 (800 m) → 133/462 (600 m); mean SMCI_B 0.0169 → 0.0133 → 0.0107;
  the four-typology structure is near-invariant across 600–1200 m, so the headline does not hinge
  on the exact catchment. Build default `--walking-threshold-m` now 800.
- [ ] Full study area data collection and analysis.

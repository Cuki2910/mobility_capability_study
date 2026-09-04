# Unified Roadmap — SMCI/NAI Method Upgrade + Interactive Map Rebuild

Merges three source documents into one ordered execution plan:

1. `MASTER PROMPT — HOÀN THIỆN TOÀN BỘ NÂNG CẤP SMCI–NAI.md` (method upgrade, publication pipeline)
2. `agent_prompt_SMCI_geometric_mean.md` (manuscript-facing GM formula change — subsumed into Phase 2 below)
3. `master_agent_plan_mobility_map.md` (interactive map rebuild)
4. `De_xuat_nang_cap_chi_so_SMCI_hien_tai.docx` / `Ke_hoach_nang_cap_phuong_phap_NAI_theo_Bruno.docx` (methodological justification — already folded into MASTER PROMPT Phases 1–6)

Single branch: `feat/complete-smci-nai-upgrade`. No direct commits to `main`. Commit sequence extends the MASTER PROMPT's 13-commit list to insert map-rebuild work in its correct dependency position (after GM SMCI + NAI-Bruno land, since the map renders their outputs).

Ground rules carried from both source docs, non-negotiable throughout:
- No hand-edited generated artifacts (`outputs/`, HTML, CSV) — regenerate from code.
- No fabricated data. Missing external data → `NOT_RUN_DATA_REQUIRED` status + protocol, not an estimate.
- Cube root / geometric mean computed per-cell, never on an aggregate mean.
- Product-vs-geometric-mean is a reporting-scale change, not a robustness test (see `src/accessibility.py:121-134` docstring — already encodes this).

---

## Phase 0 — Baseline lock

From MASTER PROMPT §3. Run before any code change.

```bash
python -m pytest tests/ -q
python scripts/agent_gate.py
python scripts/check_document_consistency.py
python scripts/project_self_audit.py
python scripts/freeze_geospatial_baseline.py --help
python scripts/baseline_integrity.py --help
python scripts/graph_health.py --help
```

Output: `outputs/upgrade/baseline_lock.json` + `.md` — commit SHA, 462 cells, product-based SMCI A/B, zero-access, VIF, typology counts, test/gate status, hashes of grid/metrics/WorldPop/boundary/network inputs.

Commit: `chore: lock pre-upgrade baseline`

---

## Phase 1 — Decision record + data contract

From MASTER PROMPT §4. Add decision entry to `docs/decisions.md`:
- GM promoted to primary reporting scale; product retained as legacy audit.
- Product vs GM = same ordinal ranking, different scale, not robustness.
- Additive stays the real aggregation sensitivity; minimum-component is bottleneck diagnostic.
- Typology primary is NAI/MCS rank-split — does not depend on SMCI form, unaffected by this change.
- Local Moran/LISA must rerun (nonlinear transform can change local significance).

Update `config/pipeline.json`, `src/headline_metrics.py`, schemas, fixtures with:
```json
{
  "smci_primary_operator": "equal_weight_geometric_mean",
  "smci_legacy_operator": "product",
  "smci_robustness_operator": "additive",
  "smci_bottleneck_operator": "minimum_component"
}
```

Commit: `docs: record geometric SMCI primary decision`

---

## Phase 2 — Implement geometric-mean SMCI (cell-level)

From MASTER PROMPT §5 + `agent_prompt_SMCI_geometric_mean.md` (manuscript-facing wording is now just one consumer of this, see Phase 11).

**2.1 `src/accessibility.py`** — add alongside existing `compute_smci` (keep as `compute_smci_product*`):
```python
compute_smci_geometric(...)          # np.cbrt(nai_norm * mai_norm * rac_norm)
compute_smci_geometric_from_normalized(...)
compute_smci_min(...)                # bottleneck diagnostic
compute_smci_min_from_normalized(...)
```
`compute_smci_additive*` already exists — no change needed there.
No epsilon in the primary formula (breaks zero-preserving property).

**2.2 `src/pilot.py`** — canonical names:
```
SMCI_A = geometric A          SMCI_product_A = legacy
SMCI_B = geometric B          SMCI_product_B = legacy
Delta_SMCI = geometric B - A  Delta_SMCI_product = legacy
SMCI_min_A / SMCI_min_B       (new diagnostic)
```
`SMCI_additive_A/B` already exists, keep name.

**2.3 Invariant tests** (10 listed in MASTER PROMPT §5.3) — zero-preservation, positive-cell ordering unchanged, Spearman=1, Delta sign match, improved/unchanged/declined counts unchanged, typology A/B unchanged, values in [0,1], no cbrt-of-mean.

**2.4 Consumers to update** (grep for `SMCI_A`, `SMCI_B`, `Delta_SMCI`, `mean_SMCI`, `product`, `zero-access`, `times higher`, `ratio`, `boundary`, `hotspot`, `scenario`):
`src/headline_metrics.py`, `scripts/build_headline_snapshot.py`, `scripts/run_pilot_metrics.py`, `scripts/make_distribution_diagnostics.py`, `scripts/compute_population_weighted_smci.py`, `scripts/analyze_boundary_discontinuity.py`, `scripts/analyze_spatial_autocorrelation.py`, `scripts/make_pilot_maps.py`, `scripts/make_combined_interactive_map.py`, `scripts/make_paper_tables.py`, `scripts/make_paper_figures.py`, `scripts/make_supervisor_memo.py`, `scripts/project_self_audit.py`, all sensitivity scripts, paper/proposal/docs.

Note: `scripts/make_interactive_map.py` is deliberately **not** patched piecemeal here — it gets a full rebuild in Phase 4, which will consume `SMCI_A`/`SMCI_B`/`Delta_SMCI` under their new GM definition natively.

**2.5** Recompute per-cell first, then descriptive/weighted stats, boundary summaries, Moran/LISA, maps, tables, abstract numbers. Rewrite every "times higher" claim (ratios compress under cube root — see `agent_prompt_SMCI_geometric_mean.md` §4 formula).

**2.6** Scale-transition report: `outputs/validation/smci_scale_transition.csv` + `.md` (old/new means, deltas, boundary medians, zero counts, typology counts, Moran/LISA, rank correlation).

Bump `outputs/headline_metrics.json` schema version.

Commits: `feat: add geometric product additive and minimum SMCI operators`, `refactor: migrate canonical pilot metrics to geometric SMCI`, `test: add SMCI scale and typology invariants`

---

## Phase 3 — NAI upgrade per Bruno (CCS / NPT / coverage / inequality)

From MASTER PROMPT §6. New module `src/neighborhood_access.py`, new script `scripts/nai_bruno_robustness.py`, new config `config/nai_categories.yml`. **NAI primary threshold stays 800 m** — everything here is validation/robustness, not a replacement.

- **CCS** (Category Completeness Score) at 600/800/1000/1200 m; report `<0.50`, `0.50–0.75`, `≥0.75` bands; sensitivity at completeness thresholds 0.50/0.67/0.75.
- **NPT** (Neighborhood Proximity Time) at K=1/3/5; missing-category → predeclared cutoff penalty (20 min primary), not exclusion from mean; `NPT_benefit = 1 - normalized_NPT`.
- **Population coverage**: `F_complete(T,q)` grid over T×q, plus F10/F15/F_zero — report cell share and population share in parallel, not as observed behavior.
- **Population-weighted inequality**: weighted mean/median/percentiles + weighted Gini (with unit tests: equal-values→0, two-point case, zero/negative-weight rejection).
- **Local-access classification** (Zero/Low/Incomplete/Abundant-but-incomplete/Locally-complete) — supplementary only, does not replace the 4-typology primary.
- **SMCI_NPT** — two explicit forms, `SMCI_NPT_product` and `SMCI_NPT_geometric` (since primary SMCI is now GM, avoid re-creating the naming ambiguity Phase 2 just fixed).

Outputs: `outputs/validation/nai_bruno_cells.{csv,gpkg}`, `nai_bruno_summary.{csv,md}`, `nai_population_coverage.csv`, `nai_inequality.md`, `smci_npt_robustness.md`, plus maps (NAI/CCS/NPT/NPT_benefit/access-class/SMCI_NPT/boundary profiles).

Commits: `feat: add CCS and NPT neighborhood robustness`, `feat: add population coverage and weighted NPT inequality`, `feat: add SMCI NPT supplementary specification`

---

## Phase 4 — Interactive map rebuild

From `master_agent_plan_mobility_map.md`, phases A–C+E of its own internal ordering. Depends on Phase 2 (GM SMCI) and benefits from Phase 3 (CCS/NPT layers optional add-on, not required for map correctness). This is a full rebuild of `scripts/make_interactive_map.py`, not an incremental patch.

**4.1 Config + correctness fixes** (verified against current code):
- Central `ANALYTICAL_SPEC` dict (nai_primary_threshold_m=800, smci_form, default_scenario, default_metric) driving every label.
- Fix NAI popup text — currently hardcoded `"1200m (~15 min)"` at `make_interactive_map.py:496`, must read 800 m from spec.
- Fix NaN→0.0 coercion at `make_interactive_map.py:149` (`return float(v) if pd.notna(v) else 0.0`) — replace with `safe_float` that preserves `None`; distinguish no-data / structural-zero / positive in rendering.
- Replace `convex_hull` boundary (`:77`) with `unary_union(grid.geometry)` (optionally simplified with `preserve_topology=True`).

**4.2 Data model** — one grid geometry, full property set per cell (scenario A+B fields, normalized values, boundary attributes, zero flags, `has_data`) instead of scenario-specific duplication. Centralize `METRIC_META` (already exists at `:494` but only covers nai/smci/mai/rac/delta — extend to cover new fields, add label/unit/formatter/scenario-availability/scale-type per MASTER map plan §3.3) with a test asserting every displayed label maps to exactly one field (guards the "Bruno frontend category mismatch" failure mode named in the plan).

**4.3 Cartography**:
- Replace `SPECTRAL` diverging palette (`:824`, currently used for one-directional NAI/MAI/RAC/SMCI too) with sequential (Viridis/Cividis/Inferno/YlGnBu) for one-directional metrics; keep a dedicated zero-centered diverging scale only for `Delta_SMCI` (q02/q98 symmetric bounds, `DELTA_EPSILON=1e-10` for improved/unchanged/declined classification, cross-check counts against Phase 2 pipeline output).
- Shared A/B bounds (`lo=min(q02_A,q02_B)`, `hi=max(q98_A,q98_B)`) for scenario-dependent metrics; clamp visually, preserve exact value in popup.
- Structural-zero cells get a distinct style (hatch/dashed grey), not placed on the sequential scale with low-positive cells.
- Colorblind-safe categorical/bivariate typology palette.

**4.4 Controls + interaction**: separate scenario selector (A/B/Difference) from metric selector; NAI marked scenario-invariant (Difference disabled for it); typology transition categories (not raw subtraction); shareable URL state; selected-cell panel with full field list + structural-zero reason; cell-level A-vs-B comparison chart + NAI/MAI/RAC component-balance chart (one chart library only — audit for duplicate Chart.js loads first).

**4.5 Boundary + population layers**: `share_inside_project`, `boundary_side` (Inside/Outside/Boundary-straddling at 0.75/0.25 thresholds), `distance_to_boundary_m`, boundary bands (0–250/250–500/500–1000/1000–2000 m); population + population-density layers; exposure diagnostics (`population_in_zero`, `population_in_lockin`, population-weighted Delta_SMCI) explicitly labeled as diagnostic, not validated index.

**4.6 Product quality**: default view = Scenario B + Typology + both boundaries + structural-zero rendering; POIs/routes/stops/population/boundary-bands off by default; presets (Capability / Transit network / Boundary fragmentation / Population exposure / Scenario comparison); default extent fits the 462-cell study area, not the full VinBus network; responsive layout <768px; load dataset once, no reload on control switch.

**4.7 Tests**: `tests/test_interactive_map.py`, `tests/test_grid_sensitivity.py` (stub until Phase 5 lands), `tests/test_metric_metadata.py` — analytical consistency (462 unique cells, GM recomputed correctly, zero→zero, shared bounds, Delta=B−A, counts match pipeline, threshold=800m, population conserved, no NaN→0), metadata mapping (no duplicate/conflicting labels), geometry validity (share_inside∈[0,1], distances≥0, bands mutually exclusive). Playwright smoke tests only if the dependency is actually available in the environment — verify before committing to this, don't assume.

**4.8** Build report `outputs/maps/map_build_report.md` (commit SHA, hashes, threshold, SMCI form, cell/zero counts, population total, visual bounds, CRS/anchor, snap-distance summary, test results) + `outputs/maps/README.md`.

Commits: `refactor: rebuild interactive map data model and cartography`, `feat: add boundary fragmentation and population exposure map layers`, `test: add interactive map analytical and metadata tests`

---

## Phase 5 — Grid geometry robustness (heaviest phase — flagged, not skipped)

From `master_agent_plan_mobility_map.md` §2.4. Requires rebuilding network-routing accessibility inputs on alternate geometries, not just a map change — treat as its own work cycle within the branch, sequenced after Phase 4 lands (so there's a stable primary map to compare sensitivity runs against).

- Shifted-square grids: +125 m X, +125 m Y, +125 m X&Y, same 250×250 m cells.
- Equal-area hexagonal grid: side ≈155.1 m, area 62,500 m² (matches primary square area).
- Same networks, POIs, thresholds, scenarios, normalization, study extent held constant across all grid variants.
- Compare: Spearman(NAI, MAI, RAC, SMCI), population-weighted mean SMCI, zero-access share, typology agreement (kappa), boundary discontinuity, Delta direction, HH/LL cluster locations.
- Goal is stability of substantive conclusions, not identical cell values. Primary grid (250 m square) is not replaced regardless of outcome.

Output: grid-shift and hexagon sensitivity report in `outputs/validation/`.

Commit: `feat: add grid-shift and equal-area hexagon robustness`

---

## Phase 6 — Consolidate sensitivity specs

From MASTER PROMPT §7. Canonicalize MAI weights (default/equal/job-heavy/econ-light/service-health-heavy/UTM-derived + seeded-2026 Dirichlet stress test, ≥1000 draws if feasible), time-decay (linear 20-40/30-60 primary/45-90, exponential 30-60), normalization (min-max primary/log/percentile-capped; anchor-based only if defensible anchors exist, else `NOT_RUN_DATA_REQUIRED`), aggregation (GM primary/additive sensitivity/min diagnostic — product reported as legacy scale, not robustness), typology (rank-median primary + quantile 0.40/0.45/0.55/0.60 + defensible absolute thresholds). Regenerate or archive stale `outputs/validation/sensitivity_analysis_report.md`. All scripts should read canonical defaults from `config/pipeline.json` rather than re-hardcoding (`merged_pois_observed.gpkg`, `observed_strict`, 800 m NAI, RAC_time primary, current pop weighting, GM SMCI).

Commit: `refactor: canonicalize MAI and normalization sensitivities`

---

## Phase 7 — Data quality + uncertainty

From MASTER PROMPT §8. Data-quality grade (A/B/C/D) per component/cell from existing provenance (POI, GTFS, VinBus pseudo-GTFS, motorcycle calibration, WorldPop, footprints, observed-magnitude tiers) — not a new SMCI component, just an audit layer + map + population exposure by grade. Scenario envelope (p05/p25/median/p75/p95/min/max per cell across motorcycle-speed/transit-impedance/MAI-weight/time-decay/normalization/observed-vs-proxy/NAI-threshold/aggregation-operator scenarios) — explicitly not called a confidence interval.

Commit: `feat: add scenario uncertainty envelope and data-quality grades`

---

## Phase 8 — RAC, reliability, mixed traffic (code contracts only where data is missing)

From MASTER PROMPT §9. RAC_time stays primary (no change without stronger evidence). Reliability module (departure time, median/p95 travel time, buffer time, headway variability, missed-transfer penalty) and generalized-cost RAC (walk/wait/in-vehicle/transfer time, fare, moto operating cost, parking, VOT, discomfort) — build schema + refuse-to-run behavior + `NOT_RUN_DATA_REQUIRED` status + data-collection protocol. Do not fabricate coefficients. Mixed-traffic friction layer — design contract only, same rule.

Commit: `docs: add external validation and generalized-cost protocols` (shared with Phase 9)

---

## Phase 9 — External validation

From MASTER PROMPT §10. `scripts/external_validation.py` — validates schema, joins observations to cells, computes predefined metrics, **refuses to run** without required fields. `docs/external_validation_protocol.md`, `data/raw/external_validation_template.csv`, `outputs/validation/external_validation_status.md` = `NOT_RUN_DATA_REQUIRED` unless real observational data exists. Never claim "externally validated" without it.

---

## Phase 10 — West Tay Mo comparison site

From MASTER PROMPT §11. Read existing `docs/comparison_site_protocol.md`, `docs/western_extension_protocol.md`, `config/sites/west_taymo.yml`, `outputs/west_taymo/*` first — check for conflicts with site-selection/matching protocol before touching. Complete as much as possible: boundary provenance, area/population seed conflicts, planned/unplanned labels, merged observed-POI audit, strict opportunity coverage, WorldPop integration, accessibility inputs, metrics, comparison tables, shared-scale normalization, scenario-matched comparison, limitations. Do not promote `observed_strict` if `needs_source > 0`. Cross-site comparison uses common metric definitions and fixed/common normalization — no causal claims from n=2.

---

## Phase 11 — Publication + documentation sync

From MASTER PROMPT §12 (manuscript-facing GM rewrite from `agent_prompt_SMCI_geometric_mean.md` happens here, using Phase 2's recomputed cell-level values — not before). Update `paper/paper_draft.md`, `proposal/proposal_v7.md`, `docs/Research_Proposal_SMCI_v2.md`, `docs/metrics_reference.md`, `docs/decisions.md`, `CLAUDE.md`, `README.md`. Recalculate every SMCI number in abstract/results/conclusion at cell level — never copy old product-scale headline numbers into GM-labeled text. Rewrite every "times higher" claim (ratio compression under cube root). Remove stale caveats from `make_supervisor_memo.py` / `project_self_audit.py` (WorldPop-not-integrated, Overture-pending, POI-gate-pending, RAC_time-not-primary — all already resolved per current CLAUDE.md status). Extend `scripts/check_document_consistency.py` with semantic assertions (primary SMCI/RAC operator, NAI threshold, opportunity basis, Overture/WorldPop/GTFS/comparison-site/external-validation status) that fail if manuscript contradicts canonical config.

Commits: `fix: regenerate canonical outputs and publication artifacts`, `chore: strengthen semantic consistency and final gates`

---

## Phase 12 — Tests + final gates

From MASTER PROMPT §13. Full unit + integration test suite (geometric/product/additive/min SMCI, zero preservation, monotonicity, scenario-delta sign, typology invariance, CCS, NPT K=1/3/5, missing-category cutoff, population coverage, weighted Gini, local-access classes, SMCI_NPT, deterministic Monte Carlo, scenario envelope, provenance grading, external-validation schema refusal, West Tay Mo strict gate, interactive-map analytical/metadata/geometry tests from Phase 4). Final gate run:

```bash
python -m pytest tests/ -q
python scripts/agent_gate.py
python scripts/check_document_consistency.py
python scripts/project_self_audit.py
python scripts/graph_health.py
```

Do not report done if: tests fail, doc consistency fails, generated outputs stale, headline snapshot mismatches processed cells, semantic status conflicts, or a source file is missing while output claims completion.

---

## Final deliverables

From MASTER PROMPT §14 + map plan §16, combined:

- `outputs/upgrade/upgrade_completion_report.{md,json}`, `outputs/upgrade/upgrade_status_matrix.csv` — every recommendation from all 5 source documents mapped to status (`COMPLETED` / `COMPLETED_WITH_LIMITATION` / `CODE_COMPLETE_DATA_REQUIRED` / `NOT_IMPLEMENTED_WITH_REASON` / `REJECTED_BY_METHOD_DECISION`), files changed, tests, output artifact, evidence, remaining blocker, paper location.
- `outputs/maps/map_build_report.md`, `outputs/maps/README.md`, `outputs/maps/screenshots/`.
- Old/new headline SMCI table (product vs GM, per scenario, per statistic).
- Section-by-section manuscript change log.
- Exact reproduction commands, final commit SHAs, PR-ready summary.

---

## Commit sequence (extends MASTER PROMPT §15)

1. `chore: lock pre-upgrade baseline`
2. `docs: record geometric SMCI primary decision`
3. `feat: add geometric product additive and minimum SMCI operators`
4. `refactor: migrate canonical pilot metrics to geometric SMCI`
5. `test: add SMCI scale and typology invariants`
6. `feat: add CCS and NPT neighborhood robustness`
7. `feat: add population coverage and weighted NPT inequality`
8. `feat: add SMCI NPT supplementary specification`
9. `refactor: rebuild interactive map data model and cartography`
10. `feat: add boundary fragmentation and population exposure map layers`
11. `test: add interactive map analytical and metadata tests`
12. `feat: add grid-shift and equal-area hexagon robustness`
13. `refactor: canonicalize MAI and normalization sensitivities`
14. `feat: add scenario uncertainty envelope and data-quality grades`
15. `docs: add external validation and generalized-cost protocols`
16. `fix: regenerate canonical outputs and publication artifacts`
17. `chore: strengthen semantic consistency and final gates`

Each commit: single clear scope, no raw-data changes, no unrelated formatting churn, tests run and noted in the message.

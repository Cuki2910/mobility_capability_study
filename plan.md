# Geospatial Extension Plan

**Objective:** strengthen the enclave argument without changing the primary
NAI, MAI, RAC, MCS, SMCI, typology, or Scenario A/B baseline.

**Scope decision:** Local Moran's I (LISA) and boundary-permeability analysis
are core extensions. Dasymetric population work is a sensitivity analysis.
Geographically Weighted Regression is deferred because SMCI is constructed from
the most plausible candidate regressors.

## Track 0 - Baseline Lock

- [x] Record SHA-256 hashes for the grid, Ocean Park boundary, `pilot_metrics.csv`,
      `grid_worldpop.csv`, Network A GraphML, and Network D GraphML.
- [x] Record headline metrics and typology counts before the extension.
- [x] Run `python -m pytest tests/ -v` and save the result in the extension report.
- [x] Confirm that the new analysis reads existing inputs only and does not
      rewrite core inputs or canonical headline outputs.

**Checkpoint 0:** baseline hashes and headline values are recorded; all tests
pass before implementation begins.

## Track 1 - Spatial Autocorrelation

- [x] Add `libpysal` and `esda` only if the installed environment does not
      already provide the required functions.
- [x] Build reusable spatial-weight helpers in `src/` from the 250 m grid.
- [x] Set Queen contiguity as the primary spatial-weight specification.
- [x] Define Rook contiguity and k-nearest-neighbour weights as sensitivities.
- [x] Run Global Moran's I before local statistics for `SMCI_B`, `Delta_SMCI`,
      `NAI`, `MAI_B`, and primary `RAC_B`.
- [x] Run Local Moran's I with a fixed seed, 9,999 permutations, row-standardized
      weights, and Benjamini-Hochberg FDR correction.
- [x] Classify significant cells as High-High, Low-Low, High-Low, or Low-High;
      label all others Not Significant.
- [x] Report zero inflation for SMCI and interpret Local Moran results as
      spatial clustering, not causal evidence.
- [x] Export a cell-level GeoPackage/GeoJSON, CSV, Markdown report, and map.
- [x] Add deterministic tests for cell IDs, CRS, weights, permutations, and
      cluster-label logic.

**Checkpoint 1:** High-High and Low-Low claims are reported only when they
survive FDR correction and at least one alternative weight specification. A
null or unstable result remains a reported result, not a reason to tune inputs.

## Track 2 - Boundary Permeability

- [x] Use Network A and Network D only; do not alter Network B/C or GTFS inputs.
- [x] Identify graph edges and nodes that cross the Ocean Park boundary.
- [x] Audit candidate crossings against OSM access, barrier, highway, and
      footway tags.
- [ ] Manually inspect influential crossings/gates on an OSM or field-reference map.
- [x] Compute modeled crossings per kilometre of boundary and cross-boundary edge
      density for walking and motorcycle networks separately.
- [x] Construct reproducible inside-to-outside OD pairs near the boundary.
- [x] Compute network-to-Euclidean detour ratios by mode for those OD pairs.
- [x] Calculate fixed-seed approximate edge betweenness for boundary crossings
      as a structural diagnostic; do not present it as observed travel flow.
- [x] Map crossings and LISA clusters; detours and crossing centrality are exported as tabular diagnostics.
- [x] Add synthetic graph tests for directed motorcycle edges, blocked crossings,
      boundary intersection detection, and detour calculation.

**Checkpoint 2:** describe these outputs as network-permeability mechanisms.
Do not equate low global betweenness with a barrier or claim that the boundary
causes accessibility differences.

## Track 3 - Dasymetric Population Sensitivity

- [x] Record VIDA footprint provenance, confidence threshold, and the absence of
      reliable height/use attributes for a building-level population claim.
- [x] Define a population-preserving redistribution rule: residential floor area
      if available; footprint area only as a disclosed fallback.
- [x] Reallocate WorldPop only within its source units, then reaggregate to the
      existing 250 m grid.
- [x] Test conservation of total population and identify cells affected by
      cross-cell allocation.
- [x] Compare baseline and dasymetric population-weighted SMCI and population
      shares in the four Scenario B typologies.
- [x] Keep NAI, MAI, RAC, SMCI, and typology values unchanged.
- [x] Report limitations: footprint area is not dwelling count, building use may
      be non-residential, and high-rise population cannot be inferred reliably
      without floor/height information.
- [x] Add tests for conservation, missing footprints, invalid geometry, and
      deterministic allocation.

**Checkpoint 3:** include in the main text only if the population-exposure
interpretation changes materially; otherwise retain as an appendix robustness
result.

## Track 4 - Integration and Publication

- [x] Add reproducible scripts under `scripts/` and reusable logic under `src/`.
- [x] Add output contracts to `config/pipeline.json` after the outputs stabilize.
- [x] Regenerate boundary tables and maps from source inputs rather than editing
      generated artifacts by hand.
- [x] Update `proposal/proposal_v7.md` with methods, results, and limits that
      distinguish clustering, mechanism, and causality.
- [x] Record the methodological decision in `docs/decisions.md`.
- [x] Run `python scripts/check_document_consistency.py`.
- [ ] Run `python scripts/check_agent_ownership.py` when multiple agents work
      on the change.
- [x] Run `python scripts/agent_gate.py` and `python -m pytest tests/ -v`.
- [ ] Regenerate canonical outputs only on an integration branch, following the
      repository workflow.

**Final acceptance criteria:** all pre-extension core metrics are unchanged,
new results are reproducible from tracked code and declared inputs, tests and
gates pass, and the proposal makes no causal or building-level-population claim
that exceeds the evidence.

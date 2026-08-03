# Geospatial Extension Plan

**Objective:** strengthen the enclave argument without changing the primary
NAI, MAI, RAC, MCS, SMCI, typology, or Scenario A/B baseline.

**Scope decision:** Local Moran's I (LISA) and boundary-permeability analysis
are core extensions. Dasymetric population work is a sensitivity analysis.
Geographically Weighted Regression is deferred because SMCI is constructed from
the most plausible candidate regressors.

## Track 0 - Baseline Lock

- [ ] Record SHA-256 hashes for the grid, Ocean Park boundary, `pilot_metrics.csv`,
      `grid_worldpop.csv`, Network A GraphML, and Network D GraphML.
- [ ] Record headline metrics and typology counts before the extension.
- [ ] Run `python -m pytest tests/ -v` and save the result in the extension report.
- [ ] Confirm that the new analysis reads existing inputs only and does not
      rewrite core inputs or canonical headline outputs.

**Checkpoint 0:** baseline hashes and headline values are recorded; all tests
pass before implementation begins.

## Track 1 - Spatial Autocorrelation

- [ ] Add `libpysal` and `esda` only if the installed environment does not
      already provide the required functions.
- [ ] Build reusable spatial-weight helpers in `src/` from the 250 m grid.
- [ ] Set Queen contiguity as the primary spatial-weight specification.
- [ ] Define Rook contiguity and k-nearest-neighbour weights as sensitivities.
- [ ] Run Global Moran's I before local statistics for `SMCI_B`, `Delta_SMCI`,
      `NAI`, `MAI_B`, and primary `RAC_B`.
- [ ] Run Local Moran's I with a fixed seed, 9,999 permutations, row-standardized
      weights, and Benjamini-Hochberg FDR correction.
- [ ] Classify significant cells as High-High, Low-Low, High-Low, or Low-High;
      label all others Not Significant.
- [ ] Report zero inflation for SMCI and interpret Local Moran results as
      spatial clustering, not causal evidence.
- [ ] Export a cell-level GeoPackage/GeoJSON, CSV, Markdown report, and map.
- [ ] Add deterministic tests for cell IDs, CRS, weights, permutations, and
      cluster-label logic.

**Checkpoint 1:** High-High and Low-Low claims are reported only when they
survive FDR correction and at least one alternative weight specification. A
null or unstable result remains a reported result, not a reason to tune inputs.

## Track 2 - Boundary Permeability

- [ ] Use Network A and Network D only; do not alter Network B/C or GTFS inputs.
- [ ] Identify graph edges and nodes that cross the Ocean Park boundary.
- [ ] Audit candidate crossings against OSM access, barrier, highway, and
      footway tags; manually inspect influential crossings on a map.
- [ ] Compute legal crossings per kilometre of boundary and cross-boundary edge
      density for walking and motorcycle networks separately.
- [ ] Construct reproducible inside-to-outside OD pairs near the boundary.
- [ ] Compute network-to-Euclidean detour ratios by mode for those OD pairs.
- [ ] Calculate fixed-seed, flow-weighted edge betweenness for boundary crossings
      using grid origins and external destinations.
- [ ] Map crossings, detours, and influential boundary edges alongside the LISA
      cluster map and descriptive boundary-band output.
- [ ] Add synthetic graph tests for directed motorcycle edges, blocked crossings,
      boundary intersection detection, and detour calculation.

**Checkpoint 2:** describe these outputs as network-permeability mechanisms.
Do not equate low global betweenness with a barrier or claim that the boundary
causes accessibility differences.

## Track 3 - Dasymetric Population Sensitivity

- [ ] Confirm VIDA footprint provenance, confidence threshold, geometry quality,
      and available height/use attributes.
- [ ] Define a population-preserving redistribution rule: residential floor area
      if available; footprint area only as a disclosed fallback.
- [ ] Reallocate WorldPop only within its source units, then reaggregate to the
      existing 250 m grid.
- [ ] Test conservation of total population and identify cells affected by
      cross-cell allocation.
- [ ] Compare baseline and dasymetric population-weighted SMCI and population
      shares in the four Scenario B typologies.
- [ ] Keep NAI, MAI, RAC, SMCI, and typology values unchanged.
- [ ] Report limitations: footprint area is not dwelling count, building use may
      be non-residential, and high-rise population cannot be inferred reliably
      without floor/height information.
- [ ] Add tests for conservation, missing footprints, invalid geometry, and
      deterministic allocation.

**Checkpoint 3:** include in the main text only if the population-exposure
interpretation changes materially; otherwise retain as an appendix robustness
result.

## Track 4 - Integration and Publication

- [ ] Add reproducible scripts under `scripts/` and reusable logic under `src/`.
- [ ] Add output contracts to `config/pipeline.json` after the outputs stabilize.
- [ ] Regenerate boundary tables and maps from source inputs rather than editing
      generated artifacts by hand.
- [ ] Update `proposal/proposal_v7.md` with methods, results, and limits that
      distinguish clustering, mechanism, and causality.
- [ ] Record the methodological decision in `docs/decisions.md`.
- [ ] Run `python scripts/check_document_consistency.py`.
- [ ] Run `python scripts/check_agent_ownership.py` when multiple agents work
      on the change.
- [ ] Run `python scripts/agent_gate.py` and `python -m pytest tests/ -v`.
- [ ] Regenerate canonical outputs only on an integration branch, following the
      repository workflow.

**Final acceptance criteria:** all pre-extension core metrics are unchanged,
new results are reproducible from tracked code and declared inputs, tests and
gates pass, and the proposal makes no causal or building-level-population claim
that exceeds the evidence.

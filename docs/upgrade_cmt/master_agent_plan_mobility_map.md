# Master Agent Plan: Publication-Ready Mobility Capability Map and Analytical Consistency

## Mission

Upgrade the `mobility_capability_study` repository so that the analytical pipeline, manuscript-facing outputs, and interactive map are fully consistent, reproducible, publication-ready, and robust to grid design.

The agent must modify source code, regenerate derived outputs, add tests, and document every change. Do not manually edit generated HTML or derived CSV outputs.

## Implementation Checkpoint (2026-08-11)

This plan has been implemented in the dedicated feature worktree/branch
`D:\GREEN-X\mobility-capability-study-smci-nai-upgrade`
(`feat/complete-smci-nai-upgrade`). The primary analytical, cartographic,
robustness, manuscript, and documentation upgrades are complete, including
the equal-weight geometric-mean SMCI migration, 800 m primary NAI, rebuilt
interactive map, shifted-square/equal-area-hexagon sensitivity, Bruno NAI
robustness, data-quality grades, and scenario uncertainty envelope. The last
known full suite result is `161 passed`.

Remaining items are deliberately status-constrained rather than silently
filled with proxies:

- Reliability, generalized-cost, and mixed-traffic RAC contracts are code
  complete but require real observed reliability, cost, and friction inputs.
- The 10-pair manual Android Google Maps motorcycle OD dataset at
  `outputs/validation/manual_motorcycle_validation_template.csv` is now
  validated reproducibly against exact Network D OD routes (MAE 1.90 min).
  The result is correctly limited to motorcycle travel-time plausibility, not
  validation of SMCI, typology, opportunity magnitudes, or causal claims.
- The current West Tay Mo comparison pair must not be promoted: Tay Mo is
  18.6% closer to Hoan Kiem than Ocean Park and fails the preregistered
  +/-15% CBD-distance matching rule. Selecting a different control core or
  changing the matching protocol is a methodological decision requiring user
  direction. A reproducible shortlist of 10 `organic_west` candidate origins
  that pass the distance gate is available at
  `outputs/west_taymo/matching_candidate_shortlist.csv`; it is not a selected
  replacement core.
- The final integration gate cannot pass on the feature branch because
  canonical outputs are policy-locked. Merge/integration authority (or an
  explicitly authorized override) is required; do not bypass the lock.

Current evidence is recorded in `outputs/upgrade/upgrade_completion_report.md`,
`outputs/west_taymo/readiness_status.md`, and
`outputs/west_taymo/matching_preflight.md` in the feature worktree.

## Primary repository targets

```text
scripts/make_interactive_map.py
outputs/maps/ocean_park_interactive.html
src/accessibility.py
src/pilot.py
data/processed/pilot_metrics.csv
data/interim/pilot_grid.gpkg
outputs/validation/
tests/
paper_draft.md
```

The Python analytical pipeline is the source of truth. JavaScript must only render precomputed values and must not independently recompute accessibility, normalization, SMCI, typology, or boundary statistics.

---

# 1. Lock and centralize the analytical specification

## 1.1 Primary NAI threshold

Use:

```text
800 m network-walking distance
approximately 10 minutes at 80 m/min
```

Treat 1200 m as an optimistic sensitivity only.

Remove every map label or description that presents 1200 m as the primary specification.

Create one central configuration object, for example:

```python
ANALYTICAL_SPEC = {
    "nai_primary_threshold_m": 800,
    "nai_sensitivity_thresholds_m": [600, 1000, 1200],
    "smci_form": "geometric_mean",
    "default_scenario": "B",
    "default_metric": "typology",
}
```

All visible labels, formulas, metadata, tests, and build reports must derive from this configuration.

## 1.2 Primary SMCI formula

Promote the equal-weight geometric mean:

\[
SMCI_i =
\left(
NAI_{norm,i}
\times
MAI_{norm,i}
\times
RAC_{norm,i}
\right)^{1/3}
\]

Interpret it as an equal-weight, multiplicative, weak-link-sensitive, zero-preserving composite on a 0–1 scale.

Preserve these properties:

- if any component is zero, SMCI is zero;
- ordinal ranking is identical to the original product;
- the geometric mean improves interpretability and reduces compression near zero;
- product versus geometric mean is not an independent robustness test;
- partial compensation among positive components remains possible.

Recalculate SMCI at the individual cell level. Never transform an aggregate mean by taking its cube root.

## 1.3 Robustness specifications

Retain:

\[
SMCI^{ADD}_i = \frac{NAI_i + MAI_i + RAC_i}{3}
\]

as the meaningful compensatory sensitivity.

Optionally retain:

\[
SMCI^{MIN}_i = \min(NAI_i, MAI_i, RAC_i)
\]

as an extreme bottleneck sensitivity.

Do not describe product versus geometric mean as robustness.

## 1.4 Scenario language

Use:

```text
Scenario A — conventional-transit reference
Scenario B — VinBus network assumption
Modeled difference — Scenario B minus Scenario A
```

Do not use causal labels such as:

```text
VinBus effect
caused by VinBus
intervention impact
```

unless a causal design is introduced.

---

# 2. Retain the 250 m square grid as primary

## 2.1 Primary geometry

Keep:

```text
regular 250 × 250 m square grid
462 cells
```

Use the square grid because:

- travel impedance is calculated on observed networks rather than through cell adjacency;
- WorldPop and dasymetric population inputs are raster-based;
- Queen, Rook, and k-nearest-neighbour spatial weights are already implemented;
- the 250 m cell scale aligns with the boundary-distance analysis.

Do not replace the primary grid with hexagons.

## 2.2 Improve grid documentation

Document:

- projected CRS used to generate the grid;
- grid anchor/origin coordinates;
- exact cell width and height;
- whether cells are clipped or retained whole;
- routing-origin construction;
- network snapping method;
- maximum snap distance;
- count of failed or distant snaps.

## 2.3 Routing origin

Prefer:

```text
building-weighted or population-weighted centroid
```

then snap to the nearest accessible walking-network node.

If only geometric centroids are available, retain them but add:

- maximum snap distance;
- diagnostics for origins snapped across barriers;
- count and distribution of snap distances;
- sensitivity using building-weighted centroids where possible.

## 2.4 Grid robustness

Add two robustness families.

### Shifted-square grids

Create grids shifted by half a cell:

```text
+125 m X
+125 m Y
+125 m X and Y
```

### Equal-area hexagonal grid

Primary square area:

\[
250 \times 250 = 62{,}500\ m^2
\]

Use a regular hexagon with approximately:

```text
side length = 155.1 m
area = 62,500 m²
```

Keep all networks, POIs, thresholds, scenarios, normalization rules, and study extent constant.

Compare:

- Spearman correlation of NAI, MAI, RAC, and SMCI;
- population-weighted mean SMCI;
- zero-access share;
- typology agreement;
- boundary discontinuity;
- Scenario B minus A direction;
- High–High and Low–Low cluster locations.

The objective is not identical cell values. The objective is stability of substantive conclusions.

---

# 3. Refactor the map data model

## 3.1 One geometry, multiple analytical fields

Use one grid geometry and attach all scenario values to each feature.

Required cell properties:

```text
cell_id
population
population_density
origin_lon
origin_lat
snap_distance_m
inside_project
share_inside_project
boundary_side
distance_to_boundary_m
boundary_band

NAI
NAI_norm

MAI_A
MAI_B
MAI_A_norm
MAI_B_norm

RAC_A
RAC_B
RAC_A_norm
RAC_B_norm

SMCI_A
SMCI_B
Delta_SMCI

SMCI_add_A
SMCI_add_B
SMCI_min_A
SMCI_min_B

typology_A
typology_B
typology_transition

zero_NAI
zero_MAI_A
zero_MAI_B
zero_RAC_A
zero_RAC_B
zero_SMCI_A
zero_SMCI_B

has_data
```

Do not create duplicate polygon sets for Scenario A and B.

## 3.2 Missing data must not become zero

Replace any conversion of `NaN` to `0.0`.

Use:

```python
def safe_float(value):
    return None if pd.isna(value) else float(value)
```

Distinguish:

```text
No data
Structural zero
Positive value
```

## 3.3 Centralized metadata dictionary

Create one Python metadata dictionary and serialize it into JavaScript.

It must control:

- field name;
- label;
- unit;
- formatter;
- description;
- scenario availability;
- scale type;
- palette;
- zero handling;
- histogram behavior;
- popup labels;
- chart labels.

Example:

```python
METRIC_META = {
    "nai": {
        "label": "Neighborhood Accessibility Index",
        "unit": "reachable POIs",
        "formatter": "integer",
        "scenario_invariant": True,
        "scale": "sequential",
    },
    "smci": {
        "label": "Sustainable Mobility Capability Index",
        "unit": "0–1 index",
        "formatter": "float4",
        "scenario_invariant": False,
        "scale": "sequential",
    },
    "delta_smci": {
        "label": "Modeled difference: Scenario B − A",
        "unit": "index difference",
        "formatter": "signed_float4",
        "scale": "diverging_zero_centered",
    },
}
```

Do not maintain separate hard-coded field-to-label mappings in Python, HTML, JavaScript, legends, and charts.

Add tests that verify every displayed label maps to the intended field.

---

# 4. Correct all map scales and palettes

## 4.1 Sequential metrics

Use colour-blind-friendly sequential palettes for:

```text
NAI
MAI
RAC
SMCI
population
population density
```

Recommended:

```text
Viridis
Cividis
Inferno
YlGnBu
```

Do not use the current diverging Spectral palette for one-directional variables.

Use language:

```text
lower value
higher value
```

not:

```text
cold
warm
```

## 4.2 Shared Scenario A/B bounds

For each scenario-dependent metric, derive common bounds from A and B together.

Recommended robust bounds:

```python
lo = min(q02_A, q02_B)
hi = max(q98_A, q98_B)
```

Clamp values outside the visual bounds, but preserve exact values in the popup.

The legend must mark:

```text
≤ lower bound
≥ upper bound
```

## 4.3 Delta_SMCI

Use a dedicated diverging scale centered exactly at zero.

Calculate:

```python
q_low = quantile(delta_values, 0.02)
q_high = quantile(delta_values, 0.98)
max_abs = max(abs(q_low), abs(q_high))
delta_bounds = [-max_abs, max_abs]
```

Include negative, zero, and positive values in the histogram.

Suggested direction:

```text
negative = orange/red
zero = neutral light grey
positive = blue/green
```

Use:

```python
DELTA_EPSILON = 1e-10
```

to classify:

```text
Declined
Unchanged
Improved
```

Verify the counts match the analytical pipeline.

## 4.4 Typology palette

Use a colour-blind-safe categorical or bivariate palette.

Do not rely on red versus green alone.

The colour logic should reflect:

```text
NAI axis
MCS axis
```

and make clear that the four classes are nominal categories rather than a continuous quality scale.

---

# 5. Make structural zero a first-class state

Structural-zero cells must be automatically distinguishable when viewing:

```text
NAI
SMCI_A
SMCI_B
Typology
```

Use a dedicated style, such as:

```text
neutral grey fill
diagonal hatch or dotted pattern
white dashed border
```

Do not place zero cells on the same sequential scale as low-positive cells.

The legend must define:

```text
No data:
Metric could not be calculated.

Structural zero:
At least one required component is absent.

Positive:
All required components exist, although joint capability may remain weak.
```

The selected-cell panel must report the exact zero reason:

```text
NAI = 0
MAI = 0
RAC = 0
multiple components = 0
```

---

# 6. Redesign controls around scenario and metric

## 6.1 Scenario selector

Provide:

```text
Scenario A
Scenario B
Difference B − A
```

## 6.2 Metric selector

Provide:

```text
Typology
NAI
MAI
RAC
SMCI
Population
Population density
Population exposure
Boundary fragmentation
```

Rules:

- NAI is scenario-invariant;
- Difference is disabled for NAI;
- Typology difference is represented as transition, not subtraction.

## 6.3 Typology transition

Create:

```text
No class change
Moved toward Integrated Capability
Moved away from Integrated Capability
Changed between intermediate classes
```

Also show exact transition in the selected-cell panel:

```text
Scenario A: Fragmented Capability
Scenario B: Integrated Capability
```

## 6.4 Shareable state

Persist current controls in the URL:

```text
?scenario=B&metric=smci&preset=capability
```

---

# 7. Add boundary-fragmentation functionality

## 7.1 Boundary attributes

Calculate in projected CRS:

```text
share_inside_project
inside_project
boundary_side
distance_to_boundary_m
boundary_band
```

Use:

\[
ShareInside_i =
\frac{Area(cell_i \cap project)}{Area(cell_i)}
\]

Suggested classification:

```python
if share_inside >= 0.75:
    boundary_side = "Inside"
elif share_inside <= 0.25:
    boundary_side = "Outside"
else:
    boundary_side = "Boundary-straddling"
```

Boundary bands:

```text
0–250 m
250–500 m
500–1000 m
1000–2000 m
```

## 7.2 Exact study-area boundary

Do not use a convex hull and label it as an exact study boundary.

Use:

```python
study_boundary_geom = unary_union(grid.geometry)
```

If simplification is required:

```python
study_boundary_geom.simplify(tolerance, preserve_topology=True)
```

## 7.3 Boundary map mode

Display:

- project boundary;
- study-area boundary;
- inside/outside/straddling cells;
- distance bands;
- optional network crossing points;
- selected-cell distance and inside share.

Add summary statistics to the panel:

```text
inside median SMCI
outside median SMCI
difference
bootstrap interval
```

Label this as descriptive, not causal.

---

# 8. Add population and exposure views

## 8.1 Population layers

Add:

```text
population per cell
population density, people/km²
```

## 8.2 Exposure layers

Add:

```text
population in structural-zero cells
population in Motorcycle Lock-in
population exposed to low capability
population-weighted Delta_SMCI
```

A possible visualization diagnostic is:

\[
Exposure_i = Population_i(1-SMCI_i)
\]

Clearly label it as a diagnostic, not a validated independent index.

Do not distort polygon area. Use:

- separate choropleth;
- transparent overlay;
- proportional circles at origins.

---

# 9. Improve selected-cell interaction

## 9.1 Selected-cell panel

Display:

```text
Cell ID
Scenario
Typology
Typology transition
Boundary side
Distance to boundary
Share inside project
Population
Population density
Origin type
Snap distance
NAI raw / normalized
MAI raw / normalized
RAC raw / normalized
SMCI
Delta_SMCI
Structural-zero reason
```

## 9.2 Cell-level comparison chart

Add a compact Scenario A versus B chart for:

```text
MAI
RAC
SMCI
```

Also add a component-balance chart:

```text
NAI_norm
MAI_norm
RAC_norm
```

The objective is to reveal the weak link rather than only displaying the composite.

Use one chart library version only.

Do not duplicate Chart.js or load unused UI bundles.

---

# 10. Reduce visual clutter and improve presets

## 10.1 Default state

Enable:

```text
Scenario B
Typology
Project boundary
Study-area boundary
Structural-zero rendering
```

Disable:

```text
POIs
VinBus routes
VinBus stops
Hanoi GTFS stops
Population overlay
Boundary bands
```

## 10.2 Presets

Add:

```text
Capability
Transit network
Boundary fragmentation
Population exposure
Scenario comparison
```

## 10.3 Layer order

Recommended order:

```text
basemap
grid fill
structural-zero pattern
population overlay
boundary bands
POIs
routes
stops
project boundary
selected-cell highlight
```

The project boundary must remain visible above analytical layers.

---

# 11. Improve map extent and navigation

Default extent:

```javascript
map.fitBounds(gridLayer.getBounds(), {padding: [20, 20]});
```

Do not fit to the entire VinBus route network by default.

Add buttons:

```text
Fit study area
Fit project boundary
Show full VinBus network
Reset view
```

---

# 12. Performance architecture

## 12.1 Precompute in Python

Precompute:

```text
all metrics
normalization
SMCI
typology
boundary attributes
population exposure
histograms
visual bounds
```

JavaScript should only:

```text
switch field
apply style
update legend
update panel/chart
toggle layers
```

## 12.2 Load once

Load or embed the analytical dataset once.

Switching metric, scenario, or palette must not reload, unzip, or reparse the dataset.

## 12.3 Current scale

For 462 cells, retain Leaflet GeoJSON polygon interaction.

Do not implement Bruno-style invisible circles or Canvas hit layers at this scale.

## 12.4 Future citywide scale

Only if the map grows to thousands or tens of thousands of cells, consider:

```text
TopoJSON
GeoJSON gzip
FlatGeobuf
Leaflet VectorGrid
MapLibre GL
WebGL
viewport culling
spatial index
```

Document the threshold for migration, but do not introduce unnecessary complexity now.

---

# 13. Accessibility and responsive design

Use:

```html
<html lang="en">
```

unless a real language toggle is implemented.

Add responsive layout for widths below 768 px.

Ensure:

- controls are keyboard accessible;
- selected states are visually clear;
- palettes remain interpretable under common colour-vision deficiencies;
- patterns or labels supplement colour;
- main analytical meaning remains understandable in greyscale.

---

# 14. Automated tests

Create or expand:

```text
tests/test_interactive_map.py
tests/test_grid_sensitivity.py
tests/test_metric_metadata.py
```

## 14.1 Analytical consistency

Verify:

```text
462 unique cells
SMCI geometric mean recomputed correctly per cell
zero component implies zero SMCI
Scenario A/B normalization bounds are shared
Delta = B − A
improved/unchanged/declined counts match outputs
NAI primary threshold = 800 m
population total is conserved
missing values are not converted to zero
```

## 14.2 Metadata mapping

Verify:

```text
every metric field has one label
every chart label maps to the correct field
every legend uses the correct unit
no duplicate or conflicting category mapping
```

This test must prevent the category-label mismatch found in the Bruno frontend.

## 14.3 Grid sensitivity

Verify:

```text
shifted grids generated successfully
equal-area hexagons are approximately 62,500 m²
substantive comparison metrics are produced
boundary conclusions are summarized for every grid
```

## 14.4 Geometry

Verify:

```text
valid grid geometries
valid project boundary
valid dissolved study boundary
share_inside in [0,1]
distance_to_boundary >= 0
boundary bands mutually exclusive
origin snap distances non-negative
```

## 14.5 JavaScript smoke tests

If Playwright is available:

1. Open generated map.
2. Switch Scenario A/B.
3. Switch SMCI/Delta.
4. Confirm Delta legend is zero-centered.
5. Click a cell.
6. Confirm correct fields and labels.
7. Toggle boundary mode.
8. Toggle population mode.
9. Confirm no console errors.
10. Test mobile width.

## 14.6 Visual regression

Capture:

```text
default typology
SMCI_A
SMCI_B
Delta_SMCI
structural-zero map
boundary fragmentation
population exposure
mobile layout
```

---

# 15. Documentation and build report

Create:

```text
outputs/maps/README.md
outputs/maps/map_build_report.md
outputs/maps/screenshots/
```

The build report must include:

```text
commit SHA
timestamp
input file hashes
NAI threshold
SMCI form
cell count
zero-cell count
population total
Scenario A/B visual bounds
Delta symmetric range
grid CRS and anchor
origin method
snap-distance summary
HTML size
test results
```

Canonical generation command:

```bash
python scripts/make_interactive_map.py
```

Optional CLI:

```bash
python scripts/make_interactive_map.py \
  --nai-threshold 800 \
  --smci-form geometric_mean \
  --default-scenario B \
  --default-metric typology
```

---

# 16. Required deliverables

1. Updated analytical source code.
2. Recomputed cell-level metrics.
3. Updated manuscript values affected by geometric-mean SMCI.
4. Updated `scripts/make_interactive_map.py`.
5. Regenerated `outputs/maps/ocean_park_interactive.html`.
6. Grid-shift and equal-area hexagon sensitivity outputs.
7. Automated tests.
8. Visual regression screenshots.
9. Build report.
10. Section-by-section change log.
11. Old/new table for every recalculated headline SMCI value.
12. List of unresolved data or implementation limitations.

---

# 17. Implementation order

## Phase A — Analytical correctness

1. Centralize configuration.
2. Lock 800 m NAI.
3. Promote geometric-mean SMCI.
4. Recompute all cell-level and aggregate outputs.
5. Add Scenario A fields.
6. Separate missing data from zero.
7. Add metadata tests.

## Phase B — Cartographic correctness

8. Replace sequential palettes.
9. Add shared A/B bounds.
10. Fix Delta scale and histogram.
11. Add structural-zero rendering.
12. Fix typology palette.
13. Correct all labels and units.

## Phase C — Research functionality

14. Separate scenario and metric selectors.
15. Add typology transition.
16. Add boundary attributes and map mode.
17. Replace convex hull with exact dissolved boundary.
18. Add population and exposure layers.
19. Add selected-cell comparison chart.

## Phase D — Robustness

20. Add shifted-square grids.
21. Add equal-area hexagonal grid.
22. Compare correlations, kappa, population exposure, boundary findings, and scenario direction.
23. Document whether substantive conclusions remain stable.

## Phase E — Product quality

24. Reduce default clutter.
25. Add presets.
26. Focus default extent on the study area.
27. Add responsive and accessible UI.
28. Add Playwright and visual regression tests.
29. Regenerate documentation and build report.

---

# 18. Non-goals and prohibited shortcuts

Do not:

- replace the primary square grid with hexagons;
- copy Bruno's frontend architecture wholesale;
- reload the dataset when switching layers;
- create invisible interaction circles for 462 cells;
- define labels independently in multiple files;
- clip displayed values without preserving exact popup values;
- classify missing values as zero;
- use a sequential palette for signed Delta;
- use causal wording for scenario differences;
- manually patch generated HTML;
- fabricate recalculated values when cell-level data are unavailable.

If required data are missing, mark:

```text
[RECALCULATION REQUIRED]
```

and list the exact file, field, or pipeline stage needed.

---

# 19. Final acceptance checklist

The work is complete only when:

- [ ] The primary grid is documented as 250 × 250 m square.
- [ ] Shifted-square and equal-area hexagon sensitivities exist.
- [ ] Primary NAI is 800 m everywhere.
- [ ] Primary SMCI is the equal-weight geometric mean.
- [ ] Every SMCI-derived value is recomputed from cell-level data.
- [ ] Scenario A and B values exist in one shared geometry.
- [ ] Missing data and structural zero are distinct.
- [ ] Scenario A/B maps use shared bounds.
- [ ] Delta uses a symmetric diverging scale centered at zero.
- [ ] Negative, zero, and positive Delta values appear correctly.
- [ ] Structural-zero cells are visually distinct.
- [ ] Boundary-straddling cells and distance bands are available.
- [ ] Population and exposure layers are available.
- [ ] The selected-cell panel explains the weak link.
- [ ] Metric labels and fields come from one metadata dictionary.
- [ ] The map loads data once and only restyles on control changes.
- [ ] Default view focuses on the 462-cell study area.
- [ ] POIs, routes, and stops are off by default.
- [ ] No causal scenario language remains.
- [ ] Automated analytical, geometry, metadata, UI, and visual tests pass.
- [ ] Generated outputs and manuscript values are synchronized.
- [ ] A complete change log and build report are delivered.

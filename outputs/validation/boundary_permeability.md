# Boundary Permeability Audit

> This is a topology and routing diagnostic. It does not identify a causal effect of the Ocean Park boundary.

## Crossing Supply

| mode | boundary_length_km | directed_crossing_edges | physical_crossings | physical_crossings_per_km | restricted_crossings | components | components_spanning_boundary | restriction_tag_coverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| walking | 10.107718 | 118 | 59 | 5.837124 | 0 | 1 | 1 | 0.0 |
| motorcycle | 10.107718 | 40 | 31 | 3.066963 | 0 | 1 | 1 | 0.0 |

## Near-Boundary Detours

| mode | pairs | reachable | median_detour_ratio | max_detour_ratio |
| --- | --- | --- | --- | --- |
| motorcycle | 39 | 39 | 2.357803 | 14.939615 |
| walking | 39 | 39 | 2.10484 | 8.606063 |

## Data Interpretation

Crossings are detected where graph-edge endpoints fall on opposite sides of the declared boundary. Access and barrier tags flag potential restrictions, but absent OSM tags do not prove unrestricted access. Approximate edge betweenness uses a fixed seed and samples graph nodes; it is a structural centrality diagnostic, not observed pedestrian or motorcycle flow.

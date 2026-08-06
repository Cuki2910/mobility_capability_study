# Professor Meeting Response - 2026-07-01

This memo converts the 2026-07-01 proposal feedback into concrete design changes.

## 1. Walkability threshold critique

**Feedback.** A 1200 m / 15-minute walking catchment is too directly imported from European
15-minute-city literature. Hanoi/Ocean Park walking conditions differ: heat, humidity,
sidewalk obstruction, crossing stress, motorcycle dominance, and shade quality make 15 minutes
of theoretical network distance less persuasive as a primary local-access threshold.

**Response.**

- Reframe the 15-minute city as a conceptual benchmark, not a fixed European distance standard.
- Treat 1200 m as an optimistic upper-bound sensitivity, not the only defensible primary.
- Run a threshold-response audit for NAI and SMCI at 600 m, 800 m, 1000 m, and 1200 m.
- Select the final primary threshold after checking whether core findings survive stricter
  Hanoi-sensitive cutoffs.
- Add a walkability-comfort limitation: distance is not the same as comfortable walking.
  A future improvement can use shade/tree cover, sidewalk presence, crossing density, and road
  hierarchy to create an impedance-adjusted walking catchment.

**Likely paper wording.** The paper should say it localizes the 15-minute-city idea for a
motorcycle-dependent tropical city rather than applying the 15-minute threshold mechanically.

## 2. Insight / policy impact critique

**Feedback.** The current insight is not strong enough. "VinBus improves mean SMCI but
fragmentation remains" is methodologically correct, but the policy impact needs to be bigger
and easier to act on.

**Response.** Shift the policy claim from a metric result to a governance/planning diagnosis:

- **Enclave accessibility:** Ocean Park can be internally complete while failing to export
  sustainable mobility capability to the surrounding urban fabric.
- **Boundary discontinuity:** compare SMCI/RAC/NAI immediately inside vs outside the project
  edge, not only global means.
- **Transit supply mismatch:** report whether bus supply is dense enough to compete with
  motorcycles, using stop density, route-km density, and access time to stops.
- **Green-but-not-walkable risk:** test whether green branding translates into usable walking
  conditions by adding tree/green/shade indicators where data allow.
- **Public-action levers:** identify where policy should add connectors, bus priority, missing
  local destinations, shade/sidewalk improvements, or external POI integration.

The policy output should become a diagnostic toolkit for authorities evaluating planned
megaprojects, not only a case-study scorecard.

## 3. Extension to another area

**Feedback.** The study probably needs another area. The comparison site must have measurable
features comparable with Ocean Park: station density, route-km of bus service, tree/green
density, POI density, distance to center, and similar baseline metropolitan position.

**Response.**

- Keep the matched-pair idea, but make the comparison variables more explicit and measurable.
- Primary comparison: Ocean Park Scenario A vs control Scenario A, so "planning form" is not
  confused with the private VinBus intervention.
- Secondary layer: Ocean Park Delta_SMCI from VinBus remains the electric-bus intervention result.
- Candidate control remains Trau Quy core unless matching gates fail.

Minimum cross-site comparison indicators:

| Dimension | Indicator |
| --- | --- |
| Metropolitan position | network distance to Hoan Kiem / CBD, bearing, river-bridge path |
| Scale | same bbox size, same 250 m grid |
| Residential demand | WorldPop density distribution |
| Local services | neighborhood POI density, POI mix/diversity, verified POI rate |
| Transit supply | bus stops/km2, bus route-km/km2, average stop access time |
| Green/walk comfort | NDVI/tree/green-space density, shade proxy if available |
| Street structure | intersection density, block size, road hierarchy mix |
| Capability result | pooled/shared-scale SMCI, RAC, boundary gradients |

## 4. 15-minute-city literature direction

Use the literature to support a more careful claim:

- The 15-minute city is useful as a proximity and local-completeness concept.
- Recent work stresses feasibility varies strongly across cities; it should not be applied as
  one universal fixed-distance rule.
- Hanoi-specific walkability evidence matters: new urban areas may be less walkable than older
  mixed neighborhoods, and sidewalk/motorcycle conflicts reduce effective pedestrian access.
- Tropical-climate walkability work supports adding shade, thermal comfort, and sidewalk quality
  as walking-comfort variables.

## 5. Immediate implementation checklist

- [x] Add a threshold-response script/table for 600/800/1000/1200 m NAI.
- [x] Update proposal Section 8.1 so 1200 m is no longer presented as a universal primary.
- [x] Update `docs/decisions.md` Decision #23 after the threshold-response results are rerun.
- [x] Extend `docs/comparison_site_protocol.md` with bus supply, POI density, green/shade, and
      street-structure comparison variables.
- [ ] Add policy-impact outputs: boundary discontinuity, stop-density gap, route-km density,
      POI-density gap, green/walkability comfort gap.
- [x] Add a short 15-minute-city literature note to the proposal references.

## 6. Threshold-response result

Script added: `scripts/nai_threshold_sensitivity.py`.

Output:

- `outputs/validation/nai_threshold_sensitivity.csv`
- `outputs/validation/nai_threshold_sensitivity.md`

Main result:

| Threshold | Zero NAI | Mean NAI | Mean SMCI_B | Improved | Declined | Kappa vs 1200 m |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 600 m | 133/462 (28.8%) | 3.56 | 0.0107 | 262 | 67 | 0.718 |
| 800 m | 88/462 (19.0%) | 6.09 | 0.0133 | 281 | 93 | 0.756 |
| 1000 m | 58/462 (12.6%) | 9.47 | 0.0148 | 295 | 109 | 0.837 |
| 1200 m | 33/462 (7.1%) | 13.47 | 0.0169 | 298 | 131 | 1.000 |

Interpretation: the direction of the VinBus/SMCI story survives stricter walking thresholds,
but the scale of local completeness changes substantially. The paper should therefore use the
threshold audit as evidence of robustness and avoid treating 1200 m as a universal primary
walkability assumption.

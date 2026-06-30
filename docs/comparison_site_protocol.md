# Comparison-Site Matching Protocol — Planned vs Unplanned (Paper #2)

**Status:** design locked *before* data collection (this is the point — site choice and
matching variables are fixed in advance so the comparison cannot be reverse-engineered from
the result).

**Research question (Paper #2).** Does a master-planned green megaproject (Vinhomes Ocean
Park) produce measurably greater sustainable-mobility *capability* than an organically grown,
unplanned settlement of similar size, distance-to-CBD, and metropolitan position — or is the
difference mainly branding plus a private bus line?

**Design type.** Place-based **quasi-experimental spatial comparison** (matched pair, n=2
areas). NOT a causal-inference design: with two areas we report capability-surface
differences, we do **not** claim the master plan *causes* them. Framing must stay comparative-
descriptive (see §6).

This protocol operationalizes the idea raised in `docs/decisions.md` #1 (single-site scope was
chosen for the pilot) and #9 (the "green" dimension must be tested, not assumed). The control
site upgrades the design from descriptive (one site) to comparative (matched pair) — it is a
*counterfactual control*, not a *reproducibility appendix* (which #1 deliberately cut).

---

## 1. Treatment vs control definitions

| | **Treatment** | **Control** |
|---|---|---|
| Site | Vinhomes Ocean Park (master-planned green megaproject) | Trâu Quỳ town, Gia Lâm (organic/unplanned urban settlement) |
| Planning | Top-down master plan, 420 ha, 19.2% construction density | Incremental, market-led growth around the district capital |
| Status | Done (462-cell pilot) | To build (same pipeline, new bbox) |

**Why Trâu Quỳ (decided in advance).**
- Same district (Gia Lâm), same side of the Red River, same ~8–10 km CBD band → minimizes
  metropolitan-position confounding.
- Genuinely unplanned: incremental growth around the district-capital township, not a master
  plan. Dense enough (district capital) that POI/population are non-trivial — unlike the
  thinner rural communes.
- **Not inside the Ocean Park footprint.** Ocean Park spans Đa Tốn + Dương Xá + Kiêu Kỵ + part
  of Trâu Quỳ; the township *core* of Trâu Quỳ is independent and is what we sample. The bbox
  must be drawn over the township core, explicitly **excluding** any cell overlapping the
  Ocean Park boundary (see §4 spillover rule).

**Sites rejected (and why) — recorded so the choice is auditable:**
- **Đa Tốn** — rejected: it is *part of the Ocean Park project territory*, so it cannot be a
  control for it.
- **Kiêu Kỵ / Bát Tràng** — rejected: too small (5.9 km² / village scale) and immediately
  adjacent to Ocean Park → high spillover risk; Bát Tràng's pottery monoculture is also a
  non-representative economic base.

---

## 2. Matching variables — fix these BEFORE building either surface

The comparison is only credible if the two areas differ mainly in *planned vs unplanned*, not
in a dozen other things. Match on the list below; **report every variable you cannot match as
an explicit limitation** (do not hide residual imbalance).

| # | Variable | How to measure | Target | Confound if unmatched |
|---|---|---|---|---|
| M1 | **Network distance to CBD** | shortest-path **on the routable network** (OSM drive graph, Dijkstra) from area centroid to Hoàn Kiếm, **over the actual Red River bridges** — NOT haversine | within ±15% of Ocean Park's value | core "metropolitan reach" confound |
| M2 | Area / extent | same bbox size + cell size (250 m) as the pilot | identical 5×5 km, 250 m cells | scale effects on counts |
| M3 | Cardinal position vs CBD | same bearing band (SE/E of Hoàn Kiếm, east bank) | same sector | radial-access asymmetry |
| M4 | Residential density | WorldPop 2020 per cell; report median + distribution | same order of magnitude | demand-side weighting (Decision #19) differs |
| M5 | Base road network type | classify OSM highway tags (grid vs organic lane structure) | *expected to differ* — this is part of the treatment, report it, don't "match it away" | — |
| M6 | Transit endowment | which networks each area has (see §3) | **control = Scenario A only** | the big one — see §3 |
| M7 | Topography / barriers | rivers, rail, limited-access roads inside bbox | note any hard barriers | artificial zero-access cells |

**Pre-registration discipline.** Write the measured M1–M4 values for *both* areas into this
file *before* computing any SMCI. If a reviewer asks "did you pick the control to flatter Ocean
Park?", the answer is the timestamped matching table, not a post-hoc rationalization.

---

## 3. The VinBus problem — separate "planning" from "the bus" (CRITICAL)

Ocean Park has VinBus; Trâu Quỳ does not. If the comparison is Ocean-Park-with-VinBus vs
Trâu-Quỳ-without, then any difference could be **"one site has a private bus line"**, which is
*not* the same claim as **"the master plan produces better mobility."** Two separate treatments
would be entangled.

**Rule: the headline comparison uses Scenario A (no VinBus) for BOTH sites.**

| Layer | Isolates | Networks |
|---|---|---|
| **Primary comparison** | spatial planning *per se* | Ocean Park **Scenario A** (walk + 2018 baseline transit) vs Trâu Quỳ **Scenario A** |
| Secondary layer | marginal value of the private green bus | Ocean Park Scenario B (+VinBus) as an *added* contribution, reported separately |

This way:
- "Does the *layout* deliver capability?" → answered by A-vs-A.
- "Does the *electric bus* add capability on top?" → answered by Ocean Park ΔSMCI (B−A),
  exactly the pilot's existing result, now contextualized against an unplanned baseline.

NAI, MAI, RAC, SMCI, typology are all computed identically (same `src/`, same thresholds, same
observed-opportunity hierarchy) for both sites.

---

## 4. Spillover & boundary rules

- **Exclude Ocean Park overlap.** Any Trâu Quỳ cell whose geometry intersects the Ocean Park
  project boundary is dropped from the control sample (and the drop count is logged) — otherwise
  Ocean Park's own opportunities leak into the "unplanned" surface.
- **Edge-effect symmetry.** POIs *outside* a bbox but within walking/transit reach of an edge
  cell are counted for both sites equally (the routing already does this; just confirm the POI
  fetch bbox is buffered the same on both).
- **Same buffer.** POI fetch, building footprints, and WorldPop clipping use the same buffer
  distance around each bbox.

---

## 5. Data-collection parity checklist

Each site must be built with the **same** pipeline and the **same** source tiers, or the
comparison measures data quality, not mobility. Reuse `scripts/` verbatim; only the
`--center-lat/--center-lon` (and POI inputs) change.

- [ ] OSM walk + drive graphs (same `fetch_osm_data.py`, same half-box)
- [ ] Overture + OSM POIs merged, **same source-agreement gate** (Overture promotion only if it
      passes the same spot-check rate as Ocean Park's 55/55)
- [ ] Economic enrichment (landuse/office) — same `merge_economic_features.py`
- [ ] Building footprints (VIDA, same confidence ≥0.70) — needed for built-cell mask, since an
      unplanned area will have very different open-space structure
- [ ] WorldPop 2020 aggregation — same raster, same method
- [ ] **Observed-opportunity magnitudes (Decision #21) — the bottleneck.** Trâu Quỳ needs its
      own beds/jobs/enrollment/GLA hierarchy built from scratch. Budget for this; it is the most
      labor-intensive step and the one most likely to introduce asymmetry.
- [ ] Motorcycle calibration (Network D) — identical literature priors, no re-tuning per site

**Coverage-bias guard.** Unplanned areas typically have sparser, harder-to-verify POI data.
Before comparing SMCI, report POI density and verification rate for *both* sites. If control
coverage is materially worse, that is a limitation on the comparison, not a finding about
mobility — say so explicitly.

---

## 6. Interpretation guardrails (what we may and may not claim)

**May claim:**
- "The capability *surfaces* differ: Ocean Park shows [X], Trâu Quỳ shows [Y]."
- "Even Ocean Park's relatively strong cells have RAC_norm ≈ 0.09 (transit uncompetitive with
  the motorcycle), and the unplanned site shows [comparison]."
- "The typology distribution differs between planned and unplanned forms."

**May NOT claim:**
- That the master plan *causes* any difference (n=2, observational, confounded by M1–M7
  residuals).
- That Trâu Quỳ is "representative" of all unplanned Hanoi settlements (it is one matched case).
- A statistical-significance story across two areas — report distributions and effect sizes,
  not p-values on a two-area contrast.

**Typology caveat carried from the pilot:** "Integrated Capability" is a *rank-relative* label
(median split within each surface), not an absolute threshold. When comparing two sites, the
ranks are computed within each site's own distribution — so "Trâu Quỳ has X% Integrated" and
"Ocean Park has 37% Integrated" are **not** directly comparable as absolute quality. For the
cross-site comparison, use **absolute** SMCI / RAC values (or a shared-scale normalization
across both sites' pooled cells), not the within-site typology shares. This mirrors the
shared-scale rule already used for Scenario A/B deltas (Decision #11).

---

## 7. Pre-flight matching table (fill BEFORE any SMCI is computed)

| Variable | Ocean Park | Trâu Quỳ | Matched? | Note |
|---|---|---|---|---|
| M1 network dist → CBD | _to measure_ | _to measure_ | ? | over Red River bridge |
| M2 bbox / cell | 5×5 km / 250 m | (set identical) | — | |
| M3 bearing vs CBD | SE, east bank | SE, east bank | ✓ (prelim) | |
| M4 median pop density | _from grid_worldpop_ | _to measure_ | ? | |
| M5 road structure | planned grid | organic lanes | ✗ (by design) | part of treatment |
| M6 transit | A (+ B w/ VinBus) | A only | controlled via §3 | |
| M7 barriers | lakes (planned) | _to inspect_ | ? | |

Distance reference: Ocean Park centroid (20.9930, 105.9450); Hoàn Kiếm CBD (21.0287, 105.8524);
straight-line 10.4 km (network distance to be measured per M1).

---

## 8. Go / no-go gates

Proceed to full Trâu Quỳ build only if:
1. M1 network distance is within ±15% of Ocean Park's — else the metropolitan-position confound
   is too large; pick another township.
2. POI verification rate for the control reaches the same gate as Ocean Park's Overture
   promotion (no severe category bias) — else coverage bias dominates.
3. The Ocean-Park-overlap exclusion (§4) removes < ~15% of control cells — else the bbox is too
   close to the megaproject and should be shifted.

If any gate fails, the protocol says **change the site or the bbox**, not relax the gate.

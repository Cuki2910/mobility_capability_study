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

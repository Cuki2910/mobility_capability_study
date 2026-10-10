# Methodology guidance

Read implementation rather than maintaining a second formula glossary:

| Question | Source |
| --- | --- |
| Index operators and typology | `src/accessibility.py` |
| Primary RAC and shared Scenario A/B bounds | `src/pilot.py` |
| Primary NAI threshold and SMCI reporting operator | `config/pipeline.json` analytical specification |
| Calibration assumptions and provenance | `src/calibration.py`, production calibration CSV, DEC-030/031 |
| Method changes and rationale | `docs/decisions.md` |
| Proposal methods and limitations | `proposal/proposal_v7.md`, Sections 7-10 and 13 |

## Current baseline and interpretation

The following describes the current pilot, not immutable design requirements. The user's new direction supersedes it. Update affected implementation, tests and documentation; report what changed and request confirmation rather than reverting to this list. Mathematical facts (e.g. monotonic equivalence) and evidence limitations still apply.

- Primary RAC is RAC_time; full-RAC is retained as robustness. Do not treat RAC_time as an unexecuted future contingency (DEC-022).
- Primary SMCI uses the equal-weight geometric mean. The legacy product preserves the same ranking; comparing those operators is a scale audit, not independent robustness. Additive SMCI remains the compensatory alternative (DEC-004/033).
- Typology uses rank-based median splits of NAI and MCS, including ties; k-means is robustness only. Four categories are a construction rule, not evidence of four natural clusters.
- Delta_SMCI requires shared A+B normalization. Separate scenario normalization can invent declines.
- Primary MAI uses strict source-backed magnitudes or explicit exclusions. Source-backed does not mean every magnitude is a facility census; report weak derived tiers.
- Check collinearity using `src/validation.py`. MAI/full-RAC overlap is structural; distinguish the primary RAC_time diagnostics from legacy full-RAC results.
- Network D uses the production calibration CSV. Road-class mapping is a modeling assumption informed by literature, not verified class-specific motorcycle speeds (DEC-030/031). Missing production calibration is a blocker.
- Consumer-app motorcycle checks are small-sample plausibility checks. Do not depend on bulk Google TWO_WHEELER routing for Vietnam.

When a formula changes, update its implementation, meaningful tests, and the corresponding proposal methods together. Change decisions only when a methodological choice changes; regenerate affected outputs through their generators under the repository gate policy.

## Literature and proposal checks

- Verify each substantive claim against the original paper/report where accessible, not just search snippets or an AI synthesis. Confirm title, authors, year, DOI/URL, and the supporting page/table. State whether support comes from full text or an abstract; leave unavailable details unverified.
- Distinguish observed travel speeds from design speeds and legal limits; distinguish a walking-catchment assumption from a locally validated behavioral threshold. Record study location, population, mode, and measurement conditions before transferring evidence to Ocean Park.
- Keep citations and source notes in existing project references; record a decision when evidence changes a methodological choice. Use the research tooling in `docs/agent_workflow.md` when available; missing optional tools do not prevent direct source verification.
- Trace reported results to their source snapshot and operator. Historical product-scale SMCI and refreshed-source previews must not become current geometric-mean headlines through a prose edit. Describe modeled associations and scenario differences without asserting observed mode change or a causal boundary effect.

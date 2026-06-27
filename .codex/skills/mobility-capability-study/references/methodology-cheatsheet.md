# Methodology Cheatsheet

## Core Hypothesis

High neighborhood accessibility alone is insufficient for integrated sustainable mobility capability when walking-and-transit accessibility remains weak relative to motorcycle accessibility.

## Indices

- `NAI`: Neighborhood Accessibility Index, count-based, walking threshold.
- `MAI`: Metropolitan Accessibility Index, magnitude-weighted, walk+transit threshold.
- `RAC`: Relative Accessibility Competitiveness, geometric mean of normalized `RAC_time` and `RAC_opp`.
- `MCS`: Metropolitan Competitiveness Score, geometric mean of normalized `MAI` and `RAC`; classification only.
- `SMCI`: Sustainable Mobility Capability Index, `NAI_norm * MAI_norm * RAC_norm`.
- Scenario A/B deltas must use shared A+B normalization bounds for MAI, RAC subcomponents, RAC composite, and SMCI components. Do not compare separately normalized scenario scores.

## Networks And Scenarios

- Network A: walking.
- Network B: walking + existing transit.
- Network C: walking + existing transit + VinBus.
- Network D: motorcycle, speed-calibrated.
- Scenario A: A + B, no VinBus.
- Scenario B: A + C, with VinBus.
- Delta: `SMCI(B) - SMCI(A)`.

## Classification

Primary typology is median split: high/low `NAI` x high/low `MCS`.

- High NAI, high MCS: Integrated Capability.
- High NAI, low MCS: Fragmented Capability.
- Low NAI, high MCS: Transit-Dependent.
- Low NAI, low MCS: Motorcycle Lock-in.

Use k-means only as robustness cross-check. Report disagreement; do not tune it to match.

## Validation And Robustness

- Additive SMCI alternative: `(NAI_norm + MAI_norm + RAC_norm) / 3`.
- Never use `(NAI*MAI*RAC)**(1/3)` as robustness against multiplicative SMCI.
- Run VIF for MAI/RAC before trusting typology on real data.
- Validate motorcycle times with literature-calibrated speeds plus small manual Google Maps consumer-app spot checks.

## Proposal-Code Consistency

If editing formulas, edit all of:

- `src/accessibility.py`
- `tests/test_accessibility.py`
- `docs/decisions.md` if a decision changes
- `proposal/proposal_v6.docx` Section 3

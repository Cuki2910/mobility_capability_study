# Prompt for Agent: Replace Product SMCI with Geometric Mean

Revise `paper_draft(2).md` so the main Sustainable Mobility Capability Index uses an **equal-weight geometric mean**.

## 1. Replace the formula

Old:

\[
SMCI_i^{P}=NAI_{norm,i}\times MAI_{norm,i}\times RAC_{norm,i}
\]

New:

\[
SMCI_i=
\left(
NAI_{norm,i}\times MAI_{norm,i}\times RAC_{norm,i}
\right)^{1/3}
\]

Define it as an **equal-weight, multiplicative, weak-link-sensitive, zero-preserving composite on a 0–1 scale**.

Suggested Methods wording:

> SMCI was calculated as the equal-weight geometric mean of normalized NAI, MAI, and RAC. The multiplicative specification preserves the conjunctive structure of the framework: a zero value in any component produces zero overall capability, while the cubic root retains the composite on an interpretable 0–1 scale. The transformation changes the reporting scale but not the ordinal ranking of spatial cells.

## 2. Preserve the correct interpretation

State clearly that:

- NAI, MAI, and RAC remain jointly necessary.
- Any zero component still makes SMCI zero.
- \(SMCI^{GM}=(SMCI^{P})^{1/3}\), so rankings, quantile membership, hotspots, and rank-based correlations do not change.
- The geometric mean improves interpretability and reduces compression near zero.
- It does not create a substantively different model or remove partial compensation.
- Product versus geometric mean is **not** an independent robustness test.

## 3. Recalculate all SMCI results

Calculate the new SMCI for each spatial cell first, then recompute:

- descriptive and population-weighted statistics;
- inside–outside and boundary-distance results;
- scenario effects;
- absolute thresholds and typologies;
- all values in the abstract, tables, figures, captions, results, discussion, and conclusion.

Do not calculate:

\[
(\overline{SMCI^{P}})^{1/3}
\]

because this is generally not equal to the mean of cell-level geometric SMCI values.

Quantile classes may retain the same membership, but all reported cut-offs and values must be verified.

## 4. Update interpretation of effects

Geometric-mean scores will be numerically higher than positive product scores below 1, while spatial ordering remains unchanged.

Revise all “times higher” statements because ratios are compressed:

\[
\frac{GM_A}{GM_B}
=
\left(\frac{P_A}{P_B}\right)^{1/3}
\]

Report absolute differences alongside percentages or ratios. Keep zero-access cells separate from low-positive cells.

## 5. Robustness tests

Retain the additive alternative as the meaningful sensitivity test:

\[
SMCI_i^{ADD}=\frac{NAI_i+MAI_i+RAC_i}{3}
\]

Optionally add:

\[
SMCI_i^{MIN}=\min(NAI_i,MAI_i,RAC_i)
\]

as an extreme bottleneck test.

## 6. Scope control

Do not alter NAI, MAI, RAC, normalization, scenarios, study boundaries, or conceptual framing unless recalculated evidence requires it.

Search the full manuscript for: `SMCI`, `product`, `multiplicative`, `geometric mean`, `weak-link`, `zero-access`, `additive`, `ranking`, `quantile`, `boundary`, and `scenario`.

## 7. Data rule and deliverables

If cell-level data or code are unavailable, do not fabricate values. Mark every affected location `[RECALCULATION REQUIRED]`.

Deliver:

1. Revised manuscript.
2. Section-by-section change log.
3. Old/new table of every recalculated SMCI result.
4. List of unresolved items.
5. Confirmation that product versus geometric mean is no longer treated as a robustness comparison.

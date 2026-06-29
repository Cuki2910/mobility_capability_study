"""
Derive MAI domain weights from the UTM-Hanoi travel survey trip-purpose
distribution (replaces the hand-set 0.40/0.20/0.20/0.20 prior).

Why this exists
---------------
The MAI composite weights (`MAI_DOMAIN_WEIGHTS["default"]` in src/accessibility.py)
were a theory-informed analyst prior. A reviewer will ask where 0.40/0.20/0.20/0.20
comes from. This script grounds them in an observed trip-purpose distribution so the
weights are survey-informed and reproducible, with a written provenance trail.

Source
------
UTM-Hanoi household travel survey (N=26,106), Vu Anh Tuan et al.
  - Paper: Nature Scientific Data (2024) https://doi.org/10.1038/s41597-024-02950-9
  - Open data (CC): OSF repository DOI 10.17605/OSF.IO/497US
Survey trip-purpose categories: work, education, shopping, leisure, visit, caring.

HAIDEP 2010 person-trip purpose shares are NOT used: the raw distribution is behind
JICA licensing and could not be obtained without fabricating numbers. UTM-Hanoi is
open and more recent. If a licensed HAIDEP table later becomes available, re-run this
script against it (same mapping) as a sensitivity scheme.

What it does NOT do
-------------------
It does not invent the survey numbers. The trip-purpose counts must be supplied in
`data/raw/utm_hanoi_trip_purpose.csv` (download/transcribe from the OSF dataset or the
paper's Fig. 4). The template ships with blank counts on purpose. This script only
performs the deterministic mapping + renormalization once real counts are present.

Mapping (survey purpose -> MAI opportunity domain)
--------------------------------------------------
  work      -> economic            (employment access)
  education -> higher_education     (education campuses / schools)
  shopping  -> metro_commercial     (retail / GLA)
  caring    -> tertiary_healthcare  (proxy: care/medical errands; see caveat)
  leisure   -> (excluded: not a metropolitan-opportunity domain)
  visit     -> (excluded: social, not an opportunity domain)

Caveat (must stay in the docs): `caring` is an imperfect proxy for healthcare access.
The survey has no dedicated health-trip purpose, and health is essential-but-low-
frequency, so the derived healthcare weight is reported as a survey-informed lower
bound, not a pure frequency. This keeps the weights *survey-informed*, not naively
*survey-derived*. Excluded purposes (leisure, visit) are dropped before renormalizing
so weights sum to 1 over the four MAI domains.

Run
---
  # 1. Fill data/raw/utm_hanoi_trip_purpose.csv with real counts (see template).
  # 2. Then:
  python scripts/derive_mai_weights_utm.py

Outputs
-------
  data/interim/mai_weights_utm_derived.csv   provenance: purpose -> domain -> share
  prints the MAI_DOMAIN_WEIGHTS["utm_derived"] dict to paste into src/accessibility.py
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

# survey purpose -> MAI domain (None = excluded from MAI weighting)
PURPOSE_TO_DOMAIN: dict[str, str | None] = {
    "work": "economic",
    "education": "higher_education",
    "shopping": "metro_commercial",
    "caring": "tertiary_healthcare",
    "leisure": None,
    "visit": None,
}

MAI_DOMAINS = ["economic", "higher_education", "tertiary_healthcare", "metro_commercial"]

RAW_TEMPLATE = Path("data/raw/utm_hanoi_trip_purpose.csv")
OUT_PROVENANCE = Path("data/interim/mai_weights_utm_derived.csv")

TEMPLATE_HEADER = "purpose,count,source_note\n"
TEMPLATE_ROWS = [
    "work,,UTM-Hanoi Fig.4 / OSF 497US — fill observed trip count or share\n",
    "education,,UTM-Hanoi Fig.4 / OSF 497US\n",
    "shopping,,UTM-Hanoi Fig.4 / OSF 497US\n",
    "leisure,,UTM-Hanoi Fig.4 / OSF 497US (excluded from MAI)\n",
    "visit,,UTM-Hanoi Fig.4 / OSF 497US (excluded from MAI)\n",
    "caring,,UTM-Hanoi Fig.4 / OSF 497US (proxy for healthcare)\n",
]


def write_template(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(TEMPLATE_HEADER)
        fh.writelines(TEMPLATE_ROWS)
    print(f"Wrote blank template: {path}")
    print("Fill the `count` column from the UTM-Hanoi distribution, then re-run.")


def load_counts(path: Path) -> dict[str, float]:
    counts: dict[str, float] = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            purpose = (row.get("purpose") or "").strip().lower()
            raw = (row.get("count") or "").strip()
            if not purpose:
                continue
            if purpose not in PURPOSE_TO_DOMAIN:
                raise SystemExit(
                    f"Unknown survey purpose '{purpose}' — extend PURPOSE_TO_DOMAIN."
                )
            counts[purpose] = float(raw) if raw else float("nan")
    return counts


def derive_weights(counts: dict[str, float]) -> tuple[dict[str, float], list[dict]]:
    # aggregate survey counts into the four MAI domains (excluded purposes dropped)
    domain_totals = {d: 0.0 for d in MAI_DOMAINS}
    mapped_total = 0.0
    for purpose, domain in PURPOSE_TO_DOMAIN.items():
        c = counts.get(purpose)
        if c is None or c != c:  # missing / NaN
            raise SystemExit(
                f"Count for '{purpose}' is missing. Fill {RAW_TEMPLATE} completely first."
            )
        if domain is None:
            continue
        domain_totals[domain] += c
        mapped_total += c

    if mapped_total <= 0:
        raise SystemExit("Mapped trip counts sum to 0 — check the input CSV.")

    weights = {d: round(domain_totals[d] / mapped_total, 4) for d in MAI_DOMAINS}

    # provenance rows
    prov = []
    for purpose, domain in PURPOSE_TO_DOMAIN.items():
        prov.append(
            {
                "purpose": purpose,
                "mapped_domain": domain or "(excluded)",
                "count": counts.get(purpose),
                "domain_weight": weights[domain] if domain else "",
            }
        )
    return weights, prov


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--input", type=Path, default=RAW_TEMPLATE,
        help=f"trip-purpose count CSV (default {RAW_TEMPLATE})",
    )
    ap.add_argument(
        "--make-template", action="store_true",
        help="write the blank template CSV and exit",
    )
    args = ap.parse_args()

    if args.make_template:
        write_template(args.input)
        return 0

    if not args.input.exists():
        write_template(args.input)
        return 0

    counts = load_counts(args.input)
    weights, prov = derive_weights(counts)

    OUT_PROVENANCE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PROVENANCE.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(
            fh, fieldnames=["purpose", "mapped_domain", "count", "domain_weight"]
        )
        w.writeheader()
        w.writerows(prov)

    print(f"Wrote provenance: {OUT_PROVENANCE}")
    print("\nDerived UTM-Hanoi MAI domain weights (sum=1 over 4 domains):")
    dict_literal = ", ".join(f'"{d}": {weights[d]}' for d in MAI_DOMAINS)
    print(f'    "utm_derived": {{{dict_literal}}},')
    print("\nPaste into MAI_DOMAIN_WEIGHTS in src/accessibility.py, then decide whether")
    print("to promote it to 'default' (update docs/decisions.md + metrics_reference.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

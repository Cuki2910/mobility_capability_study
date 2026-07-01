# Phase 2 Walkthrough — Observed-Opportunity MAI Enrichment & Data Cleaning

Narrative record of the Phase 2 working session: scraping, citation filtering,
and opportunity-hierarchy optimization for the strict observed MAI specification.
All numbers below are validated against repo artifacts (2026-07-01).

Related: Decisions #18–#23 in `docs/decisions.md`; canonical strict spec is the
build default (`--opportunity-basis observed_strict`, `merged_pois_observed.gpkg`).

## 1. What changed

### 1.1 Commercial data tiering fix
Removed the hard-coded `source_tier = "geometry_measured"` assignment on
commercial POIs. Convenience-format supermarkets (WinMart+, Circle K) using the
standard GLA estimate now fall correctly into `manual_checked`.

### 1.2 Junk filtering & dental exclusion (healthcare 18 → 12)
Mislocated OSM "healthcare" points removed via `include_in_mai = False`:
- **Siêu Thị Người Lớn** (adult retail shop) — misclassified retail.
- **Cương Kinh Bắc** (guard gate) — not a destination.

Outpatient dental / traditional-medicine clinics excluded from tertiary
inpatient-bed index (`tertiary_healthcare` domain):
- Nha Khoa Dr. Hiền, S-Dental Implant, Nha Khoa Hải Âu (OceanPark Dental),
  and other outpatient dental / châm cứu listings.

Result: tertiary healthcare drops **18 → 12** valid high-quality POIs.
(6 total healthcare-domain exclusions: 5 outpatient dental/junk +
1 duplicate generic "Siêu Thị Sức Khỏe Trường Phát".)

### 1.3 Market job calibration by floor area
Replaced flat 80-jobs-per-market with dynamic sizing:
`jobs = GFA × 0.1` (≈1 trader/staff per 10 m² of market floor area).

| Market | Floor area (m²) | Jobs |
|---|---|---|
| Chợ Bún | 974.98 | 97 |
| Chợ Trâu Quỳ | 2,811.04 | 281 |
| Chợ Sinh Viên VNUA | 7,078.73 | 500 (capped) |

### 1.4 FAVRI double-count avoidance
Removed the "Rau quả" abbreviation from the static lookup to avoid doubling the
two independent FAVRI (Viện Nghiên cứu Rau quả) buildings. Floor-area formula
now estimates the two buildings at **133** and **92** (total **225**, close to
the ~200-staff ground truth).

### 1.5 VNUA research-institute keywords
Added "sinh thái", "nông nghiệp", "bệnh cây", "lab" to the classifier so VNUA
research centres (CARES, Plant Disease Center, COSMOS Lab) are assigned to the
`research_institute` group with actual headcounts.

### 1.6 Documentation sync
Final metrics synced into `CLAUDE.md`, `proposal/proposal_v7.md`,
`paper/paper_draft.md`, and this walkthrough.

## 2. Final optimized metrics (validated)

| Metric | Value | Source |
|---|---|---|
| POIs included in MAI | **192** (of 208; 16 excluded) | `merged_pois_observed.gpkg` |
| NAI walking threshold | **800 m / ~10 min** (primary; Decision #27) | `build_accessibility_inputs.py` |
| Mean SMCI_A (walking) | **0.0070** | `outputs/pilot_summary.csv` |
| Mean SMCI_B (walk+transit) | **0.0133** | `outputs/pilot_summary.csv` |
| Mean Delta_SMCI | **0.0063** | `outputs/pilot_summary.csv` |
| Improved / unchanged / declined | **281 / 88 / 93** (60.82% improved) | `pilot_metrics.csv` |
| Zero-NAI cells | **88 / 462 (19.0%)** | `pilot_metrics.csv` |
| VIF(MAI) | **2.93** | `outputs/validation/vif_flags.csv` |
| VIF(RAC_time) | **2.05** | `outputs/validation/vif_flags.csv` |
| Pytest | **80 passed** | `pytest tests/` |

> **Note (2026-07-01, Decision #27):** primary NAI threshold moved 1200 m → **800 m**
> after professor feedback that 1200 m is too far for Hanoi. 1200 m / 15 min is now
> reported as an optimistic upper-bound sensitivity (SMCI_A=0.0092, SMCI_B=0.0169 there).
> The four-typology structure is near-invariant across 600–1200 m.

## 3. Final source-tier distribution (included POIs)

| Source tier | POIs |
|---|---|
| manual_checked | 91 |
| geometry_measured | 44 |
| facility_source | 26 |
| official_source | 17 |
| observed_dasymetric_weak | 8 |
| observed_point | 6 |
| **Total** | **192** |

## 4. Reproduce

```bash
python scripts/derive_all_observed.py          # rebuild merged_pois_observed.gpkg
python scripts/build_accessibility_inputs.py --mode network --gtfs-status baseline_limited
python scripts/run_pilot_metrics.py
python scripts/make_validation_report.py
python scripts/make_supervisor_memo.py
pytest tests/ -q                               # 80 passed
```

Build defaults are the canonical strict spec (`--opportunity-basis observed_strict`
+ `--pois data/interim/merged_pois_observed.gpkg` + `--walking-threshold-m 800`),
reproducing SMCI_A=0.0070 / SMCI_B=0.0133.

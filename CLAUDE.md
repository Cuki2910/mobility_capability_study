# CLAUDE.md

Context file for Claude Code (or any future session) working in this repo.
Read this fully before writing or changing code or the proposal.

## What this project is

Research proposal + analysis pipeline for: *"Fragmented Mobility Capability
in Motorcycle-Dependent Green Megaprojects: A Dual-Scale and
Mode-Competitive Accessibility Framework from Vietnam"* (target: Journal of
Transport Geography). Case study: Vinhomes Ocean Park, Hanoi.

**Core hypothesis:** High neighborhood accessibility alone is insufficient
to generate integrated sustainable mobility capability when Relative
Accessibility Competitiveness (RAC) — walking-and-transit accessibility
relative to motorcycle accessibility — remains low.

Full methodology: `proposal/proposal_v6.docx`. This CLAUDE.md is a map to
the repo and a record of decisions, not a replacement for reading Section 3
of the proposal before touching the analysis code.

## Glossary (used everywhere in code — match these names exactly)

| Term | Meaning |
|---|---|
| **NAI** | Neighborhood Accessibility Index — count-based, walking threshold |
| **MAI** | Metropolitan Accessibility Index — magnitude-weighted, walk+transit threshold |
| **RAC** | Relative Accessibility Competitiveness — geometric mean of RAC_time and RAC_opp |
| **MCS** | Metropolitan Competitiveness Score — geometric mean of normalized MAI and RAC; used for classification only |
| **SMCI** | Sustainable Mobility Capability Index = NAI_norm × MAI_norm × RAC_norm |
| **Network A/B/C/D** | Walking / Walking+existing transit / Walking+existing transit+VinBus / Motorcycle |
| **Scenario A/B** | A = Networks A+B (no VinBus). B = Networks A+C (with VinBus). ΔSMCI = SMCI(B) − SMCI(A) |
| Four typologies | Integrated Capability, Fragmented Capability, Transit-Dependent, Motorcycle Lock-in |

Exact formulas: `src/accessibility.py` (implemented, tested) — this is the
single source of truth for these formulas, not the prose in the .docx.
If you change a formula, update both the code and Section 3 of the
proposal in the same commit.

## Repo structure

```
proposal/              proposal_v6.docx is current. archive/ has v3, v5 for reference.
data/raw/               immutable, as-downloaded. Nothing in here is hand-edited.
data/interim/           cleaned/aligned data (calibrated networks, built grid).
data/processed/         analysis-ready per-grid-cell table (NAI, MAI, RAC, SMCI, typology).
src/                    reusable formulas and pipeline functions. Import, don't duplicate.
  accessibility.py        NAI/MAI/RAC/SMCI/classification formulas — DONE, tested.
  networks.py              network construction — implemented; loads GraphML, applies calibration.
  calibration.py           motorcycle speed calibration — implemented, cited from literature.
  validation.py            VIF check, validation helpers — DONE.
  routing.py               Dijkstra-based NAI/MAI/RAC inputs from GraphML — DONE.
  accessibility_inputs.py  proxy and network input builders — DONE.
scripts/                one-off executable scripts that call src/.
  fetch_osm_data.py        run on a machine with real internet access (NOT this sandbox).
notebooks/              exploratory work only. Promote anything reusable into src/.
tests/                  pytest. Run before trusting any change to src/accessibility.py.
outputs/                figures/tables/results for the paper. Gitignored except structure.
docs/
  data_sources.md          status of every data source — CHECK BEFORE ASSUMING DATA EXISTS.
  decisions.md             why things are the way they are — READ BEFORE CHANGING METHODOLOGY.
```

## Before doing anything else

1. Read `docs/data_sources.md`. VinBus OSM relations are confirmed (39 found);
   Hanoi GTFS is still missing locally — Network B is baseline-limited.
2. Read `docs/decisions.md`. Several things that look like they could be
   "simplified" (theory-first classification, rank-based median split,
   single-site scope, the additive-not-geometric robustness check) were
   deliberately chosen after finding a problem with the alternative. Don't
   revert them without re-reading why.

## Running things

```bash
pip install -r requirements.txt

# On a machine with real internet access (this sandbox cannot reach OSM servers):
python scripts/fetch_osm_data.py
python scripts/fetch_hanoi_gtfs.py   # needed to unlock MAI_A > 0

# Pipeline (run in order):
python scripts/build_accessibility_inputs.py --mode network --gtfs-status missing
python scripts/run_pilot_metrics.py
python scripts/make_validation_report.py
python scripts/make_supervisor_memo.py

# Anywhere:
pytest tests/ -v   # must be 22 passed
```

## Known constraints / gotchas

- **No internet access to OSM/Overpass from this sandbox.** Data-fetching
  scripts are written but must be run on a real machine.
- **Google Maps TWO_WHEELER mode at the API level is unconfirmed for
  Vietnam** — don't design any step that depends on bulk/automated
  motorcycle routing via the API. See `docs/data_sources.md`.
  Manual spot-check template: `outputs/validation/manual_motorcycle_validation_template.csv`
  (10 pre-filled OD pairs with lat/lon for Ocean Park area).
- **Hanoi GTFS missing locally.** Network B remains baseline-limited; MAI_A = 0
  for all pilot cells until a current feed is downloaded. See `data/interim/hanoi_gtfs_source.json`.
- **theory_first_typology uses rank-based split**, not `>= np.median()`, to
  guarantee 4 typologies even when MCS has a mass point at 0. See decision #2.
- **MAI and RAC are expected to be correlated by construction**, not just by
  chance — see decision #3. Always run VIF check
  (`src/validation.py::collinearity_check`) before trusting the 4-way
  classification on new data. Network-v1 pilot VIF: NAI=1.76, MAI=1.81, RAC=1.04 (all OK).
- **Motorcycle speed calibration** uses literature priors from JICA HAIDEP (2010)
  and Nguyen et al. (2018). Source citations in `data/raw/motorcycle_speed_calibration.csv`.

## Current status (update this section as the project progresses)

- [x] Proposal text finalized at v6 (theory-RAC consistency, classification
  logic, collinearity check, validation hierarchy all resolved).
- [x] Analysis formulas (`src/accessibility.py`) implemented and tested. 22 tests pass.
- [x] OSM check for existing VinBus route relations (39 found 2026-06-21;
  `data/raw/vinbus_overpass_relations.json`).
- [x] VinBus Overpass geometry dump for Ocean Park-facing refs (`E01,E02,E03,E10,OCP1,OCP2`);
  `data/raw/vinbus_overpass_relations_geom.json`.
- [x] Real OSM data fetch: 462 grid cells, 106 POIs (`data/interim/pilot_data_manifest.json`).
- [x] Motorcycle speed calibration CSV with JICA/literature citations:
  `data/raw/motorcycle_speed_calibration.csv`.
- [x] Network-v1 accessibility inputs: Dijkstra NAI + motorcycle travel times from GraphML,
  VinBus corridor proxy for MAI_B/RAC_B. `data/interim/pilot_accessibility_inputs.csv`.
- [x] Pilot metrics (network-v1): 4 typologies confirmed in Scenario B, VIF all < 5,
  robustness rho=0.41. `data/processed/pilot_metrics.csv`, `outputs/pilot_summary.csv`.
- [x] Validation outputs: VIF flags, correlation matrix, robustness summary.
  `outputs/validation/`. Motorcycle spot-check template pre-filled with 10 OD pairs.
- [x] Self-audit report generated by `scripts/project_self_audit.py` at `outputs/project_self_audit.md`.
- [x] POI audit: `outputs/poi_audit.md`. Manual spot-check still pending (20 records needed).
- [x] Download Hanoi GTFS — World Bank CC-BY 4.0, 1.51 MB, Jun 2020 vintage (224 routes, 7,670 stops).
  `data/raw/hanoi_gtfs.zip`. Status = `baseline_limited` (service dates 2018, stop geometry valid).
  MAI_A now nonzero for 162/462 cells using stop proximity. Network B timetable cũ → vẫn là
  baseline_limited nhưng stop geometry được dùng cho stop_accessibility().
- [x] Verify WorldPop using actual raster: `data/raw/worldpop/vnm_ppp_2020.tif`, ~92.77m metadata resolution, adequate for 250m grid.
- [ ] Integrate WorldPop raster into MAI magnitude weighting if needed.
- [ ] Manual motorcycle spot-check: fill `outputs/validation/manual_motorcycle_validation_template.csv`
  on Android device using Google Maps motorcycle mode.
- [ ] Supervisor review of v6 + pilot results.
- [ ] Full study area data collection and analysis.

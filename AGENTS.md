# AGENTS.md

Guidance for any AI coding agent (Codex, Cursor, etc.) working in this repo.
Claude Code reads `CLAUDE.md`; this file points everyone to the same sources of
truth so the two agents do not drift.

## Read these first (canonical, in order)

1. **`CLAUDE.md`** — the master context file: project description, glossary,
   repo map, decisions log pointer, gotchas, and the live status checklist.
   This is the single canonical brief. Read it fully before changing code,
   data, or the proposal.
2. **`docs/data_sources.md`** — status of every data source. Check before
   assuming any dataset exists.
3. **`docs/decisions.md`** — *why* things are the way they are. Several choices
   that look "simplifiable" were made deliberately. Do not revert without
   re-reading.
4. **`proposal/proposal_v7.md`** — current methodology (Section 3). `proposal_v6.docx`
   is the prior Word version, reference only.

## Sources of truth (do not duplicate; import / cite)

- **Formulas (NAI/MAI/RAC/MCS/SMCI/typology):** `src/accessibility.py` — the
  single source of truth, NOT the prose. If you change a formula, update both
  the code and proposal Section 3 in the same commit, and update the tests.
- **Glossary terms:** match exactly — `NAI`, `MAI`, `RAC`, `MCS`, `SMCI`,
  Network `A/B/C/D`, Scenario `A/B`. Definitions live in `CLAUDE.md`.
- **Headline numbers / current status:** the status section of `CLAUDE.md` and
  `outputs/pilot_summary.csv`. If `outputs/project_self_audit.md` disagrees,
  regenerate it (`python scripts/project_self_audit.py`).

## Two GTFS sources — do not confuse

- **Network B** = `data/raw/hanoi_gtfs.zip` (World Bank, file vintage 2020 but
  *service dates 2018*, pre-VinBus → status `baseline_limited`).
- **Network C** = `data/raw/vinbus_pseudo_gtfs_fixed/` (no official VinBus GTFS;
  scraped via `scripts/scrape_vinbus.py`, QC'd via `scripts/fix_vinbus_gtfs.py`).

## Guardrails

- Single-site scope: Vinhomes Ocean Park only.
- Theory-first rank-based median-split typology; k-means is robustness only.
- Additive SMCI robustness, not geometric (geometric is vacuous — see decisions).
- Delta_SMCI must use shared A+B normalization bounds (see `src/pilot.py`).
- Expect MAI/RAC collinearity by construction; run `validation.collinearity_check`
  and report RAC_time-only sensitivity when VIF is high.
- No raw OSM driving speeds for motorcycle Network D — use literature-derived
  speed multipliers (`src/calibration.py`).
- No dependence on Google TWO_WHEELER bulk API for Vietnam; manual consumer-app
  spot-checks only.
- Keep functions in `src/`, scripts thin in `scripts/`, notebooks exploratory only.

## After changes

- Run `pytest tests/ -v` (must be 61 passed) after touching `src/accessibility.py`,
  `validation`, network construction, or calibration.
- Report: files changed, tests run, remaining data blockers.

## Two-agent coordination (Claude + Codex)

- Treat `CLAUDE.md` + `docs/` as shared truth; agent-private memory is NOT shared
  between Claude and Codex, so durable facts belong in these files.
- Avoid both agents editing the same file in parallel — split work by area
  (e.g. one on pipeline/`src`, one on proposal text) to prevent merge conflicts
  and methodology drift.

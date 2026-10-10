# AGENTS.md

## Change authority and confirmation

The user's latest explicit direction takes precedence over the working baseline below and historical plans. Methodology, study scope, input sources, thresholds, and classification may change. Implement the requested change as a reviewable draft; never restore an old design merely to satisfy old prose or tests. Update affected code, evidence, tests, and guidance to the new intent.

After each change batch, present `.agent/change_review.md` with before/after, purpose, effects, checks, and remaining data limitations; ask the user to confirm or request revisions. Until an explicit reply, status is `PENDING_USER_CONFIRMATION`. Passing tests is not approval. Do not present the draft as an accepted research decision or publish/merge it before confirmation. Existing authorization permits preparing and checking the complete draft.

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
4. **`proposal/proposal_v7.md`** — the only retained proposal; methodology in Sections 7-10, limitations in Section 13. Section 3 contains research questions.

## Sources of truth (do not duplicate; import / cite)

- **Formulas (NAI/MAI/RAC/MCS/SMCI/typology):** `src/accessibility.py` — the
  single source of truth, NOT the prose. If you change a formula, update both
  the code and corresponding proposal methods in the same commit, and update the tests.
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

## Working baseline (changeable, not a design lock)

- Current scope: Vinhomes Ocean Park. Expand when the user requests it.
- Theory-first rank-based median-split typology; k-means is robustness only.
- Primary SMCI is the equal-weight geometric mean; additive is compensatory robustness.
  Comparing the legacy product with the geometric mean is a scale audit, not independent robustness (DEC-033).
- Delta_SMCI must use shared A+B normalization bounds (see `src/pilot.py`).
- RAC_time is primary; full-RAC is robustness (DEC-022). MAI/full-RAC overlap is
  structural; run `validation.collinearity_check` and distinguish primary from legacy diagnostics.
- Network D requires the production `data/raw/motorcycle_speed_calibration.csv`;
  road-class speeds are modeling assumptions informed by literature, not verified
  class-specific observations (DEC-030/031; `src/calibration.py`).
- No dependence on Google TWO_WHEELER bulk API for Vietnam; manual consumer-app
  spot-checks only.
- Keep functions in `src/`, scripts thin in `scripts/`, notebooks exploratory only.

## After changes

- With multiple agents, create `.agent/ownership.json` from the tracked example and
  run `python scripts/check_agent_ownership.py` before handoff.
- After changes, run `python scripts/agent_gate.py` before handoff; read-only explanations
  need no gate. The tracked policy at
  `config/agent_policy.json` selects checks and reports coupled/output changes for confirmation;
  see `docs/agent_workflow.md`. Historical method/status assertions are not acceptance criteria.
- Run `pytest tests/ -v` (the full current suite must pass) after touching
  `src/accessibility.py`, validation, network construction, or calibration.
- Report: files changed, tests run, remaining data blockers.

## Two-agent coordination (Claude + Codex)

- Treat `CLAUDE.md` + `docs/` as shared truth; agent-private memory is NOT shared
  between Claude and Codex, so durable facts belong in these files.
- Avoid both agents editing the same file in parallel — reserve file ownership in
  `.agent/ownership.json` and use separate Git worktrees as specified in
  `docs/agent_workflow.md`.

---
name: mobility-capability-study
description: "Work on the Ocean Park mobility-capability-study repository: analysis, research data, proposal/paper consistency, and workspace maintenance. Use for tasks in this project or explicitly about its methodology; not unrelated Hanoi transport research."
---

# Mobility Capability Study

The user's latest direction supersedes historical designs. Prepare the requested draft, update affected implementation/tests/guidance, and present the batch report before asking for confirmation. Never revert an authorized new idea to satisfy an old method assertion. Until the user replies, label the batch `PENDING_USER_CONFIRMATION`; do not claim research adoption or publish/merge it.

## Sources and scope

- Follow the repository's `AGENTS.md`. Read `CLAUDE.md`, `docs/data_sources.md`, `docs/decisions.md`, and `proposal/proposal_v7.md` in that order before changes; reuse context already read this session unless it changed.
- Formulas live in `src/accessibility.py`; Scenario A/B normalization and primary RAC selection live in `src/pilot.py`; analytical defaults live in `config/pipeline.json`. If prose conflicts, inspect these sources and the latest applicable decision; identify the stale guidance before correcting it. Preserve dated history.
- `proposal/proposal_v7.md` is the only retained proposal. Methods are in Sections 7-10; Section 3 contains research questions.
- Derive current status from repository artifacts and actual local files. A recorded download does not prove the dataset exists in this checkout. Do not hard-code a current blocker or headline number in this skill.
- Keep the requested scope. Workspace cleanup does not require data acquisition or pipeline regeneration. Ocean Park is the current study; extend it when the user requests that change.

## Choose the relevant workflow

- **Formulas, validation, or analysis:** read [methodology guidance](references/methodology-cheatsheet.md).
- **Proposal, paper, or literature review:** read the same guidance, including its citation checks; match code, config, and decisions rather than dated prose.
- **Data acquisition, VinBus, or OSM:** read [data workflow](references/osm-vinbus-workflow.md).
- **Workspace maintenance:** preserve user changes, data, canonical outputs, and referenced paths. Follow explicit retention/deletion choices; update affected guidance.
- **Explanation or status review:** inspect the relevant files and report evidence. A read-only request does not require downloads, regeneration, or gates.

## Verification and handoff

- Use the project's Python environment and paths appropriate to the current OS. Inspect acquisition scripts for top-level side effects before invoking `--help` or importing them; `scripts/scrape_vinbus.py` performs acquisition at top level. Do not assume legacy Windows commands work on macOS.
- Formula changes require proposal index-construction/validation updates and meaningful tests in the same change. Keep reusable logic in `src/` and command wrappers in `scripts/`.
- After changes, run `python scripts/agent_gate.py`; full tests apply to formula, validation, network, or calibration changes under `AGENTS.md`. Documentation-only work needs no extra full test run beyond checks selected by the gate. Follow `docs/agent_workflow.md` and `config/agent_policy.json` for change review and coordination.
- Gate self-audits write under `.agent/`, preserving published outputs. Read `.agent/change_review.md`, add the purpose, impact and limitations in the user-facing report, then ask for confirmation after each batch. Method/status transitions and missing coupled edits are review notes, not orders to restore the baseline. Genuine calculation, schema, or data errors still require correction. A gate PASS does not certify review, freshness, or user approval.
- Report files changed, checks that passed or could not run, and remaining data blockers. Verify live external claims when needed; report local availability separately from historical acquisition status.

# Agent Workflow

The user's latest direction supersedes historical methods and plans. Prepare requested changes as a draft, run checks, present the change report, and request confirmation after each batch. Do not revert to a historical design to make a checker pass. Do not merge/publish or claim adoption while confirmation is pending.

## Author flow

1. Read `CLAUDE.md`, `docs/data_sources.md`, `docs/decisions.md`, and proposal Sections 7-10 for methodology work.
2. Reserve one-writer ownership in the issue/PR.
3. Create a worktree:

```powershell
git worktree add ..\mcs-routing -b agent/routing development
Copy-Item .agent/ownership.example.json .agent/ownership.json
```

Edit `.agent/ownership.json` with the task, exact branch, owner, and owned files/directories. The local reservation is ignored by Git.

4. Implement only inside owned scope.
5. Check scope and policy:

```powershell
python scripts/check_agent_ownership.py
python scripts/agent_gate.py --dry-run
python scripts/agent_gate.py
```

6. Fill the PR template. Independent reviewer checks; human merges.

## Gate behavior

Policy source: `config/agent_policy.json`.

Gates apply after changes, not to read-only explanations. Self-audits write under `.agent/`, not canonical outputs. The gate generates `.agent/change_review.md`: changed files, Git baseline, analytical configuration before/after, review notes, selected checks and PASS/FAIL. The report stays `PENDING_USER_CONFIRMATION` even on PASS. Present purpose, impacts and data blockers with the report; ask the user to confirm or request revisions. Only the user's explicit reply confirms the batch. Record substantive accepted research decisions in `docs/decisions.md`; read-only explanations need no confirmation.

| Change | Enforcement |
|---|---|
| Any diff | `git diff --check` |
| `src/` or network scripts | full tests |
| proposal/paper/docs | document consistency |
| headline files | consistency + self-audit |
| `src/accessibility.py` | missing proposal/test updates reported for review |
| `src/pilot.py` | missing test updates reported for review |

Useful deterministic checks:

```powershell
python scripts/agent_gate.py --changed-file src/routing.py --dry-run
python scripts/agent_gate.py --changed-file proposal/proposal_v7.md --dry-run
python scripts/agent_gate.py --format json --dry-run
python scripts/agent_gate.py --reason "Explain purpose, expected impact, and limitations of this batch"
```

## Published-output review

Changes to published outputs and `CLAUDE.md` are reported for user confirmation on every branch. No branch-specific method lock or override is required. Legacy override flags remain accepted for command compatibility only. Numeric publication assertions still must match their declared snapshot; for a changed design, update or regenerate the corresponding draft artifacts rather than adjusting new results to old values. Never resolve generated-output conflicts by choosing one side blindly.

## Reviewer flow

Check the requested intent against the working implementation, formula/proposal/test consistency, source provenance, comparable scenario scales, data quality, headline consistency, reproduction commands, and unrelated churn. Historical defaults do not override the new intent. Reviewer does not silently edit the author's branch.

## Integration flow

Merge one approved branch at a time. Regenerate in canonical order documented in `CLAUDE.md`, then run:

```powershell
python scripts/check_document_consistency.py
python scripts/project_self_audit.py
python -m pytest tests/ -v
```

Commit canonical outputs once. CI does not fetch external data or rebuild unavailable raw/interim datasets.

## Recovery and cleanup

Branch conflict: rebase/merge integration branch in the task worktree, rerun gates. Ownership conflict: stop; transfer paths explicitly in issue/PR. Failed checks: fix calculation/data/schema errors; report method transitions and pending confirmation instead of restoring old methods.

```powershell
git worktree remove ..\mcs-routing
git worktree prune
```

## Research tooling

Tool assignments for literature discovery, code execution, and handoff.

| Tool | Role | Excluded from |
|---|---|---|
| **OpenScience** | Literature discovery, synthesis, read-only methodology audit, reviewer simulation | Editing canonical files; running pipeline scripts |
| **Antigravity** | Approved code/document changes, tests, consistency checks, Git | Independent literature search |
| **Zotero** | Canonical PDF, DOI, page-level notes, bibliography | — |
| **Google Scholar / OpenAlex** | Independent citation and metadata verification | — |
| **9router** | Local OpenAI-compatible model endpoint for OpenScience | — |
| **Consensus.app** | Intentionally excluded — substantially overlaps OpenScience literature discovery | — |

OpenScience runs against a disposable clone or separate worktree, not the main repo. Its outputs are advisory: verify citations and repository claims before copying into canonical files. OpenScience and coding agents must not edit the same files concurrently.

Literature review sessions that produce verified DOIs and methodology implications should be recorded as decisions in `docs/decisions.md` (see DEC-029 for example).

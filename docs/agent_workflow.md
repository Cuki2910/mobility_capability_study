# Agent Workflow

Lightweight contract: Git worktrees provide isolation; tracked policy selects checks; humans merge.

## Author flow

1. Read `CLAUDE.md`, `docs/data_sources.md`, `docs/decisions.md`, and proposal Section 3 for methodology work.
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

| Change | Enforcement |
|---|---|
| Any diff | `git diff --check` |
| `src/` or network scripts | full tests |
| proposal/paper/docs | document consistency |
| headline files | consistency + self-audit |
| `src/accessibility.py` | proposal v7 + tests required |
| `src/pilot.py` | tests required |

Useful deterministic checks:

```powershell
python scripts/agent_gate.py --changed-file src/routing.py --dry-run
python scripts/agent_gate.py --changed-file proposal/proposal_v7.md --dry-run
python scripts/agent_gate.py --format json --dry-run
```

## Canonical-output lock

Integration-owned files include `outputs/pilot_summary.csv`, headline snapshot, self-audit, supervisor memo, and current status in `CLAUDE.md`. Feature-branch edits fail the gate.

Emergency/integration regeneration override requires both fields:

```powershell
python scripts/agent_gate.py --allow-canonical-output-changes --reason "approved integration regeneration"
```

Reviewer must inspect the reason. Never resolve generated-output conflicts by choosing one side; regenerate after merge.

## Reviewer flow

Check formula/proposal/test consistency, Network B/C provenance, shared A+B normalization, RAC_time primary, source existence/licensing, headline consistency, reproduction commands, and unrelated churn. Reviewer does not silently edit the author's branch.

## Integration flow

Merge one approved branch at a time. Regenerate in canonical order documented in `CLAUDE.md`, then run:

```powershell
python scripts/check_document_consistency.py
python scripts/project_self_audit.py
python -m pytest tests/ -v
```

Commit canonical outputs once. CI does not fetch external data or rebuild unavailable raw/interim datasets.

## Recovery and cleanup

Branch conflict: rebase/merge integration branch in the task worktree, rerun gates. Ownership conflict: stop; transfer paths explicitly in issue/PR. Failed canonical gate: remove generated changes or move regeneration to integration branch.

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

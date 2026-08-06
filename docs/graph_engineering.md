# Graph Engineering

This repository uses a typed research DAG, not a general graph database. The graph makes objectives, dependencies, artifacts, decisions, evaluations, and runs explicit while Git remains the reversible state mechanism.

## Surfaces

- `config/pipeline.json`: versioned node and artifact contracts.
- `scripts/run_research_pipeline.py`: bounded deterministic executor.
- `outputs/lineage/runs/*.json`: immutable run evidence.
- `outputs/lineage/research_lineage.sqlite`: disposable query index.
- `scripts/query_lineage.py`: artifact/node/decision/run queries.
- `scripts/graph_health.py`: static graph quality report.

## Commands

```powershell
python scripts/run_research_pipeline.py --target core --dry-run --explain
python scripts/run_research_pipeline.py --target publication --offline --dry-run
python scripts/graph_health.py
python scripts/query_lineage.py artifact outputs/headline_metrics.json
```

## Invariants

Every node has an objective, typed argv command, declared inputs/outputs, decisions, resource class, tags, and artifact contracts. Paths are repository-relative. One output has one producer. Cycles and unknown dependencies fail loading. Every real run records Git state, pipeline hash, environment, node status, artifact hashes, and errors.

## Deliberate ceiling

No Neo4j/RDF layer: the current graph is a bounded pipeline DAG, and SQLite answers required provenance queries. No concurrent canonical writers: worktrees parallelize exploration; integration regenerates canonical outputs once. Add a graph DB only when cross-project entity resolution or graph traversal exceeds SQLite/DAG needs.

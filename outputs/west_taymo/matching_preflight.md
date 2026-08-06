# West Tay Mo Matching Preflight

Generated UTC: 2026-07-02T10:13:49.500908+00:00

## Seed Values To Verify

| Variable | Candidate A | Candidate B | Status |
|---|---:|---:|---|
| Tay Mo area km2 | 5.56 | 5.95 | unresolved seed conflict |
| Tay Mo population | 46894 | 46469 | unresolved seed conflict |
| Smart City area ha | 280 |  | seed; verify against boundary area |

## Required Measurements

- OSM drive-network distance from Smart City centroid to Hoan Kiem.
- OSM drive-network distance from Tay Mo core centroid to Hoan Kiem.
- WorldPop total and density distribution by labeled core.
- Planned/organic boundary separability using `scripts/label_site_cells.py`.

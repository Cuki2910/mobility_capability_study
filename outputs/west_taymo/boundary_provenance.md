# West Core Boundary Provenance

Generated UTC: 2026-07-02T10:13:26+00:00

| Boundary | Method | Output | Area km2 | Vertices |
|---|---|---|---:|---:|
| Smart City | OSM Nominatim polygon | `data\raw\west_taymo_smart_city_core_boundary.gpkg` | 2.14 | 124 |
| Tay Mo | OSM-derived local fabric trace | `data\raw\west_taymo_tay_mo_core_boundary.gpkg` | 4.90 | 3446 |

Notes:
- Smart City is imported directly from OSM/Nominatim, same pattern as the Ocean Park boundary.
- Tay Mo uses an OSM administrative boundary if Overpass returns one; otherwise it uses an OSM-derived organic-core trace from named local fabric and building footprints, with Smart City removed.

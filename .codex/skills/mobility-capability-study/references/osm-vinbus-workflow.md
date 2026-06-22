# OSM / VinBus Workflow

## Priority Order

1. Check OSM route relations for VinBus before manual digitization.
2. Confirm GHSL/WorldPop resolution for the Ocean Park pilot bbox.
3. If OSM has no VinBus routes, digitize E01-E09 from vinbus.vn street-name descriptions onto the OSM road network.
4. Re-check Hanoi GTFS currency; 2020 feed is likely stale.

## Overpass Target

Core query pattern:

```overpass
[out:json][timeout:180];
(
  relation[route=bus][operator~VinBus,i](south,west,north,east);
  relation[route=bus][name~^E0[1-9],i](south,west,north,east);
  relation[route=bus][ref~^E0[1-9],i](south,west,north,east);
);
out tags geom;
```

Use a Hanoi-wide bbox first to avoid missing relations that extend outside Ocean Park.

Suggested starting bbox: `20.85 105.75 21.15 106.05` (`south west north east`).

## Interpretation

- If relations exist and geometry is complete: use them for Network C route geometry, then document relation IDs in `docs/data_sources.md`.
- If partial relations exist: compare route names/refs against VinBus E01-E09 and document missing pieces.
- If empty: proceed to manual digitization, but save query output/log in `data/raw/` or `docs/data_sources.md` notes.

## Data Hygiene

- Keep raw downloads immutable in `data/raw/`.
- Put cleaned/aligned route/network artifacts in `data/interim/`.
- Put analysis-ready grid metrics in `data/processed/`.
- Do not hand-edit raw OSM/GTFS files.

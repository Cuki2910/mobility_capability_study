# GTFS Catalog Check

Checked on 2026-06-23.

## Sources Checked

| Source | Query / URL | Result | Interpretation |
|---|---|---|---|
| MobilityDatabase | `scripts/check_mobility_database.py --query Hanoi` | 0 Hanoi hits in `data/interim/mobility_database_hanoi_candidates.csv` | No maintained MobilityDatabase candidate found. |
| TUMI Datahub | `https://hub.tumidata.org/dataset/?page=3&res_format=GTFS` | Lists `GTFS: Hanoi, Morning`, `GTFS: Hanoi, Afternoon`, and `GTFS: Hanoi, Midday` | TUMI has Hanoi GTFS candidates. |
| TUMI Datahub | `https://hub.tumidata.org/dataset/gtfs-hanoi-morning` | `GTFS: Hanoi, Morning`, created 2024-01-22, last updated 2024-05-23, license not specified; source points to World Bank Hanoi GTFS dataset | Candidate for current-service or time-of-day sensitivity, but license/source vintage must be checked before use. |
| TUMI Datahub | `https://hub.tumidata.org/dataset/gtfs-hanoi` | `GTFS: Hanoi, Midday`, created 2024-01-22, last updated 2024-06-04, license not specified; warns license info may be outdated | Candidate for current-service or time-of-day sensitivity, but not a clean replacement for the pre-VinBus baseline. |

## Conclusion

Do not replace the 2018 World Bank feed as Network B primary baseline in this pilot. The 2018 feed remains methodologically useful as a pre-VinBus conventional-transit baseline. TUMI Hanoi Morning/Midday/Afternoon feeds should be downloaded and checked in a separate sensitivity pass if the paper needs a post-2021/current-service comparison.

## Required Follow-Up Before Using TUMI Feeds

- Download each TUMI Hanoi feed and run `scripts/check_hanoi_gtfs.py`.
- Confirm service dates, route count, stop count, and whether VinBus routes are included.
- Confirm license/terms from the original World Bank source before redistribution.
- If usable, run alongside the 2018 baseline as a current-service sensitivity, not as a replacement for Scenario A.

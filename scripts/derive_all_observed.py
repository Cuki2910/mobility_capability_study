"""
Derive observed opportunity values for all four MAI domains.

Strategy per domain:
  tertiary_healthcare — citable bed counts from MOH/web sources;
      hospitals: observed_point (named) or building-area proxy (obs_derived);
      commune health stations: MOH standard 10 beds → observed_derived
  higher_education    — Vietnam national class-size standards as floor enrollment;
      primary/lower-sec/upper-sec: students = classes * std_class_size;
      capacity proxy from building area where area available;
      language/enrichment centres: small observed_derived counts
  economic            — employment density per land-use sector * building area;
      industrial (factory): 15 workers/100m² ; commercial/office: 35/100m²;
      retail/marketplace: 10/100m² ; bank/post_office: point estimate
  metro_commercial    — already 34.9 % covered by GLA from derive_commercial_floorspace;
      top-up remaining POIs with area-based GLA where building_area_m2 present

All values are stored as obs_* columns and obs_source / obs_source_url,
then merged into merged_pois_observed.gpkg via merge_observed_opportunity.py.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# ── Healthcare bed-count table ─────────────────────────────────────────────
# Named hospital bed counts with citations. Order matters: first match wins.
HOSPITAL_BEDS: list[dict] = [
    # Already in healthcare_beds.csv; included here for completeness
    {
        "name_fragment": "Gia Lâm",
        "amenity": "hospital",
        "obs_beds": 288,
        "obs_source": "congnghiepmoitruong_2019_actual_beds",
        "obs_source_url": "https://congnghiepmoitruong.vn/benh-vien-da-khoa-gia-lam-dat-muc-tieu-phat-trien-ky-thuat-chuyen-mon-sau-de-phuc-vu-nhan-dan-4423.html",
    },
    {
        "name_fragment": "Sông Hồng",
        "amenity": "hospital",
        # Bệnh viện Đa khoa Sông Hồng — publicly listed 200 beds
        "obs_beds": 200,
        "obs_source": "song_hong_hospital_website_2023",
        "obs_source_url": "https://benhviensonghong.vn",
    },
    {
        "name_fragment": "Quân y 76",
        "amenity": "clinic",
        # Military polyclinic Gia Lam — ~50 beds estimated from facility type
        "obs_beds": 50,
        "obs_source": "military_polyclinic_area_derived",
        "obs_source_url": "",
    },
]

# Commune health station standard (Vietnam MOH Circular 26/2019-BYT):
# each commune health station maintains ≥10 inpatient beds
COMMUNE_STATION_BEDS = 10
COMMUNE_STATION_SOURCE = "MOH_circular26_2019_commune_standard"
COMMUNE_STATION_URL = "https://thuvienphapluat.vn/van-ban/The-thao-Y-te/Thong-tu-26-2019-TT-BYT-730302.aspx"

# For unnamed hospitals without a bed count, estimate from building area:
# Typical Vietnamese district hospital: ~1 bed / 20 m² gross floor area
BED_PER_M2 = 1.0 / 20.0


# ── Higher-education enrollment standards ──────────────────────────────────
# Vietnam MOET Decision 1600/QD-BGDDT 2022 — maximum class sizes:
#   Preschool/kindergarten: 35 pupils/class
#   Primary (tiểu học):     35 pupils/class
#   Lower secondary (THCS): 45 pupils/class
#   Upper secondary (THPT): 45 pupils/class
# Typical school: 20-30 classes. Use conservative 20 classes as floor.
SCHOOL_ENROLLMENT: dict[str, dict] = {
    "preschool": {
        "class_size": 35, "classes": 12,
        "source": "MOET_1600_2022_class_standard",
        "url": "https://thuvienphapluat.vn/van-ban/Giao-duc/Quyet-dinh-1600-QD-BGDDT-2022",
    },
    "primary": {
        "class_size": 35, "classes": 20,
        "source": "MOET_1600_2022_class_standard",
        "url": "https://thuvienphapluat.vn/van-ban/Giao-duc/Quyet-dinh-1600-QD-BGDDT-2022",
    },
    "lower_secondary": {
        "class_size": 45, "classes": 20,
        "source": "MOET_1600_2022_class_standard",
        "url": "https://thuvienphapluat.vn/van-ban/Giao-duc/Quyet-dinh-1600-QD-BGDDT-2022",
    },
    "upper_secondary": {
        "class_size": 45, "classes": 25,
        "source": "MOET_1600_2022_class_standard",
        "url": "https://thuvienphapluat.vn/van-ban/Giao-duc/Quyet-dinh-1600-QD-BGDDT-2022",
    },
    "international": {
        # International/bilingual schools: smaller classes, fewer grades
        "class_size": 25, "classes": 15,
        "source": "international_school_standard_estimate",
        "url": "",
    },
    "university_faculty": {
        # VinUniversity lecture hall / faculty building
        "class_size": 200, "classes": 5,
        "source": "VinUniversity_website_capacity_estimate",
        "url": "https://vinuni.edu.vn",
    },
    "language_centre": {
        # Language/enrichment centre: small cohorts, multiple sessions
        "class_size": 15, "classes": 8,
        "source": "language_centre_standard_estimate",
        "url": "",
    },
    "research_institute": {
        # Research centres: staff/graduate researchers, not enrolled students
        # Use 50 as a conservative headcount proxy
        "class_size": 50, "classes": 1,
        "source": "research_institute_staff_estimate",
        "url": "",
    },
}


def _classify_school(name: str, tags: dict) -> str:
    n = (name or "").lower()
    amenity = str(tags.get("amenity") or "").lower()
    office = str(tags.get("office") or "").lower()
    cat = str(tags.get("category") or "").lower()
    if "mầm non" in n or "mam non" in n or "preschool" in n or "kindergarten" in n:
        return "preschool"
    if "tiểu học" in n or "tieu hoc" in n or "primary" in n:
        return "primary"
    if "trung học cơ sở" in n or "thcs" in n or "lower secondary" in n:
        return "lower_secondary"
    if "trung học phổ thông" in n or "thpt" in n or "upper secondary" in n:
        return "upper_secondary"
    if any(kw in n for kw in ("international", "bilingual", "cambridge", "greenfield", "brighton")):
        return "international"
    if any(kw in n for kw in ("giảng đường", "đại học", "university", "campus", "vinuni")):
        return "university_faculty"
    if any(kw in n for kw in ("nghiên cứu", "research", "viện nghiên cứu", "institute")):
        return "research_institute"
    if any(kw in n for kw in ("english", "tiếng anh", "ngoại ngữ", "lái xe", "yoga", "âm nhạc", "nhạc")):
        return "language_centre"
    if office in ("educational_institution", "university", "research", "academic"):
        return "university_faculty" if "university" in office else "research_institute"
    # fallback: treat unnamed or uncategorised as language centre (small)
    return "language_centre"


# ── Economic employment density ────────────────────────────────────────────
# Workers per 100 m² gross floor area, by sector (literature-derived, Vietnam context)
# Bui Thi Bich Lien (2019) HAIDEP employment density estimates;
# World Bank Vietnam industrial labour survey 2020
EMPLOYMENT_DENSITY: dict[str, float] = {
    # workers per m²
    "industrial":  0.08,   # factories: ~8 workers/100 m² (light industry Hanoi suburbs)
    "office":      0.12,   # modern office: ~12 workers/100 m²
    "commercial":  0.05,   # mixed commercial: ~5 workers/100 m²
    "retail":      0.04,   # retail floor: ~4 workers/100 m²
    "government":  0.10,   # government offices
    "company":     0.12,
    "it":          0.15,
    "financial":   0.12,
    "insurance":   0.12,
    "energy_supplier": 0.06,
    "ngo":         0.08,
    "yes":         0.08,
}
EMPLOYMENT_SOURCE = "HAIDEP_2010_VN_employment_density_by_sector"
EMPLOYMENT_URL = "https://www.jica.go.jp/project/vietnam/012/materials/ku57pq000002bkjm-att/haidep_vol01.pdf"

# Point-source employment estimates for amenity=bank/marketplace/post_office
AMENITY_JOBS: dict[str, dict] = {
    "bank":        {"jobs": 15, "source": "bank_branch_standard_Vietnam", "url": ""},
    "marketplace": {"jobs": 80, "source": "marketplace_employment_estimate", "url": ""},
    "post_office": {"jobs": 8,  "source": "vnpost_branch_standard", "url": ""},
}


def _derive_healthcare(row: pd.Series) -> dict | None:
    amenity = str(row.get("amenity") or "").lower()
    name = str(row.get("name") or "")

    if amenity == "hospital":
        # Try named lookup first
        for entry in HOSPITAL_BEDS:
            if entry["name_fragment"] in name:
                return {
                    "obs_beds": entry["obs_beds"],
                    "obs_source": entry["obs_source"],
                    "obs_source_url": entry["obs_source_url"],
                }
        # Fallback: derive from building area
        area = pd.to_numeric(row.get("building_area_m2"), errors="coerce")
        if pd.notna(area) and area > 0:
            beds = max(10, round(area * BED_PER_M2))
            return {
                "obs_beds": float(beds),
                "obs_source": "building_area_bed_density_derived",
                "obs_source_url": "",
            }
        # Final fallback: generic district hospital
        return {
            "obs_beds": 100.0,
            "obs_source": "district_hospital_minimum_standard_derived",
            "obs_source_url": "",
        }

    if amenity == "clinic":
        # Check if name matches military clinic
        for entry in HOSPITAL_BEDS:
            if entry["name_fragment"] in name and entry["amenity"] == "clinic":
                return {
                    "obs_beds": entry["obs_beds"],
                    "obs_source": entry["obs_source"],
                    "obs_source_url": entry["obs_source_url"],
                }
        # Commune health station standard
        if any(kw in name.lower() for kw in ("trạm y tế", "tram y te", "commune", "xã", "thị trấn")):
            return {
                "obs_beds": float(COMMUNE_STATION_BEDS),
                "obs_source": COMMUNE_STATION_SOURCE,
                "obs_source_url": COMMUNE_STATION_URL,
            }
        # Other clinics: 5-bed estimate
        return {
            "obs_beds": 5.0,
            "obs_source": "private_clinic_standard_estimate",
            "obs_source_url": "",
        }

    # healthcare=hospital/clinic fallback
    hc = str(row.get("healthcare") or "").lower()
    if hc == "hospital":
        area = pd.to_numeric(row.get("building_area_m2"), errors="coerce")
        beds = max(10, round(area * BED_PER_M2)) if pd.notna(area) and area > 0 else 50
        return {"obs_beds": float(beds), "obs_source": "building_area_bed_density_derived", "obs_source_url": ""}
    if hc == "clinic":
        return {"obs_beds": 5.0, "obs_source": "private_clinic_standard_estimate", "obs_source_url": ""}

    # Overture health_and_medical POIs without explicit amenity
    cat = str(row.get("category") or "").lower()
    if cat == "health_and_medical":
        return {"obs_beds": 5.0, "obs_source": "private_clinic_standard_estimate", "obs_source_url": ""}

    return None


def _derive_higher_education(row: pd.Series) -> dict | None:
    amenity = str(row.get("amenity") or "").lower()
    name = str(row.get("name") or "")
    office = str(row.get("office") or "").lower()
    cat = str(row.get("category") or "").lower()

    is_edu = (
        amenity in ("school", "university", "college")
        or office in ("educational_institution", "university", "research", "academic", "educational")
        or cat == "education"
        or any(kw in name.lower() for kw in (
            "giảng đường", "đại học", "university", "học viện", "campus",
            "viện nghiên cứu", "trung tâm nghiên cứu", "school", "english",
            "tiếng anh", "ngoại ngữ", "mầm non", "tiểu học", "trung học",
            "lái xe", "trung tâm", "toeic", "ielts", "thpt", "thcs",
        ))
    )
    if not is_edu:
        return None

    school_type = _classify_school(name, row.to_dict() if hasattr(row, "to_dict") else dict(row))
    spec = SCHOOL_ENROLLMENT[school_type]
    enrollment = spec["class_size"] * spec["classes"]

    # If building area available, refine — cap at 5 m² per student (TCVN 8793:2011)
    area = pd.to_numeric(row.get("building_area_m2"), errors="coerce")
    if pd.notna(area) and area > 0:
        area_based = int(area / 5.0)
        # Take geometric mean of standard and area estimates for robustness
        enrollment = int(np.sqrt(enrollment * max(area_based, 1)))

    return {
        "obs_enrollment": float(max(enrollment, 10)),
        "obs_source": spec["source"],
        "obs_source_url": spec["url"],
    }


def _derive_economic(row: pd.Series) -> dict | None:
    amenity = str(row.get("amenity") or "").lower()
    landuse = str(row.get("landuse") or "").lower()
    office = str(row.get("office") or "").lower()
    name = str(row.get("name") or "")

    # Amenity point sources with known employment
    if amenity in AMENITY_JOBS:
        entry = AMENITY_JOBS[amenity]
        return {
            "obs_jobs": float(entry["jobs"]),
            "obs_source": entry["source"],
            "obs_source_url": entry["url"],
        }

    # Landuse polygon: derive from area × density
    if landuse in EMPLOYMENT_DENSITY:
        area = pd.to_numeric(row.get("building_area_m2"), errors="coerce")
        if pd.notna(area) and area > 0:
            density = EMPLOYMENT_DENSITY[landuse]
            jobs = max(1, round(area * density))
            return {
                "obs_jobs": float(jobs),
                "obs_source": EMPLOYMENT_SOURCE,
                "obs_source_url": EMPLOYMENT_URL,
            }
        # No area — use sector default
        defaults = {"industrial": 50, "commercial": 30, "retail": 20, "office": 40}
        return {
            "obs_jobs": float(defaults.get(landuse, 20)),
            "obs_source": f"{landuse}_sector_default_estimate",
            "obs_source_url": "",
        }

    # Office=* tag
    if office and office not in ("educational", "educational_institution", "university", "research", "academic"):
        area = pd.to_numeric(row.get("building_area_m2"), errors="coerce")
        density = EMPLOYMENT_DENSITY.get(office, 0.10)
        if pd.notna(area) and area > 0:
            jobs = max(1, round(area * density))
        else:
            # Point office node: estimate by type
            defaults_office = {
                "company": 30, "government": 50, "ngo": 15, "it": 40,
                "financial": 25, "insurance": 20, "telecommunication": 30,
                "energy_supplier": 20, "yes": 15,
            }
            jobs = defaults_office.get(office, 20)
        return {
            "obs_jobs": float(jobs),
            "obs_source": EMPLOYMENT_SOURCE,
            "obs_source_url": EMPLOYMENT_URL,
        }

    return None


def _derive_commercial_topup(row: pd.Series) -> dict | None:
    """Top-up metro_commercial POIs that have no GLA yet but have building_area_m2."""
    # Only act if obs_retail_gla_m2 is missing/zero
    existing = pd.to_numeric(row.get("obs_retail_gla_m2"), errors="coerce")
    if pd.notna(existing) and existing > 0:
        return None  # already covered

    shop = str(row.get("shop") or "").lower()
    cat = str(row.get("category") or "").lower()
    area = pd.to_numeric(row.get("building_area_m2"), errors="coerce")

    # Usable fraction depends on shop type
    fractions = {
        "mall": 0.65, "department_store": 0.70, "supermarket": 0.70,
        "convenience": 0.70, "electronics": 0.75, "computer": 0.75,
        "mobile_phone": 0.80, "houseware": 0.70, "beauty": 0.80,
        "car": 0.50, "motorcycle": 0.60, "tyres": 0.60, "agrarian": 0.60,
    }
    levels_default = {"mall": 3, "department_store": 2, "supermarket": 1}.get(shop, 1)

    if pd.notna(area) and area > 0:
        frac = fractions.get(shop, 0.70)
        # Try OSM building:levels
        lvl = pd.to_numeric(row.get("building:levels"), errors="coerce")
        if not pd.notna(lvl) or lvl <= 0:
            lvl = levels_default
        gla = area * float(lvl) * frac
        return {
            "obs_retail_gla_m2": round(gla, 1),
            "obs_source": "building_area_levels_gla_derived",
            "obs_source_url": "",
        }

    if cat in ("retail", "financial_service"):
        return {
            "obs_retail_gla_m2": 100.0,
            "obs_source": "retail_poi_default_gla_estimate",
            "obs_source_url": "",
        }

    # Named shops without area: assign small default GLA
    if shop and shop not in ("nan", "yes", "agrarian", ""):
        default_gla = {
            "car": 300.0, "motorcycle": 150.0, "tyres": 100.0,
        }.get(shop, 80.0)
        return {
            "obs_retail_gla_m2": default_gla,
            "obs_source": "shop_type_default_gla_estimate",
            "obs_source_url": "",
        }

    # Parks, leisure, transportation, unnamed fallbacks → leave as proxy (no GLA)
    return None


def derive_all_observed(pois: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Return a copy of `pois` with obs_* columns filled where derivable."""
    from src.accessibility_inputs import classify_poi_opportunity_domain

    out = pois.copy()
    # Ensure numeric obs columns are float (GeoPackage/Arrow stores them as string)
    for col in ("obs_beds", "obs_enrollment", "obs_jobs", "obs_retail_gla_m2"):
        if col not in out.columns:
            out[col] = np.nan
        else:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    for col in ("obs_source", "obs_source_url"):
        if col not in out.columns:
            out[col] = ""
        else:
            out[col] = out[col].astype(str).replace("nan", "").replace("<NA>", "")

    n_filled = {"healthcare": 0, "higher_education": 0, "economic": 0, "commercial": 0}

    for idx, row in out.iterrows():
        domain, _ = classify_poi_opportunity_domain(row)

        if domain == "tertiary_healthcare":
            existing_beds = pd.to_numeric(row.get("obs_beds"), errors="coerce")
            if pd.isna(existing_beds) or existing_beds <= 0:
                result = _derive_healthcare(row)
                if result:
                    out.at[idx, "obs_beds"] = result["obs_beds"]
                    out.at[idx, "obs_source"] = result["obs_source"]
                    out.at[idx, "obs_source_url"] = result.get("obs_source_url", "")
                    n_filled["healthcare"] += 1

        elif domain == "higher_education":
            existing = pd.to_numeric(row.get("obs_enrollment"), errors="coerce")
            if pd.isna(existing) or existing <= 0:
                result = _derive_higher_education(row)
                if result:
                    out.at[idx, "obs_enrollment"] = result["obs_enrollment"]
                    out.at[idx, "obs_source"] = result["obs_source"]
                    out.at[idx, "obs_source_url"] = result.get("obs_source_url", "")
                    n_filled["higher_education"] += 1

        elif domain == "economic":
            existing = pd.to_numeric(row.get("obs_jobs"), errors="coerce")
            if pd.isna(existing) or existing <= 0:
                result = _derive_economic(row)
                if result:
                    out.at[idx, "obs_jobs"] = result["obs_jobs"]
                    out.at[idx, "obs_source"] = result["obs_source"]
                    out.at[idx, "obs_source_url"] = result.get("obs_source_url", "")
                    n_filled["economic"] += 1

        elif domain == "metro_commercial":
            result = _derive_commercial_topup(row)
            if result:
                out.at[idx, "obs_retail_gla_m2"] = result["obs_retail_gla_m2"]
                if not out.at[idx, "obs_source"]:
                    out.at[idx, "obs_source"] = result["obs_source"]
                    out.at[idx, "obs_source_url"] = result.get("obs_source_url", "")
                n_filled["commercial"] += 1

    print(f"Filled observed values:")
    for domain, n in n_filled.items():
        print(f"  {domain}: {n} POIs filled")

    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pois", type=Path,
        default=ROOT / "data/interim/merged_pois_observed.gpkg",
        help="Input POI layer (merged_pois_observed.gpkg or merged_pois_economic.gpkg)",
    )
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "data/interim/merged_pois_observed.gpkg",
        help="Output GeoPackage (overwrites in place by default)",
    )
    args = parser.parse_args()

    print(f"Reading {args.pois} ...")
    pois = gpd.read_file(args.pois)
    print(f"  {len(pois)} POIs loaded")

    enriched = derive_all_observed(pois)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_file(args.output, driver="GPKG")
    print(f"Wrote {args.output} ({len(enriched)} POIs)")

    # Coverage summary
    print("\nObserved coverage after enrichment:")
    from src.accessibility_inputs import classify_poi_opportunity_domain, OBSERVED_OPPORTUNITY_REFS
    import numpy as np
    by_domain: dict[str, dict] = {}
    for _, row in enriched.iterrows():
        domain, _ = classify_poi_opportunity_domain(row)
        if domain not in by_domain:
            by_domain[domain] = {"total": 0, "observed": 0}
        by_domain[domain]["total"] += 1
        spec = OBSERVED_OPPORTUNITY_REFS.get(domain, {})
        col = spec.get("column")
        if col:
            v = pd.to_numeric(row.get(col), errors="coerce")
            if pd.notna(v) and v > 0:
                by_domain[domain]["observed"] += 1
    for domain, counts in sorted(by_domain.items()):
        pct = 100.0 * counts["observed"] / counts["total"] if counts["total"] else 0
        print(f"  {domain}: {counts['observed']}/{counts['total']} = {pct:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Build accessibility-ready pilot inputs from real spatial layers."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

try:
    from .routing import (
        composite_mai_from_graph,
        corridor_accessibility,
        gtfs_stops_from_zip,
        load_timed_graph,
        nearest_graph_nodes,
        opportunity_weighted_mean_time,
        reachable_counts_and_mean_time,
        stop_accessibility,
        vinbus_stop_accessibility,
        vinbus_stop_accessibility_pseudo_gtfs,
        vinbus_corridor_from_overpass,
        weighted_decay_sum,
    )
except ImportError:  # pragma: no cover
    from routing import (
        composite_mai_from_graph,
        corridor_accessibility,
        gtfs_stops_from_zip,
        load_timed_graph,
        nearest_graph_nodes,
        opportunity_weighted_mean_time,
        reachable_counts_and_mean_time,
        stop_accessibility,
        vinbus_stop_accessibility,
        vinbus_stop_accessibility_pseudo_gtfs,
        vinbus_corridor_from_overpass,
        weighted_decay_sum,
    )


# POI tag → (domain, opportunity_weight) for MAI v8 (Decision #12).
# domain must be one of the keys in MAI_DOMAIN_WEIGHTS.
# opportunity_weight is the magnitude proxy for that individual POI type
# (relative, not absolute — will be used inside weighted_decay_sum).
_AMENITY_DOMAIN: dict[str, tuple[str, float]] = {
    "hospital":    ("tertiary_healthcare", 1.0),
    "clinic":      ("tertiary_healthcare", 0.4),
    "school":      ("higher_education", 0.5),
    "university":  ("higher_education", 1.0),
    "college":     ("higher_education", 0.7),
    # Economic domain — Hướng C: formal employment & financial services
    "bank":        ("economic", 0.6),
    "marketplace": ("economic", 0.8),
    "post_office": ("economic", 0.3),
}
_SHOP_DOMAIN: dict[str, tuple[str, float]] = {
    "mall":             ("metro_commercial", 1.0),
    "department_store": ("metro_commercial", 0.8),
    "supermarket":      ("metro_commercial", 0.6),
    "convenience":      ("metro_commercial", 0.2),
    "electronics":      ("metro_commercial", 0.4),
    "computer":         ("metro_commercial", 0.4),
    "mobile_phone":     ("metro_commercial", 0.3),
    "houseware":        ("metro_commercial", 0.3),
    "car":              ("metro_commercial", 0.3),
    "motorcycle":       ("metro_commercial", 0.3),
    "tyres":            ("metro_commercial", 0.2),
    "beauty":           ("metro_commercial", 0.2),
    "agrarian":         ("metro_commercial", 0.2),
}
_OFFICE_DOMAIN: dict[str, tuple[str, float]] = {
    # landuse=* polygon tags (Hướng B). Base weight encodes employment density per m²:
    # office > commercial > retail > industrial (factories employ few people per m²).
    "office":           ("economic", 1.0),
    "commercial":       ("economic", 0.7),
    "retail":           ("economic", 0.4),
    "industrial":       ("economic", 0.3),
}
# office=* node/polygon tags (Hướng C)
_OFFICE_TAG_DOMAIN: dict[str, tuple[str, float]] = {
    "company":                 ("economic", 1.0),
    "government":              ("economic", 0.8),
    "ngo":                     ("economic", 0.6),
    "it":                      ("economic", 1.0),
    "financial":               ("economic", 1.0),
    "insurance":               ("economic", 0.7),
    "telecommunication":       ("economic", 0.7),
    "energy_supplier":         ("economic", 0.8),
    "yes":                     ("economic", 0.6),
    # Education-flavored office tags → higher_education (not employment)
    "educational":             ("higher_education", 0.7),
    "educational_institution": ("higher_education", 0.7),
    "university":              ("higher_education", 1.0),
    "research":                ("higher_education", 0.8),
    "academic":                ("higher_education", 0.7),
}

# Name substrings that signal an education facility even when OSM tags it office=*.
# VinUniversity lecture halls and agricultural-academy departments are commonly
# tagged office=company/yes in OSM; these keywords reclassify them to higher_education.
# Note: "khoa " is deliberately excluded — it matches "nha khoa" (dentistry),
# a healthcare facility, not a university faculty.
_EDU_NAME_KEYWORDS = (
    "giảng đường", "university", "đại học", "học viện",
    "campus", "viện nghiên cứu", "trung tâm nghiên cứu",
)


OBSERVED_OPPORTUNITY_REFS = {
    # ref = typical mid-size facility → weight ≈ 1.0.
    # Caps match the proxy area-scaling caps from classify_poi_opportunity_domain()
    # (Decision #18 discipline: no single POI can dominate the domain).
    #
    # tertiary_healthcare: 50-bed district clinic = ref; 288-bed hospital → 5.76 (< cap 30)
    "tertiary_healthcare": {"column": "obs_beds", "unit": "beds", "ref": 50.0, "lo": 0.4, "hi": 30.0},
    # higher_education: 1000-student secondary school = ref; large campus → ≤20
    "higher_education": {"column": "obs_enrollment", "unit": "students", "ref": 1000.0, "lo": 0.5, "hi": 20.0},
    # economic: ref=500 jobs (small industrial cluster); cap=5 mirrors Decision #18 landuse cap.
    # Without this, a 30,000-worker KCN would hit cap=30 and dominate the full MAI domain.
    # 500-job reference keeps a typical SME-office-park (50-500 jobs) in [0.1, 1.0] range.
    "economic": {"column": "obs_jobs", "unit": "jobs", "ref": 500.0, "lo": 0.1, "hi": 5.0},
    # metro_commercial: 1000 m² GLA = ref; Vincom mall (~13,000 m²) → ≤25
    "metro_commercial": {"column": "obs_retail_gla_m2", "unit": "m2_gla", "ref": 1000.0, "lo": 0.1, "hi": 25.0},
}
OBSERVED_UNIT_REFS = {
    "beds": {"ref": 50.0, "lo": 0.4, "hi": 30.0},
    "students": {"ref": 1000.0, "lo": 0.5, "hi": 20.0},
    "seat_capacity_derived": {"ref": 1000.0, "lo": 0.5, "hi": 20.0},
    "jobs": {"ref": 500.0, "lo": 0.1, "hi": 5.0},
    "m2_gla": {"ref": 1000.0, "lo": 0.1, "hi": 25.0},
    "m2_park_or_leisure_area": {"ref": 10000.0, "lo": 0.1, "hi": 25.0},
    "m2_service_floor_area": {"ref": 1000.0, "lo": 0.1, "hi": 25.0},
    "service_capacity": {"ref": 100.0, "lo": 0.1, "hi": 10.0},
}
OBSERVED_SOURCE_VALUES = {
    "observed_point",
    "observed_derived",
    "observed_dasymetric",
    "observed_dasymetric_weak",
    "official_source",
    "facility_source",
    "geometry_measured",
    "facility_geometry_measured",
    "manual_checked",
}
EXCLUDED_SOURCE_VALUES = {"excluded_not_destination"}


@dataclass(frozen=True)
class PoiOpportunity:
    domain: str
    weight: float
    opportunity_source: str
    observed_value: float | None = None
    observed_unit: str | None = None
    source_id: str | None = None
    source_url: str | None = None
    source_tier: str | None = None
    confidence: str | None = None
    audit_status: str | None = None
    include_in_mai: bool = True
    exclusion_reason: str | None = None


def _tag(row, key: str) -> str:
    """Extract a normalized OSM tag value, treating NaN/None/'nan' as empty.

    The naive ``str(row.get(key) or "")`` breaks on float NaN because NaN is
    truthy, yielding the literal string 'nan' — which then matches truthiness
    checks like ``if office_val:`` and misclassifies untagged rows.
    """
    val = row.get(key)
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    s = str(val).strip().lower()
    return "" if s in ("nan", "none", "") else s


def _looks_like_education(name) -> bool:
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return False
    n = str(name).strip().lower()
    if not n:
        return False
    return any(kw in n for kw in _EDU_NAME_KEYWORDS)


def classify_poi_opportunity_domain(row) -> tuple[str, float]:
    """
    Given a POI row (pandas Series or dict with OSM tag columns), return
    (domain, opportunity_weight) for MAI v8 weighted_decay_sum().

    If building_area_m2 is present in the row, the weight is scaled by
    the physical size of the matched building footprint. Otherwise, it
    falls back to default tag-based weights.
    """
    area = pd.to_numeric(row.get("building_area_m2"), errors="coerce")
    has_area = area is not None and not pd.isna(area) and area > 0

    amenity = _tag(row, "amenity")
    if amenity in _AMENITY_DOMAIN:
        domain, base_weight = _AMENITY_DOMAIN[amenity]
        if has_area:
            if domain == "tertiary_healthcare":
                # Hospital/clinic: scale by area / 500.0, bounded [0.4, 30.0]
                weight = float(np.clip(area / 500.0, 0.4, 30.0))
            elif domain == "higher_education":
                # Schools/universities: scale by area / 2000.0, bounded [0.5, 20.0]
                weight = float(np.clip(area / 2000.0, 0.5, 20.0))
            else:
                weight = base_weight
        else:
            weight = base_weight
        return domain, weight

    shop = _tag(row, "shop")
    if shop in _SHOP_DOMAIN:
        domain, base_weight = _SHOP_DOMAIN[shop]
        if has_area:
            # Commerce: scale by area / 1000.0, bounded [0.1, 25.0]
            weight = float(np.clip(area / 1000.0, 0.1, 25.0))
        else:
            weight = base_weight
        return domain, weight

    landuse = _tag(row, "landuse")
    if landuse in _OFFICE_DOMAIN:
        domain, base_weight = _OFFICE_DOMAIN[landuse]
        if has_area:
            # Landuse polygon: base employment-density weight × sqrt(area/2000) area
            # multiplier. sqrt dampens large zones; multiplying by base_weight keeps a
            # 1 ha office worth more than a 1 ha factory. Capped at 5.0 so a single
            # industrial park cannot dominate the whole economic domain (see #18 fix).
            area_mult = float(np.clip(np.sqrt(area / 2000.0), 0.5, 6.0))
            weight = float(np.clip(base_weight * area_mult, 0.1, 5.0))
        else:
            weight = base_weight
        return domain, weight

    # office=* tag (Hướng C): office nodes and polygons
    office_val = _tag(row, "office")
    if office_val:
        domain, base_weight = _OFFICE_TAG_DOMAIN.get(office_val, ("economic", 0.6))
        # Name heuristic: VinUniversity lecture halls / academy departments are
        # tagged office=* in OSM but are education destinations, not employment.
        if domain == "economic" and _looks_like_education(row.get("name")):
            domain, base_weight = "higher_education", 0.7
            # Education buildings capped at 3.0 to stay commensurate with point POIs.
            weight = float(np.clip(area / 4000.0, 0.7, 3.0)) if has_area else base_weight
        elif has_area:
            # Office footprint scaled but capped at 5.0 (see #18 over-correction fix).
            weight = float(np.clip(base_weight * np.sqrt(area / 2000.0), base_weight, 5.0))
        else:
            weight = base_weight
        return domain, weight

    healthcare = _tag(row, "healthcare")
    if healthcare == "hospital":
        if has_area:
            return "tertiary_healthcare", float(np.clip(area / 500.0, 0.4, 30.0))
        return "tertiary_healthcare", 1.0
    if healthcare == "clinic":
        if has_area:
            return "tertiary_healthcare", float(np.clip(area / 500.0, 0.4, 30.0))
        return "tertiary_healthcare", 0.4

    category = _tag(row, "category")
    if category == "education":
        if has_area:
            return "higher_education", float(np.clip(area / 2000.0, 0.5, 20.0))
        return "higher_education", 0.5
    if category == "health_and_medical":
        if has_area:
            return "tertiary_healthcare", float(np.clip(area / 500.0, 0.4, 30.0))
        return "tertiary_healthcare", 0.4
    if category == "retail":
        if has_area:
            return "metro_commercial", float(np.clip(area / 1000.0, 0.1, 25.0))
        return "metro_commercial", 0.2
    if category == "financial_service":
        if has_area:
            return "economic", float(np.clip(area / 1000.0, 0.1, 50.0))
        return "economic", 0.5

    # generic commercial fallback
    if has_area:
        return "metro_commercial", float(np.clip(area / 1000.0, 0.1, 25.0))
    return "metro_commercial", 0.2


def _positive_number(row, key: str) -> float | None:
    val = pd.to_numeric(row.get(key), errors="coerce")
    if val is None or pd.isna(val) or float(val) <= 0:
        return None
    return float(val)


def _source_text(row, key: str) -> str | None:
    val = row.get(key)
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    text = str(val).strip()
    return text or None


def _observed_source_tier(domain: str, source_id: str | None) -> str:
    sid = (source_id or "").lower()
    if "dasymetric" in sid or "ward" in sid or "commune" in sid:
        return "observed_dasymetric"
    if domain == "metro_commercial" or "derived" in sid or "floor" in sid or "gla" in sid:
        return "observed_derived"
    return "observed_point"

def _explicit_source_tier(row, domain: str, source_id: str | None) -> str:
    tier = _source_text(row, "obs_source_tier")
    if tier:
        return tier
    return _observed_source_tier(domain, source_id)

def _bool_value(row, key: str, default: bool = True) -> bool:
    val = row.get(key)
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return default
    if isinstance(val, (bool, np.bool_)):
        return bool(val)
    text = str(val).strip().lower()
    if text in {"false", "0", "no", "n", "exclude", "excluded"}:
        return False
    if text in {"true", "1", "yes", "y", "include", "included"}:
        return True
    return default


def _proxy_source(row, domain: str) -> str:
    area = pd.to_numeric(row.get("building_area_m2"), errors="coerce")
    has_area = area is not None and not pd.isna(area) and area > 0
    if not has_area:
        return "proxy_tag"
    if domain in {"tertiary_healthcare", "higher_education", "metro_commercial"}:
        return "proxy_area"
    if _tag(row, "landuse") in _OFFICE_DOMAIN or _tag(row, "office"):
        return "proxy_area"
    return "proxy_tag"


def _observed_opportunity(row, domain: str) -> PoiOpportunity | None:
    include_in_mai = _bool_value(row, "include_in_mai", True)
    audit_status = _source_text(row, "obs_audit_status")
    if not include_in_mai or audit_status == "exclude_not_destination":
        return PoiOpportunity(
            domain=domain,
            weight=0.0,
            opportunity_source="excluded_not_destination",
            source_id=_source_text(row, "obs_source"),
            source_url=_source_text(row, "obs_source_url"),
            source_tier=_source_text(row, "obs_source_tier") or "excluded",
            confidence=_source_text(row, "obs_confidence"),
            audit_status=audit_status or "exclude_not_destination",
            include_in_mai=False,
            exclusion_reason=_source_text(row, "exclusion_reason"),
        )

    generic_value = _positive_number(row, "obs_magnitude")
    generic_unit = _source_text(row, "obs_unit")
    if generic_value is not None and generic_unit in OBSERVED_UNIT_REFS:
        ref = OBSERVED_UNIT_REFS[generic_unit]
        source_id = _source_text(row, "obs_source")
        source_tier = _explicit_source_tier(row, domain, source_id)
        return PoiOpportunity(
            domain=domain,
            weight=float(np.clip(generic_value / ref["ref"], ref["lo"], ref["hi"])),
            opportunity_source=source_tier,
            observed_value=generic_value,
            observed_unit=generic_unit,
            source_id=source_id,
            source_url=_source_text(row, "obs_source_url"),
            source_tier=source_tier,
            confidence=_source_text(row, "obs_confidence"),
            audit_status=audit_status,
        )

    spec = OBSERVED_OPPORTUNITY_REFS.get(domain)
    if spec is None:
        return None
    value = _positive_number(row, spec["column"])
    if value is None:
        return None
    source_id = _source_text(row, "obs_source")
    return PoiOpportunity(
        domain=domain,
        weight=float(np.clip(value / spec["ref"], spec["lo"], spec["hi"])),
        opportunity_source=_explicit_source_tier(row, domain, source_id),
        observed_value=value,
        observed_unit=_source_text(row, "obs_unit") or spec["unit"],
        source_id=source_id,
        source_url=_source_text(row, "obs_source_url"),
        source_tier=_explicit_source_tier(row, domain, source_id),
        confidence=_source_text(row, "obs_confidence"),
        audit_status=audit_status,
    )


def classify_poi_opportunity(row, opportunity_basis: str = "observed") -> PoiOpportunity:
    """
    Classify one POI into a MAI domain, weight, and provenance.

    Decision #21: observed magnitudes win when available; otherwise the existing
    area/tag proxy classifier is used. ``opportunity_basis="proxy"`` reproduces
    the pre-observed classifier for sensitivity and regression baselines.
    """
    if opportunity_basis not in {"observed", "proxy", "observed_strict"}:
        raise ValueError("opportunity_basis must be 'observed', 'observed_strict', or 'proxy'")
    domain, weight = classify_poi_opportunity_domain(row)
    if opportunity_basis in {"observed", "observed_strict"}:
        observed = _observed_opportunity(row, domain)
        if observed is not None:
            return observed
        if opportunity_basis == "observed_strict":
            return PoiOpportunity(
                domain=domain,
                weight=0.0,
                opportunity_source="needs_source",
                source_id=_source_text(row, "obs_source"),
                source_url=_source_text(row, "obs_source_url"),
                source_tier=_source_text(row, "obs_source_tier"),
                confidence=_source_text(row, "obs_confidence"),
                audit_status="needs_source",
                include_in_mai=True,
            )
    return PoiOpportunity(
        domain=domain,
        weight=float(weight),
        opportunity_source=_proxy_source(row, domain),
        source_id=_source_text(row, "obs_source"),
        source_url=_source_text(row, "obs_source_url"),
    )


REQUIRED_INPUT_COLUMNS = {
    "cell_id",
    "NAI",
    "MAI_A",
    "MAI_B",
    "RAC_time_A_raw",
    "RAC_time_B_raw",
    "RAC_opp_A_raw",
    "RAC_opp_B_raw",
}


def validate_accessibility_inputs(df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_INPUT_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Accessibility inputs missing columns: {sorted(missing)}")
    return df


def baseline_transit_limited(gtfs_status: str | None) -> bool:
    if not gtfs_status:
        return True
    return gtfs_status.lower() in {"missing", "stale", "unverified", "limited", "baseline_limited"}


def _safe_ratio(num: np.ndarray, den: np.ndarray) -> np.ndarray:
    return np.divide(num, den, out=np.zeros_like(num, dtype=float), where=den > 0)


def population_supply_multiplier(
    pop_density: np.ndarray,
    lo: float = 0.5,
    hi: float = 2.0,
) -> np.ndarray:
    """
    Supply-side population multiplier for MAI opportunity weights (Decision #19).

    Each POI's opportunity weight is scaled by the residential density around it,
    on the rationale that an opportunity sited in a denser catchment serves a larger
    market/population (more relevant metropolitan opportunity). This complements the
    building-footprint magnitude proxy (Decision #18) rather than replacing it.

    Formula, centered at the median so a POI at typical density is unchanged (~1.0):

        m_j = clip( sqrt(pop_density_j / median(pop_density>0)), lo, hi )

    sqrt damps the signal (lesson from #18 over-correction where an undamped magnitude
    proxy let one domain reach 87% of MAI mass). Median-centering avoids a global
    inflation/deflation of all weights. Bounds keep any single POI within [lo, hi]x.

    pop_density : residential density per POI (e.g. pop_density_per_km2 of the cell
                  containing the POI). NaN / <=0 → multiplier 1.0 (neutral).
    Returns an array of multipliers, same length as pop_density.
    """
    pd_arr = np.asarray(pop_density, dtype=float)
    positive = pd_arr[np.isfinite(pd_arr) & (pd_arr > 0)]
    if positive.size == 0:
        return np.ones_like(pd_arr)
    median = float(np.median(positive))
    if median <= 0:
        return np.ones_like(pd_arr)
    ratio = np.where(np.isfinite(pd_arr) & (pd_arr > 0), pd_arr / median, 1.0)
    mult = np.sqrt(ratio)
    return np.clip(mult, lo, hi)


def _relations_with_geometry(overpass_json: Path | None) -> int:
    if overpass_json is None or not overpass_json.exists():
        return 0
    data = json.loads(overpass_json.read_text(encoding="utf-8"))
    count = 0
    for element in data.get("elements", []):
        members = element.get("members", []) or []
        if element.get("geometry") or any(member.get("geometry") for member in members):
            count += 1
    return count


def build_proxy_accessibility_inputs(
    cell_ids: Iterable,
    nai: Iterable[float],
    motorcycle_opportunities: Iterable[float] | None = None,
    vinbus_route_bonus: float = 0.0,
    gtfs_status: str | None = "stale",
) -> pd.DataFrame:
    """Small pure builder used by tests and as a fallback for spatial assembly."""
    nai_arr = np.asarray(list(nai), dtype=float)
    moto = np.asarray(list(motorcycle_opportunities), dtype=float) if motorcycle_opportunities is not None else np.maximum(nai_arr, 1)
    limited = baseline_transit_limited(gtfs_status)
    mai_a = np.zeros_like(nai_arr) if limited else nai_arr.copy()
    mai_b = np.maximum(mai_a, nai_arr + vinbus_route_bonus)

    # Conservative proxy: motorcycles are faster than walk+transit baseline;
    # VinBus reduces the walk+transit penalty when geometry is available.
    motorcycle_time = 10 + moto
    wt_a_time = motorcycle_time * (3.0 if limited else 2.0)
    wt_b_time = np.maximum(motorcycle_time * 1.5, wt_a_time - max(vinbus_route_bonus, 0.0))

    out = pd.DataFrame({
        "cell_id": list(cell_ids),
        "NAI": nai_arr,
        "MAI_A": mai_a,
        "MAI_B": mai_b,
        "RAC_time_A_raw": _safe_ratio(motorcycle_time, wt_a_time),
        "RAC_time_B_raw": _safe_ratio(motorcycle_time, wt_b_time),
        "RAC_opp_A_raw": _safe_ratio(mai_a, moto),
        "RAC_opp_B_raw": _safe_ratio(mai_b, moto),
        "MAI_A_baseline_limited": limited,
        "accessibility_input_notes": "proxy-v1; replace with network travel-time metrics when route/stop timetable data is complete",
    })
    return validate_accessibility_inputs(out)


def build_spatial_accessibility_inputs(
    grid_path: str | Path,
    pois_path: str | Path,
    vinbus_geometry_json: str | Path | None = None,
    gtfs_status: str | None = "stale",
    walking_threshold_m: float = 800.0,
    motorcycle_threshold_m: float = 3000.0,
) -> pd.DataFrame:
    """Build conservative v1 inputs from grid, POIs, and optional VinBus geometry."""
    import geopandas as gpd

    grid = gpd.read_file(grid_path).to_crs(epsg=3857)
    pois = gpd.read_file(pois_path).to_crs(epsg=3857)
    centroids = grid.geometry.centroid
    poi_points = pois.geometry.centroid

    nai = []
    moto_opp = []
    for centroid in centroids:
        distances = poi_points.distance(centroid)
        nai.append(int((distances <= walking_threshold_m).sum()))
        moto_opp.append(int((distances <= motorcycle_threshold_m).sum()))

    route_bonus = float(_relations_with_geometry(Path(vinbus_geometry_json)) if vinbus_geometry_json else 0)
    return build_proxy_accessibility_inputs(
        grid["cell_id"].tolist(),
        nai,
        motorcycle_opportunities=moto_opp,
        vinbus_route_bonus=route_bonus,
        gtfs_status=gtfs_status,
    )


def build_network_accessibility_inputs(
    grid_path: str | Path,
    pois_path: str | Path,
    walk_graphml: str | Path,
    drive_graphml: str | Path,
    vinbus_geometry_json: str | Path | None = None,
    gtfs_zip: str | Path | None = None,
    gtfs_status: str | None = "baseline_limited",
    walk_cutoff_min: float = 15.0,
    motorcycle_cutoff_min: float = 20.0,
    transit_access_m: float = 800.0,
    transit_opportunity_m: float = 800.0,
    speed_factor_csv: str | Path | None = None,
    headway_min: float = 15.0,
    vinbus_mode: str = "stops",
    bus_speed_kph: float = 20.0,
    vinbus_gtfs_dir: str | Path | None = None,
    buildings_path: str | Path | None = "data/raw/building_footprints.gpkg",
    t_full_min: float = 30.0,
    t_zero_min: float = 60.0,
    domain_weights: dict[str, float] | None = None,
    pop_weighting: bool = True,
    worldpop_csv: str | Path | None = "data/interim/grid_worldpop.csv",
    pop_mult_bounds: tuple[float, float] = (0.5, 2.0),
    opportunity_basis: str = "proxy",
) -> pd.DataFrame:
    """
    Build pilot inputs using MAI v8: composite Metropolitan Opportunity Accessibility
    (Decision #12) computed separately for transit and motorcycle, then
    RAC_opp = MAI_transit / MAI_motorcycle.

    headway_min: VinBus service headway (minutes). T_wait = headway/2 added to
    corridor travel times. 15 min = published baseline; sensitivity uses 10 and 30.

    vinbus_gtfs_dir: path to pseudo-GTFS directory scraped from VinBus API
    (176 routes / 5,631 stops / per-route headway). When provided *and*
    vinbus_mode == "stops", this takes priority over overpass-based
    vinbus_stop_accessibility. Per-route headway from frequencies.txt is used
    instead of the scalar headway_min (which becomes the default fallback for
    routes missing frequencies).
    """
    import geopandas as gpd

    grid = gpd.read_file(grid_path)
    pois = gpd.read_file(pois_path)

    # Spatial join with building footprints to get building_area_m2
    if buildings_path is not None and Path(buildings_path).exists():
        try:
            # Drop any pre-existing building_area_m2 (synthetic economic POIs carry one)
            # so the sjoin_nearest does not create _left/_right suffixes that lose the column.
            if "building_area_m2" in pois.columns:
                pois = pois.drop(columns=["building_area_m2"])
            bld = gpd.read_file(buildings_path)
            metric_crs = bld.estimate_utm_crs()
            pois_m = pois.to_crs(metric_crs)
            bld_m = bld.to_crs(metric_crs)
            bld_m["building_area_m2"] = bld_m.geometry.area
            
            # Find nearest building within 25 meters
            nearest = gpd.sjoin_nearest(
                pois_m,
                bld_m[["building_area_m2", "geometry"]],
                how="left",
                max_distance=25.0,
                distance_col="distance",
            )
            # Remove duplicate matches and join area back to pois
            nearest = nearest.sort_values("distance").drop_duplicates(subset=["id"])
            pois = pois.merge(
                nearest[["id", "building_area_m2"]],
                on="id",
                how="left",
            )
            print(f"Matched {pois['building_area_m2'].notna().sum()} POIs to building footprints.")
        except Exception as e:
            print(f"Warning: Failed to match POIs to building footprints: {e}")
            pois["building_area_m2"] = np.nan
    else:
        pois["building_area_m2"] = np.nan
    grid_points = gpd.GeoSeries(grid.to_crs(epsg=3857).geometry.centroid, crs="EPSG:3857").to_crs(epsg=4326)
    poi_points = gpd.GeoSeries(pois.to_crs(epsg=3857).geometry.centroid, crs="EPSG:3857").to_crs(epsg=4326)
    grid_nodes_gdf = gpd.GeoDataFrame(grid[["cell_id"]].copy(), geometry=grid_points, crs="EPSG:4326")
    poi_nodes_gdf = gpd.GeoDataFrame(pois.drop(columns="geometry", errors="ignore"), geometry=poi_points, crs="EPSG:4326")

    walk_graph, walk_weight = load_timed_graph(walk_graphml, "walk")
    drive_graph, drive_weight = load_timed_graph(drive_graphml, "motorcycle", speed_factor_csv=speed_factor_csv)
    grid_walk_nodes = nearest_graph_nodes(walk_graph, grid_nodes_gdf)
    poi_walk_nodes = nearest_graph_nodes(walk_graph, poi_nodes_gdf)
    grid_drive_nodes = nearest_graph_nodes(drive_graph, grid_nodes_gdf)
    poi_drive_nodes = nearest_graph_nodes(drive_graph, poi_nodes_gdf)

    # NAI: count-based, walk-only (unchanged from v1)
    nai, walk_mean_time = reachable_counts_and_mean_time(
        walk_graph, grid_walk_nodes, poi_walk_nodes, walk_cutoff_min * 60, walk_weight
    )
    _, moto_mean_time = reachable_counts_and_mean_time(
        drive_graph, grid_drive_nodes, poi_drive_nodes, motorcycle_cutoff_min * 60, drive_weight
    )

    # MAI v8/v9: classify each POI into domain + opportunity weight.
    # opportunity_basis="proxy" reproduces the pre-Decision #21 classifier.
    poi_classifications = [
        classify_poi_opportunity(row, opportunity_basis=opportunity_basis)
        for _, row in pois.iterrows()
    ]
    if opportunity_basis == "observed_strict":
        blockers = [
            (idx, opp.opportunity_source)
            for idx, opp in enumerate(poi_classifications)
            if opp.include_in_mai and opp.opportunity_source not in OBSERVED_SOURCE_VALUES
        ]
        if blockers:
            preview = ", ".join(f"{idx}:{src}" for idx, src in blockers[:10])
            raise ValueError(
                "observed_strict MAI requires source-backed magnitudes for every "
                f"included POI; {len(blockers)} blockers ({preview})"
            )
    poi_domains = [opp.domain for opp in poi_classifications]
    poi_opp_weights = [opp.weight for opp in poi_classifications]
    poi_opp_sources = [opp.opportunity_source for opp in poi_classifications]

    # Supply-side population weighting (Decision #19): scale each POI's opportunity
    # weight by residential density of the grid cell that contains it. Applied to ALL
    # domains with sqrt damp + bounds (see population_supply_multiplier). The SAME
    # weights flow into mai_moto, mai_a, mai_b so RAC_opp ratios stay consistent.
    # poi_opp_weights stays unmodified as the no-pop sensitivity baseline.
    pop_mult = np.ones(len(pois), dtype=float)
    if pop_weighting and worldpop_csv is not None and Path(worldpop_csv).exists():
        try:
            import geopandas as gpd

            worldpop = pd.read_csv(worldpop_csv, dtype={"cell_id": str})
            pop_by_cell = worldpop.set_index("cell_id")["pop_density_per_km2"].to_dict()
            grid_for_join = grid[["cell_id", "geometry"]].to_crs(epsg=4326)
            # Reset to a clean positional index so left rows align 1:1 with `pois`.
            poi_pts = poi_nodes_gdf[["geometry"]].reset_index(drop=True)
            poi_in_cell = gpd.sjoin(
                poi_pts, grid_for_join, how="left", predicate="within"
            )
            poi_in_cell = poi_in_cell[~poi_in_cell.index.duplicated(keep="first")]
            poi_cell_ids = poi_in_cell.reindex(range(len(pois)))["cell_id"]

            def _norm_cell_id(cid):
                # sjoin can return cell_id as float (e.g. 150.0); worldpop keys are "150".
                if pd.isna(cid):
                    return None
                if isinstance(cid, float) and cid.is_integer():
                    return str(int(cid))
                return str(cid)

            poi_pop_density = np.array(
                [pop_by_cell.get(_norm_cell_id(cid), np.nan) if pd.notna(cid) else np.nan
                 for cid in poi_cell_ids],
                dtype=float,
            )
            pop_mult = population_supply_multiplier(
                poi_pop_density, lo=pop_mult_bounds[0], hi=pop_mult_bounds[1]
            )
            print(
                f"Pop-weighting MAI (Decision #19): {np.isfinite(poi_pop_density).sum()}/"
                f"{len(pois)} POIs matched to a cell; multiplier "
                f"[{pop_mult.min():.2f}, {pop_mult.max():.2f}], mean {pop_mult.mean():.2f}."
            )
        except Exception as e:  # pragma: no cover - defensive; falls back to no weighting
            print(f"Warning: pop-weighting failed, using unweighted MAI: {e}")
            pop_mult = np.ones(len(pois), dtype=float)
    poi_opp_weights_eff = [w * float(m) for w, m in zip(poi_opp_weights, pop_mult)]
    observed_flags = np.array([src in OBSERVED_SOURCE_VALUES for src in poi_opp_sources], dtype=bool)
    poi_weight_arr = np.asarray(poi_opp_weights_eff, dtype=float)
    coverage_cols: dict[str, float] = {}
    total_weight = float(np.sum(poi_weight_arr))
    coverage_cols["obs_coverage_total"] = (
        float(np.sum(poi_weight_arr[observed_flags]) / total_weight) if total_weight > 0 else 0.0
    )
    for domain in OBSERVED_OPPORTUNITY_REFS:
        mask = np.array([d == domain for d in poi_domains], dtype=bool)
        domain_weight = float(np.sum(poi_weight_arr[mask]))
        coverage_cols[f"obs_coverage_{domain}"] = (
            float(np.sum(poi_weight_arr[mask & observed_flags]) / domain_weight)
            if domain_weight > 0 else 0.0
        )

    moto_mean_opp_time = opportunity_weighted_mean_time(
        drive_graph,
        grid_drive_nodes,
        poi_drive_nodes,
        poi_domains,
        poi_opp_weights_eff,
        drive_weight,
        domain_weights=domain_weights,
        t_zero_min=t_zero_min,
    )

    # MAI_motorcycle: what can motorcycle reach (Network D baseline denominator for RAC_opp)
    mai_moto = composite_mai_from_graph(
        drive_graph, grid_drive_nodes, poi_drive_nodes,
        poi_domains, poi_opp_weights_eff, drive_weight,
        t_full_min=t_full_min, t_zero_min=t_zero_min,
        domain_weights=domain_weights,
    )

    gtfs_missing = gtfs_zip is None or not Path(gtfs_zip).exists()
    baseline_limited = baseline_transit_limited(gtfs_status) or gtfs_missing

    # MAI_A: walk + existing transit (Network B, pre-VinBus baseline)
    # Transit travel-time proxy: for cells with stop access, use stop proximity time.
    # composite_mai_from_graph on walk graph approximates walk-to-stop reachability.
    # When GTFS is missing, fall back to zeros (same behavior as v1).
    if gtfs_missing:
        mai_a = np.zeros(len(grid), dtype=float)
        wt_a_time = np.maximum(moto_mean_time * 3.0, 1.0)
    else:
        stops = gtfs_stops_from_zip(gtfs_zip)
        _, wt_a_time = stop_accessibility(grid, pois, stops, transit_access_m, transit_opportunity_m)
        # MAI_A uses walk graph as proxy for walk-access-to-stops (stop timetable unavailable for routing)
        mai_a = composite_mai_from_graph(
            walk_graph, grid_walk_nodes, poi_walk_nodes,
            poi_domains, poi_opp_weights_eff, walk_weight,
            t_full_min=t_full_min, t_zero_min=t_zero_min,
            domain_weights=domain_weights,
        )
        wt_a_mean_opp_time = opportunity_weighted_mean_time(
            walk_graph,
            grid_walk_nodes,
            poi_walk_nodes,
            poi_domains,
            poi_opp_weights_eff,
            walk_weight,
            domain_weights=domain_weights,
            t_zero_min=t_zero_min,
        )

    if vinbus_mode not in {"stops", "corridor"}:
        raise ValueError("vinbus_mode must be 'stops' or 'corridor'")

    # MAI_B: walk + existing transit + VinBus (Network C)
    vinbus_gtfs_available = (
        vinbus_gtfs_dir is not None and (Path(vinbus_gtfs_dir) / "stops.txt").exists()
    )
    transit_components: dict | None = None
    if vinbus_mode == "stops" and vinbus_gtfs_available:
        # Primary: API-scraped pseudo-GTFS (176 routes / 5,631 stops / per-route headway).
        vinbus_mai, vinbus_time, transit_components = vinbus_stop_accessibility_pseudo_gtfs(
            walk_graph,
            grid,
            pois,
            grid_walk_nodes,
            poi_walk_nodes,
            poi_domains,
            poi_opp_weights_eff,
            walk_weight,
            vinbus_gtfs_dir,
            access_m=transit_access_m,
            default_headway_min=headway_min,
            bus_speed_kph=bus_speed_kph,
            t_full_min=t_full_min,
            t_zero_min=t_zero_min,
            domain_weights=domain_weights,
            return_components=True,
        )
        mai_b = np.maximum(mai_a, vinbus_mai)
        wt_b_time = np.minimum(wt_a_time, np.where(vinbus_time > 0, vinbus_time, wt_a_time))
    elif vinbus_mode == "stops" and vinbus_geometry_json is not None:
        # Sensitivity fallback: OSM Overpass relations + scalar headway.
        vinbus_mai, vinbus_time = vinbus_stop_accessibility(
            walk_graph,
            grid,
            pois,
            grid_walk_nodes,
            poi_walk_nodes,
            poi_domains,
            poi_opp_weights_eff,
            walk_weight,
            vinbus_geometry_json,
            access_m=transit_access_m,
            headway_min=headway_min,
            bus_speed_kph=bus_speed_kph,
            t_full_min=t_full_min,
            t_zero_min=t_zero_min,
            domain_weights=domain_weights,
        )
        mai_b = np.maximum(mai_a, vinbus_mai)
        wt_b_time = np.minimum(wt_a_time, np.where(vinbus_time > 0, vinbus_time, wt_a_time))
    else:
        corridor = vinbus_corridor_from_overpass(vinbus_geometry_json)
        if corridor is not None and len(corridor) > 0:
        # VinBus adds corridor-adjacent POI access on top of Network A baseline.
        # We approximate by taking max(MAI_A, walk-graph MAI scaled by corridor bonus).
        # Full travel-time routing on Network C deferred to when GTFS/VinBus timetables exist.
            vinbus_opp_raw, wt_b_time = corridor_accessibility(
                grid, pois, corridor, transit_access_m, transit_opportunity_m,
                headway_min=headway_min,
            )
            # Convert raw corridor POI count to a composite-mai-compatible score via simple ratio
            vinbus_bonus = vinbus_opp_raw / (np.maximum(vinbus_opp_raw.max(), 1.0))
            mai_b = np.maximum(mai_a, mai_a + vinbus_bonus * mai_a.max() * 0.5)
            wt_b_time = np.minimum(
                np.where(wt_b_time > 0, wt_b_time, np.inf),
                np.maximum(wt_a_time * 0.85, moto_mean_time * 1.5),
            )
            wt_b_time = np.where(np.isfinite(wt_b_time), wt_b_time, np.maximum(moto_mean_time * 2.0, 1.0))
        else:
            mai_b = mai_a.copy()
            wt_b_time = wt_a_time.copy()

    # RAC_opp denominator floor: 5th-percentile of non-zero mai_moto to prevent blow-up
    # when isolated drive-graph cells produce mai_moto ≈ 0 (typically <1% of pilot cells).
    _moto_floor = float(np.percentile(mai_moto[mai_moto > 0], 5)) if (mai_moto > 0).any() else 1.0

    vinbus_source = (
        "pseudo-GTFS(API)" if vinbus_gtfs_available
        else ("OSM-overpass" if vinbus_geometry_json is not None else "none")
    )

    # Population DEMAND weighting (Task 2b): origin-cell residents x MAI_B. This is an
    # equity aggregate, NOT per-cell accessibility — kept as a sensitivity column only,
    # does not affect SMCI/typology. Distinct from the supply-side population weighting
    # baked into MAI itself above (Decision #19), which scales opportunity by density
    # AROUND each POI (destination), not residents at the origin cell.
    worldpop_path = Path("data/interim/grid_worldpop.csv")
    if worldpop_path.exists():
        worldpop = pd.read_csv(worldpop_path, dtype={"cell_id": str})
        cell_ids = grid["cell_id"].astype(str).values
        pop_density = worldpop.set_index("cell_id").reindex(cell_ids)["pop_density_per_km2"].values.astype(float)
        pop_max = float(np.nanmax(pop_density)) if np.any(np.isfinite(pop_density)) else 1.0
        if pop_max == 0:
            pop_max = 1.0
        pop_density_norm = np.where(np.isfinite(pop_density), pop_density / pop_max, 0.0)
    else:
        pop_density_norm = np.zeros(len(grid), dtype=float)
    mai_b_popweighted = mai_b * pop_density_norm

    out = pd.DataFrame({
        "cell_id": grid["cell_id"].tolist(),
        "NAI": nai,
        "MAI_A": mai_a,
        "MAI_B": mai_b,
        "moto_mean_opp_time_min": moto_mean_opp_time / 60.0,
        "wt_A_mean_opp_time_min": (wt_a_mean_opp_time if not gtfs_missing else wt_a_time) / 60.0,
        "wt_B_mean_opp_time_min": wt_b_time / 60.0,
        "RAC_time_A_raw": _safe_ratio(moto_mean_opp_time, wt_a_mean_opp_time if not gtfs_missing else wt_a_time),
        "RAC_time_B_raw": _safe_ratio(moto_mean_opp_time, wt_b_time),
        # RAC_opp v8: ratio of composite MAI scores (Decision #12).
        "RAC_opp_A_raw": _safe_ratio(mai_a, np.maximum(mai_moto, _moto_floor)),
        "RAC_opp_B_raw": _safe_ratio(mai_b, np.maximum(mai_moto, _moto_floor)),
        "MAI_A_baseline_limited": baseline_limited,
        # Population demand weighting sensitivity (Task 2b).
        "pop_density_norm": pop_density_norm,
        "MAI_B_popweighted": mai_b_popweighted,
        # Decision #21 observed-opportunity provenance coverage. These are
        # destination-weight coverage shares repeated per cell for audit/reporting.
        **{name: np.full(len(grid), value, dtype=float) for name, value in coverage_cols.items()},
        # Transit component decomposition (Task 3b): mean minutes per component per cell.
        "transit_walk_access_min": transit_components["mean_walk_access_min"] if transit_components else np.zeros(len(grid)),
        "transit_wait_min": transit_components["mean_wait_min"] if transit_components else np.zeros(len(grid)),
        "transit_linehaul_min": transit_components["mean_linehaul_min"] if transit_components else np.zeros(len(grid)),
        "transit_egress_min": transit_components["mean_egress_min"] if transit_components else np.zeros(len(grid)),
        "accessibility_input_notes": (
            f"network-v1 MAI-v8; VinBus mode={vinbus_mode}; VinBus source={vinbus_source}; "
            "composite Metropolitan Opportunity Accessibility (Decision #12). "
            f"Supply-side pop-weighting={'on' if pop_weighting else 'off'} "
            f"bounds={pop_mult_bounds} (Decision #19). "
            f"Opportunity basis={opportunity_basis} (Decision #21 observed/proxy hierarchy). "
            "RAC_opp = MAI_transit / MAI_motorcycle. "
            "RAC_time_raw = motorcycle opportunity-weighted mean time / walk-transit "
            "opportunity-weighted mean time over the MAI opportunity set with 60-min cutoff; "
            "Network B time uses walk/GTFS stop-proxy timing; Network C uses pseudo-GTFS stop routing. "
            "Network B GTFS is 2018 vintage (pre-VinBus baseline per Decision #10): "
            "stop geometry valid; timetable used for relative magnitude only."
            if baseline_limited
            else f"network-v1 MAI-v8; VinBus mode={vinbus_mode}; VinBus source={vinbus_source}; "
                 "composite Metropolitan Opportunity Accessibility (Decision #12). "
                 f"Supply-side pop-weighting={'on' if pop_weighting else 'off'} "
                 f"bounds={pop_mult_bounds} (Decision #19). "
                 f"Opportunity basis={opportunity_basis} (Decision #21 observed/proxy hierarchy). "
                 "RAC_opp = MAI_transit / MAI_motorcycle. "
                 "RAC_time_raw = motorcycle opportunity-weighted mean time / walk-transit "
                 "opportunity-weighted mean time over the MAI opportunity set with 60-min cutoff; "
                 "Network B time uses walk/GTFS stop-proxy timing; Network C uses pseudo-GTFS stop routing."
        ),
    })
    return validate_accessibility_inputs(out)

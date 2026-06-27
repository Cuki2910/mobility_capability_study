"""Small routing helpers for pilot accessibility inputs."""
from __future__ import annotations

from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd

try:
    from .networks import build_motorcycle_network, build_walk_network
    from .accessibility import MAI_DOMAIN_WEIGHTS, time_decay_linear
except ImportError:  # pragma: no cover
    from networks import build_motorcycle_network, build_walk_network
    from accessibility import MAI_DOMAIN_WEIGHTS, time_decay_linear


def load_timed_graph(
    graphml_path: str | Path,
    mode: str,
    speed_factor_csv: str | Path | None = None,
) -> tuple[nx.MultiDiGraph, str]:
    if mode == "walk":
        return build_walk_network(graphml_path), "walk_travel_time_s"
    if mode == "motorcycle":
        return build_motorcycle_network(graphml_path, speed_factor_csv=speed_factor_csv), "motorcycle_travel_time_s"
    raise ValueError(f"unknown mode: {mode}")


def nearest_graph_nodes(graph: nx.MultiDiGraph, geometries) -> list[int]:
    import osmnx as ox

    points = geometries.to_crs(epsg=4326)
    return list(ox.distance.nearest_nodes(graph, points.geometry.x.to_numpy(), points.geometry.y.to_numpy()))


def reachable_counts_and_mean_time(
    graph: nx.MultiDiGraph,
    origin_nodes: list[int],
    destination_nodes: list[int],
    cutoff_s: float,
    weight: str,
) -> tuple[np.ndarray, np.ndarray]:
    destination_set = set(destination_nodes)
    counts: list[int] = []
    means: list[float] = []
    for origin in origin_nodes:
        lengths = nx.single_source_dijkstra_path_length(graph, origin, cutoff=cutoff_s, weight=weight)
        times = [float(lengths[node]) for node in destination_set if node in lengths]
        counts.append(len(times))
        means.append(float(np.mean(times)) if times else float(cutoff_s))
    return np.asarray(counts, dtype=float), np.asarray(means, dtype=float)


def gtfs_stops_from_zip(gtfs_zip: str | Path | None):
    if gtfs_zip is None or not Path(gtfs_zip).exists():
        return None
    import geopandas as gpd
    import zipfile

    with zipfile.ZipFile(gtfs_zip) as zf:
        if "stops.txt" not in zf.namelist():
            return None
        with zf.open("stops.txt") as handle:
            stops = pd.read_csv(handle)
    if not {"stop_lat", "stop_lon"} <= set(stops.columns):
        return None
    return gpd.GeoDataFrame(stops, geometry=gpd.points_from_xy(stops["stop_lon"], stops["stop_lat"]), crs="EPSG:4326")


def vinbus_stops_from_pseudo_gtfs(gtfs_dir: str | Path | None):
    """Load VinBus stops from a pseudo-GTFS directory (stops.txt).

    Returns a GeoDataFrame with columns stop_id, stop_name, stop_lat, stop_lon,
    geometry — compatible with the existing vinbus_stop_accessibility() pipeline.
    Returns None when gtfs_dir is None or stops.txt is missing.
    """
    if gtfs_dir is None:
        return None
    stops_path = Path(gtfs_dir) / "stops.txt"
    if not stops_path.exists():
        return None
    import geopandas as gpd

    stops = pd.read_csv(stops_path, encoding="utf-8", dtype={"stop_id": str})
    if not {"stop_lat", "stop_lon"}.issubset(stops.columns):
        return None
    stops = stops[(stops["stop_lat"] != 0) & (stops["stop_lon"] != 0)].copy()
    return gpd.GeoDataFrame(
        stops,
        geometry=gpd.points_from_xy(stops["stop_lon"], stops["stop_lat"]),
        crs="EPSG:4326",
    )


def vinbus_headway_by_route(gtfs_dir: str | Path | None) -> dict[str, float]:
    """Load per-route headway (minutes) from pseudo-GTFS routes.txt.

    Returns {route_id: headway_min}. Routes with no parseable headway are omitted;
    callers should fall back to a default when a route_id is not in the dict.
    """
    if gtfs_dir is None:
        return {}
    routes_path = Path(gtfs_dir) / "routes.txt"
    if not routes_path.exists():
        return {}
    routes = pd.read_csv(routes_path, encoding="utf-8", dtype={"route_id": str})
    result: dict[str, float] = {}
    for _, row in routes.iterrows():
        hw = str(row.get("headway_peak_min") or "").strip()
        if not hw or hw in ("nan", ""):
            continue
        # Strip non-numeric suffix (e.g. "40 phút/Chuyến")
        hw_num = hw.split()[0].split("-")[0]
        try:
            result[str(row["route_id"])] = float(hw_num)
        except (ValueError, TypeError):
            pass
    return result


def vinbus_headway_by_period(gtfs_dir: str | Path | None) -> dict[str, dict[str, float]]:
    """Return {route_id: {"peak": float, "offpeak": float}} from pseudo-GTFS routes.txt.

    Both fields fall back to the peak value when offpeak is missing or unparseable.
    If routes.txt is absent or neither field is parseable, the route is omitted and
    callers should fall back to ``default_headway_min``.
    """
    if gtfs_dir is None:
        return {}
    routes_path = Path(gtfs_dir) / "routes.txt"
    if not routes_path.exists():
        return {}
    routes = pd.read_csv(routes_path, encoding="utf-8", dtype={"route_id": str})
    result: dict[str, dict[str, float]] = {}
    for _, row in routes.iterrows():
        def _parse(field: str) -> float | None:
            raw = str(row.get(field) or "").strip()
            if not raw or raw in ("nan", ""):
                return None
            num = raw.split()[0].split("-")[0]
            try:
                return float(num)
            except (ValueError, TypeError):
                return None

        peak = _parse("headway_peak_min")
        offpeak = _parse("headway_offpeak_min")
        if peak is None and offpeak is None:
            continue
        peak = peak if peak is not None else offpeak
        offpeak = offpeak if offpeak is not None else peak
        result[str(row["route_id"])] = {"peak": peak, "offpeak": offpeak}
    return result


def vinbus_stop_sequences_from_pseudo_gtfs(gtfs_dir: str | Path | None) -> dict[str, list[dict]]:
    """Load per-route stop sequences from pseudo-GTFS stop_times.txt.

    Returns {route_id: [{"stop_id": str, "stop_sequence": int, "direction_id": int}, ...]}.
    """
    if gtfs_dir is None:
        return {}
    st_path = Path(gtfs_dir) / "stop_times.txt"
    if not st_path.exists():
        return {}
    st = pd.read_csv(st_path, encoding="utf-8", dtype={"route_id": str, "stop_id": str})
    sequences: dict[str, list[dict]] = {}
    for route_id, group in st.groupby("route_id"):
        # Forward direction only (direction_id == 0)
        fwd = group[group["direction_id"] == 0].sort_values("stop_sequence")
        sequences[str(route_id)] = fwd[["stop_id", "stop_sequence", "direction_id"]].to_dict("records")
    return sequences


def vinbus_headway_secs_from_frequencies(gtfs_dir: str | Path | None) -> dict[str, float]:
    """Load per-route headway (minutes) from pseudo-GTFS frequencies.txt.

    Prefers frequencies.txt headway_secs (the canonical scraped field) over the
    free-text headway_peak_min in routes.txt. Returns {route_id: headway_min}.
    Routes with no parseable headway_secs are omitted; callers fall back to a
    default for any route_id not present.
    """
    if gtfs_dir is None:
        return {}
    freq_path = Path(gtfs_dir) / "frequencies.txt"
    if not freq_path.exists():
        return {}
    freq = pd.read_csv(freq_path, encoding="utf-8", dtype={"route_id": str})
    result: dict[str, float] = {}
    for _, row in freq.iterrows():
        secs = pd.to_numeric(row.get("headway_secs"), errors="coerce")
        if pd.isna(secs) or secs <= 0:
            continue
        result[str(row["route_id"])] = float(secs) / 60.0
    return result


def vinbus_stop_accessibility_pseudo_gtfs(
    walk_graph: nx.MultiDiGraph,
    grid,
    pois,
    grid_nodes: list[int],
    poi_nodes: list[int],
    poi_domains: list[str],
    poi_opp_weights: list[float],
    weight_attr: str,
    gtfs_dir: str | Path | None,
    access_m: float = 800.0,
    default_headway_min: float = 15.0,
    bus_speed_kph: float = 20.0,
    t_full_min: float = 30.0,
    t_zero_min: float = 60.0,
    domain_weights: dict[str, float] | None = None,
    time_of_day: str = "peak",
    return_components: bool = False,
) -> tuple[np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, dict]:
    """Network C stop-level VinBus access from an API-scraped pseudo-GTFS feed.

    Same line-haul proxy structure as ``vinbus_stop_accessibility`` (walk-access +
    wait + line-haul + walk-egress), but the geometry comes from the pseudo-GTFS
    ``stops.txt`` + ``stop_times.txt`` (5,631 stops / 176 routes), and the wait
    term uses each route's *observed* headway from ``frequencies.txt`` rather than
    a single scalar. Routes with no observed headway fall back to
    ``default_headway_min``.
    """
    import geopandas as gpd

    stops = vinbus_stops_from_pseudo_gtfs(gtfs_dir)
    if stops is None or len(stops) == 0:
        zeros = np.zeros(len(grid), dtype=float)
        return zeros, zeros
    stops = _filter_stops_to_grid(stops, grid, access_m)
    if stops is None or len(stops) == 0:
        zeros = np.zeros(len(grid), dtype=float)
        return zeros, zeros

    stops["stop_id"] = stops["stop_id"].astype(str)
    stop_nodes = nearest_graph_nodes(walk_graph, stops)
    stops = stops.assign(graph_node=stop_nodes)
    node_by_stop = dict(zip(stops["stop_id"], stops["graph_node"]))
    coord_by_stop = dict(zip(stops["stop_id"], zip(stops["stop_lon"], stops["stop_lat"])))
    stop_node_set = set(stop_nodes)
    poi_node_set = set(poi_nodes)
    access_cutoff_s = access_m / 1.333
    bus_mps = bus_speed_kph * 1000.0 / 3600.0

    # Stop -> POI walk (egress) times, computed once per stop graph node.
    stop_to_poi_times: dict[int, dict[int, float]] = {}
    for stop_node in stop_node_set:
        lengths = nx.single_source_dijkstra_path_length(
            walk_graph, stop_node, cutoff=access_cutoff_s, weight=weight_attr
        )
        stop_to_poi_times[stop_node] = {node: float(t) for node, t in lengths.items() if node in poi_node_set}

    sequences = vinbus_stop_sequences_from_pseudo_gtfs(gtfs_dir)
    # Period-aware headway: prefer routes.txt peak/offpeak columns; fall back to
    # frequencies.txt single headway_secs for routes not in period dict.
    period_headways = vinbus_headway_by_period(gtfs_dir)
    freq_headways = vinbus_headway_secs_from_frequencies(gtfs_dir)

    def _route_headway(route_id: str) -> float:
        period = period_headways.get(route_id)
        if period is not None:
            return period.get(time_of_day, period.get("peak", default_headway_min))
        return freq_headways.get(route_id, default_headway_min)

    # Build per-route geometry: stops in sequence order (those that fall in-grid),
    # with cumulative along-route distance and the route's wait time.
    usable_sequences: list[dict] = []
    for route_id, seq in sequences.items():
        kept = [s for s in seq if str(s["stop_id"]) in node_by_stop]
        if len(kept) < 1:
            continue
        lons = [coord_by_stop[str(s["stop_id"])][0] for s in kept]
        lats = [coord_by_stop[str(s["stop_id"])][1] for s in kept]
        seq_3857 = gpd.GeoSeries(gpd.points_from_xy(lons, lats), crs="EPSG:4326").to_crs(epsg=3857)
        cum_m = [0.0]
        for i in range(1, len(seq_3857)):
            cum_m.append(cum_m[-1] + float(seq_3857.iloc[i - 1].distance(seq_3857.iloc[i])))
        headway_min = _route_headway(str(route_id))
        wait_s = (headway_min / 2.0) * 60.0
        usable_sequences.append({
            "wait_s": wait_s,
            "stops": [
                {"graph_node": node_by_stop[str(s["stop_id"])], "cum_m": cum_m[i]}
                for i, s in enumerate(kept)
            ],
        })

    if not usable_sequences:
        zeros = np.zeros(len(grid), dtype=float)
        if return_components:
            empty_comp = {k: zeros.copy() for k in ("mean_walk_access_min", "mean_wait_min", "mean_linehaul_min", "mean_egress_min")}
            return zeros, zeros, empty_comp
        return zeros, zeros

    if domain_weights is None:
        domain_weights = MAI_DOMAIN_WEIGHTS["default"]
    scores: list[float] = []
    mean_times: list[float] = []
    comp_walk_access: list[float] = []
    comp_wait: list[float] = []
    comp_linehaul: list[float] = []
    comp_egress: list[float] = []
    for origin in grid_nodes:
        origin_lengths = nx.single_source_dijkstra_path_length(
            walk_graph, origin, cutoff=access_cutoff_s, weight=weight_attr
        )
        best_by_poi: dict[int, float] = {}
        # For component tracking: store best-route components per POI
        best_components: dict[int, tuple[float, float, float, float]] = {}  # poi_node -> (access_s, wait_s, linehaul_s, egress_s)
        for route in usable_sequences:
            wait_s = route["wait_s"]
            seq = route["stops"]
            origin_candidates = [s for s in seq if s["graph_node"] in origin_lengths]
            if not origin_candidates:
                continue
            for o_stop in origin_candidates:
                access_s = float(origin_lengths[o_stop["graph_node"]])
                for d_stop in seq:
                    egress = stop_to_poi_times.get(d_stop["graph_node"], {})
                    if not egress:
                        continue
                    linehaul_s = abs(d_stop["cum_m"] - o_stop["cum_m"]) / bus_mps if bus_mps > 0 else float("inf")
                    base_s = access_s + wait_s + linehaul_s
                    for poi_node, egress_s in egress.items():
                        total_s = base_s + egress_s
                        if total_s <= t_zero_min * 60.0 and total_s < best_by_poi.get(poi_node, float("inf")):
                            best_by_poi[poi_node] = total_s
                            best_components[poi_node] = (access_s, wait_s, linehaul_s, egress_s)
        score = 0.0
        reachable_times = []
        for i, poi_node in enumerate(poi_nodes):
            total_s = best_by_poi.get(poi_node)
            if total_s is None:
                continue
            domain = poi_domains[i]
            decay = float(time_decay_linear(np.array([total_s / 60.0]), t_full_min, t_zero_min)[0])
            score += domain_weights.get(domain, 0.0) * poi_opp_weights[i] * decay
            reachable_times.append(total_s)
        scores.append(score)
        mean_times.append(float(np.mean(reachable_times)) if reachable_times else float(t_zero_min * 60.0))
        if best_components:
            comps = list(best_components.values())
            comp_walk_access.append(float(np.mean([c[0] for c in comps])) / 60.0)
            comp_wait.append(float(np.mean([c[1] for c in comps])) / 60.0)
            comp_linehaul.append(float(np.mean([c[2] for c in comps])) / 60.0)
            comp_egress.append(float(np.mean([c[3] for c in comps])) / 60.0)
        else:
            comp_walk_access.append(0.0)
            comp_wait.append(0.0)
            comp_linehaul.append(0.0)
            comp_egress.append(0.0)
    mai_arr = np.asarray(scores, dtype=float)
    time_arr = np.asarray(mean_times, dtype=float)
    if return_components:
        components = {
            "mean_walk_access_min": np.asarray(comp_walk_access, dtype=float),
            "mean_wait_min": np.asarray(comp_wait, dtype=float),
            "mean_linehaul_min": np.asarray(comp_linehaul, dtype=float),
            "mean_egress_min": np.asarray(comp_egress, dtype=float),
        }
        return mai_arr, time_arr, components
    return mai_arr, time_arr


def vinbus_corridor_from_overpass(overpass_json: str | Path | None):
    if overpass_json is None or not Path(overpass_json).exists():
        return None
    import geopandas as gpd
    import json
    from shapely.geometry import LineString

    data = json.loads(Path(overpass_json).read_text(encoding="utf-8"))
    rows = []
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        for member in element.get("members", []) or []:
            geom = member.get("geometry") or []
            if len(geom) >= 2:
                rows.append({
                    "relation_id": element.get("id"),
                    "ref": tags.get("ref"),
                    "operator": tags.get("operator"),
                    "geometry": LineString([(p["lon"], p["lat"]) for p in geom]),
                })
    if not rows:
        return None
    return gpd.GeoDataFrame(rows, crs="EPSG:4326")

def vinbus_stops_from_overpass(overpass_json: str | Path | None):
    """Extract deduplicated VinBus stop/platform nodes from an Overpass relation dump."""
    import geopandas as gpd
    import json

    columns = ["node_id", "relation_id", "ref", "role", "route_name", "geometry"]
    if overpass_json is None or not Path(overpass_json).exists():
        return gpd.GeoDataFrame(columns=columns, geometry="geometry", crs="EPSG:4326")

    data = json.loads(Path(overpass_json).read_text(encoding="utf-8"))
    rows = []
    seen: set[int] = set()
    for element in data.get("elements", []):
        if element.get("type") != "relation":
            continue
        tags = element.get("tags", {}) or {}
        for member in element.get("members", []) or []:
            role = str(member.get("role") or "").lower()
            if member.get("type") != "node" or not ("platform" in role or "stop" in role):
                continue
            if "lat" not in member or "lon" not in member:
                continue
            node_id = int(member.get("ref"))
            if node_id in seen:
                continue
            seen.add(node_id)
            rows.append({
                "node_id": node_id,
                "relation_id": element.get("id"),
                "ref": tags.get("ref"),
                "role": member.get("role"),
                "route_name": tags.get("name"),
                "geometry": gpd.points_from_xy([float(member["lon"])], [float(member["lat"])])[0],
            })
    return gpd.GeoDataFrame(rows, columns=columns, geometry="geometry", crs="EPSG:4326")

def _vinbus_route_stop_sequences(overpass_json: str | Path | None) -> dict[int, list[dict]]:
    import json

    if overpass_json is None or not Path(overpass_json).exists():
        return {}
    data = json.loads(Path(overpass_json).read_text(encoding="utf-8"))
    sequences: dict[int, list[dict]] = {}
    for element in data.get("elements", []):
        if element.get("type") != "relation":
            continue
        relation_id = int(element.get("id"))
        tags = element.get("tags", {}) or {}
        stops = []
        seen: set[int] = set()
        for member in element.get("members", []) or []:
            role = str(member.get("role") or "").lower()
            if member.get("type") != "node" or not ("platform" in role or "stop" in role):
                continue
            if "lat" not in member or "lon" not in member:
                continue
            node_id = int(member.get("ref"))
            if node_id in seen:
                continue
            seen.add(node_id)
            stops.append({
                "node_id": node_id,
                "relation_id": relation_id,
                "ref": tags.get("ref"),
                "lat": float(member["lat"]),
                "lon": float(member["lon"]),
            })
        if stops:
            sequences[relation_id] = stops
    return sequences

def _filter_stops_to_grid(stops, grid, buffer_m: float):
    if stops is None or len(stops) == 0:
        return stops
    grid_3857 = grid.to_crs(epsg=3857)
    minx, miny, maxx, maxy = grid_3857.total_bounds
    stops_3857 = stops.to_crs(epsg=3857)
    mask = (
        (stops_3857.geometry.x >= minx - buffer_m)
        & (stops_3857.geometry.x <= maxx + buffer_m)
        & (stops_3857.geometry.y >= miny - buffer_m)
        & (stops_3857.geometry.y <= maxy + buffer_m)
    )
    return stops.loc[mask.to_numpy()].copy()

def vinbus_stop_accessibility(
    walk_graph: nx.MultiDiGraph,
    grid,
    pois,
    grid_nodes: list[int],
    poi_nodes: list[int],
    poi_domains: list[str],
    poi_opp_weights: list[float],
    weight_attr: str,
    overpass_json: str | Path | None,
    access_m: float = 800.0,
    headway_min: float = 15.0,
    bus_speed_kph: float = 20.0,
    t_full_min: float = 30.0,
    t_zero_min: float = 60.0,
    domain_weights: dict[str, float] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Compute Network C stop-level VinBus access using walk access + bus line-haul proxy."""
    stops = vinbus_stops_from_overpass(overpass_json)
    stops = _filter_stops_to_grid(stops, grid, access_m)
    if stops is None or len(stops) == 0:
        zeros = np.zeros(len(grid), dtype=float)
        return zeros, zeros

    stop_nodes = nearest_graph_nodes(walk_graph, stops)
    node_by_osm = dict(zip(stops["node_id"].astype(int), stop_nodes))
    stop_node_set = set(stop_nodes)
    poi_node_set = set(poi_nodes)
    access_cutoff_s = access_m / 1.333
    wait_s = (headway_min / 2.0) * 60.0
    bus_mps = bus_speed_kph * 1000.0 / 3600.0

    stop_to_poi_times: dict[int, dict[int, float]] = {}
    for stop_node in stop_node_set:
        lengths = nx.single_source_dijkstra_path_length(
            walk_graph, stop_node, cutoff=access_cutoff_s, weight=weight_attr
        )
        stop_to_poi_times[stop_node] = {node: float(t) for node, t in lengths.items() if node in poi_node_set}

    import geopandas as gpd

    usable_sequences = []
    allowed_node_ids = set(stops["node_id"].astype(int))
    for sequence in _vinbus_route_stop_sequences(overpass_json).values():
        seq = [s for s in sequence if int(s["node_id"]) in allowed_node_ids]
        if len(seq) < 1:
            continue
        seq_gdf = gpd.GeoDataFrame(
            seq,
            geometry=gpd.points_from_xy([s["lon"] for s in seq], [s["lat"] for s in seq]),
            crs="EPSG:4326",
        ).to_crs(epsg=3857)
        cum_m = [0.0]
        for i in range(1, len(seq_gdf)):
            cum_m.append(cum_m[-1] + float(seq_gdf.geometry.iloc[i - 1].distance(seq_gdf.geometry.iloc[i])))
        usable_sequences.append([
            {"node_id": int(row.node_id), "graph_node": node_by_osm[int(row.node_id)], "cum_m": cum_m[i]}
            for i, row in enumerate(seq_gdf.itertuples())
            if int(row.node_id) in node_by_osm
        ])

    if not usable_sequences:
        zeros = np.zeros(len(grid), dtype=float)
        return zeros, zeros

    if domain_weights is None:
        domain_weights = MAI_DOMAIN_WEIGHTS["default"]
    scores: list[float] = []
    mean_times: list[float] = []
    for origin in grid_nodes:
        origin_lengths = nx.single_source_dijkstra_path_length(
            walk_graph, origin, cutoff=access_cutoff_s, weight=weight_attr
        )
        best_by_poi: dict[int, float] = {}
        for seq in usable_sequences:
            origin_candidates = [s for s in seq if s["graph_node"] in origin_lengths]
            if not origin_candidates:
                continue
            for o_stop in origin_candidates:
                access_s = float(origin_lengths[o_stop["graph_node"]])
                for d_stop in seq:
                    egress = stop_to_poi_times.get(d_stop["graph_node"], {})
                    if not egress:
                        continue
                    linehaul_s = abs(d_stop["cum_m"] - o_stop["cum_m"]) / bus_mps if bus_mps > 0 else float("inf")
                    base_s = access_s + wait_s + linehaul_s
                    for poi_node, egress_s in egress.items():
                        total_s = base_s + egress_s
                        if total_s <= t_zero_min * 60.0 and total_s < best_by_poi.get(poi_node, float("inf")):
                            best_by_poi[poi_node] = total_s
        score = 0.0
        reachable_times = []
        for i, poi_node in enumerate(poi_nodes):
            total_s = best_by_poi.get(poi_node)
            if total_s is None:
                continue
            domain = poi_domains[i]
            decay = float(time_decay_linear(np.array([total_s / 60.0]), t_full_min, t_zero_min)[0])
            score += domain_weights.get(domain, 0.0) * poi_opp_weights[i] * decay
            reachable_times.append(total_s)
        scores.append(score)
        mean_times.append(float(np.mean(reachable_times)) if reachable_times else float(t_zero_min * 60.0))
    return np.asarray(scores, dtype=float), np.asarray(mean_times, dtype=float)


def corridor_accessibility(
    grid,
    pois,
    corridor,
    access_m: float,
    opportunity_m: float,
    headway_min: float = 15.0,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Corridor-based transit accessibility proxy.

    headway_min: service headway in minutes. T_wait = headway/2 is added to
    travel time for cells within the corridor access zone (standard transport
    planning assumption for random passenger arrivals). Default 15 min matches
    VinBus published headway on Ocean Park routes (VinBus press, 2022).
    """
    if corridor is None or len(corridor) == 0:
        zeros = np.zeros(len(grid), dtype=float)
        return zeros, zeros
    corridor_3857 = corridor.to_crs(epsg=3857)
    union = corridor_3857.geometry.union_all()
    centroids = grid.to_crs(epsg=3857).geometry.centroid
    poi_points = pois.to_crs(epsg=3857).geometry.centroid
    poi_near_corridor = poi_points.distance(union) <= opportunity_m
    corridor_poi_count = float(poi_near_corridor.sum())
    distances = centroids.distance(union)
    accessible = distances <= access_m
    opps = np.where(accessible, corridor_poi_count, 0.0)
    wait_s = (headway_min / 2.0) * 60.0
    # walk-to-stop + wait + line-haul proxy; used until timetable data exists.
    times = np.where(accessible, (distances / 1.333) + wait_s + 15 * 60, 60 * 60)
    return opps.astype(float), times.astype(float)


def stop_accessibility(grid, pois, stops, access_m: float, opportunity_m: float) -> tuple[np.ndarray, np.ndarray]:
    if stops is None or len(stops) == 0:
        zeros = np.zeros(len(grid), dtype=float)
        return zeros, zeros
    stops_3857 = stops.to_crs(epsg=3857)
    stop_union = stops_3857.geometry.union_all()
    centroids = grid.to_crs(epsg=3857).geometry.centroid
    poi_points = pois.to_crs(epsg=3857).geometry.centroid
    poi_near_stop = poi_points.apply(lambda geom: stops_3857.distance(geom).min() <= opportunity_m)
    stop_poi_count = float(poi_near_stop.sum())
    distances = centroids.distance(stop_union)
    accessible = distances <= access_m
    opps = np.where(accessible, stop_poi_count, 0.0)
    times = np.where(accessible, (distances / 1.333) + 20 * 60, 75 * 60)
    return opps.astype(float), times.astype(float)


def weighted_decay_sum(
    graph: nx.MultiDiGraph,
    origin_nodes: list[int],
    destination_nodes: list[int],
    poi_weights: list[float],
    weight_attr: str,
    t_full_min: float = 30.0,
    t_zero_min: float = 60.0,
) -> np.ndarray:
    """
    MAI v8 access score for one domain and one mode (Decision #12).

    For each origin, sum opportunity_weight_j * decay(t_ij) over all reachable POIs.
    Returns an array of length len(origin_nodes).

    poi_weights : opportunity weight per destination node (same order as destination_nodes).
    weight_attr : edge attribute for travel time in seconds.
    """
    dest_weight = dict(zip(destination_nodes, poi_weights))
    scores = []
    for origin in origin_nodes:
        lengths = nx.single_source_dijkstra_path_length(
            graph, origin, cutoff=t_zero_min * 60.0, weight=weight_attr
        )
        total = 0.0
        for node, t_s in lengths.items():
            if node in dest_weight:
                total += dest_weight[node] * float(time_decay_linear(np.array([t_s / 60.0]), t_full_min, t_zero_min)[0])
        scores.append(total)
    return np.asarray(scores, dtype=float)


def composite_mai_from_graph(
    graph: nx.MultiDiGraph,
    origin_nodes: list[int],
    destination_nodes: list[int],
    poi_domains: list[str],
    poi_opp_weights: list[float],
    weight_attr: str,
    domain_weights: dict[str, float] | None = None,
    t_full_min: float = 30.0,
    t_zero_min: float = 60.0,
    return_per_domain: bool = False,
) -> np.ndarray | tuple[np.ndarray, dict[str, np.ndarray]]:
    """
    MAI v8 composite score for all domains (Decision #12).

    Calls weighted_decay_sum() per domain then combines with domain_weights.
    Returns an array of length len(origin_nodes).

    poi_domains      : domain label per destination (same order as destination_nodes).
    poi_opp_weights  : opportunity weight per destination.
    domain_weights   : {domain: weight}; defaults to MAI_DOMAIN_WEIGHTS["default"].
    return_per_domain: if True, also return {domain: weighted contribution array}
                       (already multiplied by the domain weight, so they sum to MAI).
    """
    if domain_weights is None:
        domain_weights = MAI_DOMAIN_WEIGHTS["default"]

    domains = set(poi_domains)
    per_domain: dict[str, np.ndarray] = {}
    for domain in domains:
        idx = [i for i, d in enumerate(poi_domains) if d == domain]
        d_nodes = [destination_nodes[i] for i in idx]
        d_weights = [poi_opp_weights[i] for i in idx]
        per_domain[domain] = weighted_decay_sum(
            graph, origin_nodes, d_nodes, d_weights, weight_attr, t_full_min, t_zero_min
        )

    mai = np.zeros(len(origin_nodes), dtype=float)
    contributions: dict[str, np.ndarray] = {}
    for domain, w in domain_weights.items():
        if domain in per_domain:
            contrib = w * per_domain[domain]
            contributions[domain] = contrib
            mai += contrib
    if return_per_domain:
        return mai, contributions
    return mai

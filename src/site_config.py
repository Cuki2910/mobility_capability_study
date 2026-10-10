"""Site configuration helpers for repeatable multi-site pipeline runs."""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Any


def load_analytical_spec(path: Path | str | None = None) -> dict[str, Any]:
    """Read the working specification; historical instructions do not override it."""
    source = Path(path) if path is not None else Path(__file__).resolve().parents[1] / "config/pipeline.json"
    spec = json.loads(source.read_text(encoding="utf-8-sig"))["analytical_spec"]
    threshold = float(spec["nai_primary_threshold_m"])
    if not math.isfinite(threshold) or threshold <= 0:
        raise ValueError("nai_primary_threshold_m must be finite and positive")
    spec["nai_primary_threshold_m"] = threshold
    return spec


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "":
        return {}
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.lower() in {"null", "none"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    try:
        if any(ch in value for ch in (".", "e", "E")):
            return float(value)
        return int(value)
    except ValueError:
        return value


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Parse the small YAML subset used by config/sites/*.yml.

    Supports nested mappings with two-space indentation and scalar values.
    This avoids adding PyYAML as a dependency for one config file.
    """
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent % 2 != 0:
            raise ValueError(f"Invalid indentation in site config line: {raw_line!r}")
        key_value = line.strip()
        if ":" not in key_value:
            raise ValueError(f"Expected key: value in site config line: {raw_line!r}")
        key, value = key_value.split(":", 1)
        key = key.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        parsed = _parse_scalar(value)
        parent[key] = parsed
        if isinstance(parsed, dict):
            stack.append((indent, parsed))
    return root


@dataclass(frozen=True)
class SiteConfig:
    path: Path
    data: dict[str, Any]

    @property
    def site_id(self) -> str:
        return str(self.data["site_id"])

    def get(self, dotted_key: str, default: Any = None) -> Any:
        current: Any = self.data
        for part in dotted_key.split("."):
            if not isinstance(current, dict) or part not in current:
                return default
            current = current[part]
        return current

    def path_value(self, dotted_key: str, default: Path | str | None = None) -> Path | None:
        value = self.get(dotted_key, default)
        if value is None:
            return None
        return Path(str(value))

    def bbox(self) -> tuple[float, float, float, float]:
        lat = float(self.get("center.lat"))
        lon = float(self.get("center.lon"))
        half_box_km = float(self.get("center.half_box_km"))
        deg_per_km = 1 / 111
        return (
            lon - half_box_km * deg_per_km,
            lat - half_box_km * deg_per_km,
            lon + half_box_km * deg_per_km,
            lat + half_box_km * deg_per_km,
        )


def load_site_config(path: Path | str) -> SiteConfig:
    config_path = Path(path)
    data = _parse_simple_yaml(config_path.read_text(encoding="utf-8"))
    if "site_id" not in data:
        raise ValueError(f"Site config missing site_id: {config_path}")
    return SiteConfig(path=config_path, data=data)


def add_site_config_argument(parser: Any) -> None:
    parser.add_argument(
        "--site-config",
        type=Path,
        default=None,
        help="Optional config/sites/*.yml file. Explicit CLI args override config values.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve config/paths and print planned inputs/outputs without writing files.",
    )


def _coerce_like(value: Any, current: Any, dotted_key: str = "") -> Any:
    if dotted_key.startswith("paths."):
        return Path(str(value))
    if isinstance(current, Path):
        return Path(str(value))
    if isinstance(current, bool):
        return bool(value)
    if isinstance(current, int) and not isinstance(current, bool):
        return int(value)
    if isinstance(current, float):
        return float(value)
    return value


def apply_site_config(args: Any, parser: Any, mapping: dict[str, str]) -> SiteConfig | None:
    """Overlay config values onto argparse args without clobbering explicit CLI values."""
    config_path = getattr(args, "site_config", None)
    if config_path is None:
        return None
    config = load_site_config(config_path)
    for arg_name, dotted_key in mapping.items():
        value = config.get(dotted_key)
        if value is None:
            continue
        current = getattr(args, arg_name)
        default = parser.get_default(arg_name)
        if current == default:
            setattr(args, arg_name, _coerce_like(value, current, dotted_key))
    return config


def print_resolved_paths(title: str, values: dict[str, Any]) -> None:
    print(title)
    for key, value in values.items():
        print(f"  {key}: {value}")

"""Pure-Python GeoJSON validation for the Beacon hazard layer.

No live map or GIS library is used: the checks below are deliberately small
and deterministic. They validate structure, CRS, coordinate ranges, ring
closure, and observation timestamps, and they *disclose* (without failing)
polygons that cross the antimeridian.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

MAX_OBSERVATION_AGE = timedelta(hours=72)

# RFC 7946: GeoJSON coordinates are WGS 84 (CRS84 / EPSG:4326); a legacy
# ``crs`` member naming anything else is out of contract.
_ALLOWED_CRS_NAMES = {
    "urn:ogc:def:crs:OGC:1.3:CRS84",
    "urn:ogc:def:crs:EPSG::4326",
    "EPSG:4326",
}


@dataclass
class GeoValidationResult:
    """Machine-readable error and warning codes; never raw fixture text."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _parse_instant(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _validate_ring(ring: object, feature_idx: int, result: GeoValidationResult) -> None:
    if not isinstance(ring, list) or len(ring) < 4:
        result.errors.append(f"feature[{feature_idx}]: malformed_ring")
        return

    lons: list[float] = []
    for position in ring:
        if (
            not isinstance(position, list)
            or len(position) < 2
            or not all(isinstance(coord, (int, float)) for coord in position[:2])
        ):
            result.errors.append(f"feature[{feature_idx}]: null_or_non_numeric_coordinates")
            return
        lon, lat = float(position[0]), float(position[1])
        if not (-180.0 <= lon <= 180.0) or not (-90.0 <= lat <= 90.0):
            result.errors.append(f"feature[{feature_idx}]: impossible_coordinates")
            return
        lons.append(lon)

    if ring[0][:2] != ring[-1][:2]:
        result.errors.append(f"feature[{feature_idx}]: unclosed_ring")

    for previous, current in zip(lons, lons[1:], strict=False):
        if abs(current - previous) > 180.0:
            result.warnings.append(f"feature[{feature_idx}]: antimeridian_crossing")
            break


def validate_hazard_layer(
    geojson: dict[str, Any], as_of: datetime
) -> GeoValidationResult:
    """Validate one hazard FeatureCollection against the Beacon geo contract."""

    result = GeoValidationResult()

    if geojson.get("type") != "FeatureCollection":
        result.errors.append("not_a_feature_collection")
        return result

    crs = geojson.get("crs")
    if crs is not None:
        crs_name = ""
        if isinstance(crs, dict):
            crs_name = str(crs.get("properties", {}).get("name", ""))
        if crs_name not in _ALLOWED_CRS_NAMES:
            result.errors.append("unsupported_crs")

    features = geojson.get("features")
    if not isinstance(features, list) or not features:
        result.errors.append("empty_feature_collection")
        return result

    for idx, feature in enumerate(features):
        geometry = feature.get("geometry") if isinstance(feature, dict) else None
        if not isinstance(geometry, dict):
            result.errors.append(f"feature[{idx}]: null_geometry")
            continue
        if geometry.get("type") != "Polygon":
            result.errors.append(f"feature[{idx}]: unsupported_geometry_type")
            continue
        rings = geometry.get("coordinates")
        if not isinstance(rings, list) or not rings:
            result.errors.append(f"feature[{idx}]: malformed_ring")
            continue
        for ring in rings:
            _validate_ring(ring, idx, result)

        properties = feature.get("properties", {})
        observed_at = _parse_instant(properties.get("observed_at"))
        if observed_at is None:
            result.errors.append(f"feature[{idx}]: missing_or_naive_observed_at")
        elif as_of - observed_at > MAX_OBSERVATION_AGE:
            result.errors.append(f"feature[{idx}]: stale_observation")

    return result

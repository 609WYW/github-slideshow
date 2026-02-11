from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SCHEMA_VERSION = 1


@dataclass(slots=True)
class LoadPoint:
    max_pressure_mpa: float
    freq_per_hour: float


@dataclass(slots=True)
class ProjectModel:
    schema_version: int = SCHEMA_VERSION
    load_spectrum: list[LoadPoint] = field(default_factory=lambda: [LoadPoint(0.0, 100.0)])
    rated_pressure_mpa: float = 0.0
    active_module: str = "load_spectrum"
    modules_reserved: dict[str, Any] = field(
        default_factory=lambda: {
            "tehl": {},
            "contamination": {},
            "servo_valve": {},
            "cycloid_pump": {},
            "gear_pump": {},
            "hydraulic_cylinder": {},
        }
    )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["schema_version"] = SCHEMA_VERSION
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ProjectModel":
        load_points = [LoadPoint(**item) for item in payload.get("load_spectrum", [])]
        if not load_points:
            load_points = [LoadPoint(0.0, 100.0)]
        return cls(
            schema_version=int(payload.get("schema_version", SCHEMA_VERSION)),
            load_spectrum=load_points,
            rated_pressure_mpa=float(payload.get("rated_pressure_mpa", 0.0)),
            active_module=str(payload.get("active_module", "load_spectrum")),
            modules_reserved=dict(payload.get("modules_reserved", {})),
        )

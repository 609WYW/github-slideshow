from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import json
from typing import Dict, List


@dataclass(slots=True)
class ModuleRoute:
    key: str
    title_key: str


@dataclass(slots=True)
class ProjectState:
    name: str = "untitled"
    active_module: str = "appd_main"
    parameters: Dict[str, float] = field(default_factory=dict)


def default_routes() -> List[ModuleRoute]:
    return [
        ModuleRoute("appd_main", "app.title"),
        ModuleRoute("tehl", "module.tehl"),
        ModuleRoute("contamination", "module.contamination"),
        ModuleRoute("servo_valve", "module.servo_valve"),
        ModuleRoute("cycloid_pump", "module.cycloid_pump"),
        ModuleRoute("gear_pump", "module.gear_pump"),
        ModuleRoute("hydraulic_cylinder", "module.hydraulic_cylinder"),
    ]


def save_project(state: ProjectState, path: Path) -> None:
    path.write_text(json.dumps(asdict(state), ensure_ascii=False, indent=2), encoding="utf-8")


def load_project(path: Path) -> ProjectState:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return ProjectState(**raw)

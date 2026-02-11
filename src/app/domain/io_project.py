from __future__ import annotations

import json
from pathlib import Path

from app.domain.project_model import ProjectModel


def save_project(path: Path, project: ProjectModel) -> None:
    path.write_text(json.dumps(project.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def load_project(path: Path) -> ProjectModel:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return ProjectModel.from_dict(payload)

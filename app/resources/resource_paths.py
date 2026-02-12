from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ui_text_path() -> Path:
    return project_root() / "assets" / "i18n" / "ui_text_zh_CN.yaml"


def tehl_spec_path() -> Path:
    return project_root() / "modules" / "tehl" / "spec" / "ui_spec.yaml"


def logs_dir() -> Path:
    return project_root() / "logs"


def smoke_artifacts_dir() -> Path:
    return project_root() / "artifacts" / "smoke"

from __future__ import annotations

from app.resources.resource_paths import (  # re-export for backward compatibility
    logs_dir,
    project_root,
    smoke_artifacts_dir,
    tehl_spec_path,
    ui_text_path,
)


def ui_text_yaml_path():
    return ui_text_path()

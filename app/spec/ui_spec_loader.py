from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from shared.core.validate import validate_top_level


def _load_yaml_via_ruby(path: Path) -> dict[str, Any]:
    ruby_code = (
        "require 'yaml';"
        "require 'json';"
        "obj = YAML.load_file(ARGV[0]);"
        "puts JSON.generate(obj)"
    )
    result = subprocess.run(
        ["ruby", "-e", ruby_code, str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    if not isinstance(data, dict):
        raise ValueError("ui_spec must be a mapping")
    return data


def load_ui_spec(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    data = _load_yaml_via_ruby(p)
    errors = validate_top_level(data)
    if errors:
        raise ValueError("; ".join(errors))
    return data

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import copy
import json
import re
from typing import Any

MATLAB_CANDIDATES = [
    Path("assets/matlab/PumpLubricationApp.m"),
    Path("assets/matlab/TEHLApp.m"),
    Path("assets/matlab/main.m"),
]


@dataclass(frozen=True)
class ParsedControl:
    key: str
    label: str
    type: str
    default: Any
    unit: str
    min: float | None
    max: float | None
    tooltip: str
    group: str
    order: int
    todo: bool = False


FALLBACK_SPEC: dict[str, Any] = {
    "schema_version": "4.0",
    "meta": {
        "source": "matlab_fallback",
        "todo": True,
        "notes": ["MATLAB .m 输入缺失或解析不完整，已按最小合理假设补齐。"],
    },
    "pages": [
        {
            "id": "pressures",
            "title": "压力场",
            "plots": [
                {"title": "全局压力场", "kind": "2d", "source": "pressure", "scope": "global", "caxis_key": "p_caxis", "clip_key": "p_clip"},
                {"title": "局部压力场", "kind": "2d", "source": "pressure", "scope": "local", "caxis_key": "p_caxis", "clip_key": "p_clip"},
                {"title": "接触压力/油膜压力/总压力", "kind": "2d", "source": "pressure_components", "scope": "global", "caxis_key": "p_caxis", "clip_key": "p_clip"},
            ],
            "controls": [
                {"key": "p_clip_global", "label": "全局裁剪", "type": "bool", "default": True, "unit": "-", "min": None, "max": None, "tooltip": "全局 clip 开关", "group": "clip", "order": 1, "todo": True},
                {"key": "p_clip_local", "label": "局部裁剪", "type": "bool", "default": False, "unit": "-", "min": None, "max": None, "tooltip": "局部 clip 开关", "group": "clip", "order": 2, "todo": True},
                {"key": "p_clip_method", "label": "裁剪方法", "type": "enum", "default": "factor", "options": ["factor", "percentile"], "unit": "-", "min": None, "max": None, "tooltip": "clip 方法", "group": "clip", "order": 3, "todo": True},
                {"key": "p_cmin_factor", "label": "cmin系数", "type": "float", "default": 0.1, "unit": "-", "min": 0.0, "max": 10.0, "tooltip": "颜色条下限系数", "group": "caxis", "order": 4, "todo": True},
                {"key": "p_cmax_factor", "label": "cmax系数", "type": "float", "default": 1.0, "unit": "-", "min": 0.0, "max": 10.0, "tooltip": "颜色条上限系数", "group": "caxis", "order": 5, "todo": True},
            ],
        },
        {
            "id": "film_3d",
            "title": "膜厚3D",
            "plots": [
                {"title": "膜厚分布2D", "kind": "2d", "source": "film", "scope": "global", "caxis_key": "h_caxis", "clip_key": "h_clip"},
                {"title": "膜厚分布3D", "kind": "3d", "source": "film", "scope": "global", "caxis_key": "h_caxis", "clip_key": "h_clip"},
                {"title": "形貌/变形", "kind": "2d", "source": "deformation", "scope": "local", "caxis_key": "d_caxis", "clip_key": "d_clip"},
            ],
            "controls": [
                {"key": "h_clip_global", "label": "全局裁剪", "type": "bool", "default": True, "unit": "-", "min": None, "max": None, "tooltip": "全局 clip 开关", "group": "clip", "order": 1, "todo": True},
                {"key": "h_clip_local", "label": "局部裁剪", "type": "bool", "default": False, "unit": "-", "min": None, "max": None, "tooltip": "局部 clip 开关", "group": "clip", "order": 2, "todo": True},
                {"key": "h_clip_method", "label": "裁剪方法", "type": "enum", "default": "factor", "options": ["factor", "percentile"], "unit": "-", "min": None, "max": None, "tooltip": "clip 方法", "group": "clip", "order": 3, "todo": True},
                {"key": "h_cmin_factor", "label": "cmin系数", "type": "float", "default": 0.1, "unit": "-", "min": 0.0, "max": 10.0, "tooltip": "颜色条下限系数", "group": "caxis", "order": 4, "todo": True},
                {"key": "h_cmax_factor", "label": "cmax系数", "type": "float", "default": 1.0, "unit": "-", "min": 0.0, "max": 10.0, "tooltip": "颜色条上限系数", "group": "caxis", "order": 5, "todo": True},
            ],
        },
        {
            "id": "thermal",
            "title": "热分析",
            "plots": [
                {"title": "温度场分布", "kind": "2d", "source": "thermal", "scope": "global", "caxis_key": "t_caxis", "clip_key": "t_clip"},
                {"title": "热流", "kind": "2d", "source": "heat_flux", "scope": "local", "caxis_key": "q_caxis", "clip_key": "q_clip"},
                {"title": "粘温关系", "kind": "2d", "source": "viscosity_temp", "scope": "global", "caxis_key": "mu_caxis", "clip_key": "mu_clip"},
            ],
            "controls": [
                {"key": "t_clip_global", "label": "全局裁剪", "type": "bool", "default": True, "unit": "-", "min": None, "max": None, "tooltip": "全局 clip 开关", "group": "clip", "order": 1, "todo": True},
                {"key": "t_clip_local", "label": "局部裁剪", "type": "bool", "default": False, "unit": "-", "min": None, "max": None, "tooltip": "局部 clip 开关", "group": "clip", "order": 2, "todo": True},
                {"key": "t_clip_method", "label": "裁剪方法", "type": "enum", "default": "factor", "options": ["factor", "percentile"], "unit": "-", "min": None, "max": None, "tooltip": "clip 方法", "group": "clip", "order": 3, "todo": True},
                {"key": "t_cmin_factor", "label": "cmin系数", "type": "float", "default": 0.1, "unit": "-", "min": 0.0, "max": 10.0, "tooltip": "颜色条下限系数", "group": "caxis", "order": 4, "todo": True},
                {"key": "t_cmax_factor", "label": "cmax系数", "type": "float", "default": 1.0, "unit": "-", "min": 0.0, "max": 10.0, "tooltip": "颜色条上限系数", "group": "caxis", "order": 5, "todo": True},
            ],
        },
    ],
}


def _detect_matlab_file() -> Path | None:
    for candidate in MATLAB_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def _extract_defaults_from_matlab(content: str) -> dict[str, float]:
    defaults: dict[str, float] = {}
    patterns = [
        r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>-?\d+(?:\.\d+)?)\s*;",
        r"app\.(?P<name>[A-Za-z_][A-Za-z0-9_]*)\.Value\s*=\s*(?P<value>-?\d+(?:\.\d+)?)\s*;",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, content):
            defaults[match.group("name")] = float(match.group("value"))
    return defaults


def build_tehl_spec() -> dict[str, Any]:
    matlab_file = _detect_matlab_file()
    spec = copy.deepcopy(FALLBACK_SPEC)
    if matlab_file is None:
        return spec

    content = matlab_file.read_text(encoding="utf-8", errors="ignore")
    defaults = _extract_defaults_from_matlab(content)
    spec["meta"]["source"] = str(matlab_file)

    for page in spec["pages"]:
        for control in page["controls"]:
            matlab_key = control["key"].replace("_", "")
            if matlab_key in defaults:
                control["default"] = defaults[matlab_key]
                control["todo"] = False
    return spec


def write_spec(output_path: Path) -> Path:
    spec = build_tehl_spec()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path


if __name__ == "__main__":
    write_spec(Path("src/modules/tehl/ui_spec.yaml"))

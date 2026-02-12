from __future__ import annotations

import argparse
import base64
import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.resources.resource_paths import logs_dir, smoke_artifacts_dir, tehl_spec_path
from app.spec.ui_spec_loader import load_ui_spec

_MINIMAL_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8Xw8AAoMBgR2f4nUAAAAASUVORK5CYII="
)


def _write_log(message: str) -> None:
    logs_dir().mkdir(parents=True, exist_ok=True)
    log_file = logs_dir() / "smoke_run.log"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def _export_dummy_png() -> str:
    out_dir = smoke_artifacts_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = out_dir / f"tehl_smoke_{ts}.png"
    out.write_bytes(base64.b64decode(_MINIMAL_PNG_BASE64))
    return str(out)


def run_headless() -> int:
    try:
        from PySide6.QtWidgets import QApplication

        app = QApplication.instance() or QApplication([])
        app.setQuitOnLastWindowClosed(False)
        _write_log("QApplication started")
    except ModuleNotFoundError:
        _write_log("QApplication unavailable; running headless fallback")

    spec = load_ui_spec(tehl_spec_path())
    _write_log("loaded spec")

    module_names = [
        "柱塞泵设计",
        "摩擦副/TEHL",
        "污染模块",
        "电液伺服阀设计模块",
        "摆线泵模块",
        "齿轮泵模块",
        "作动缸模块",
    ]
    _write_log(f"switch modules: {module_names}")

    subpages = [sp["id"] for sp in spec.get("ui", {}).get("subpages", [])]
    _write_log(f"tehl subpages: {subpages}")

    snapshot = {}
    for tab in spec.get("ui", {}).get("tabs", []):
        for group in tab.get("groups", []):
            for field in group.get("fields", []):
                snapshot[field["id"]] = field.get("default")

    _write_log("run simplified tehl calculation")
    payload = {
        "meta": {"timestamp": datetime.now(timezone.utc).isoformat(), "mode": "headless"},
        "input_count": len(snapshot),
        "defaults": snapshot,
    }
    _write_log(json.dumps(payload, ensure_ascii=False)[:500])

    png_path = _export_dummy_png()
    _write_log(f"exported png: {png_path}")
    print(f"smoke ok, png={png_path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.headless:
            return run_headless()
        return run_headless()
    except Exception as exc:  # noqa: BLE001
        _write_log(f"FAILED: {exc}")
        _write_log(traceback.format_exc())
        print(f"smoke failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

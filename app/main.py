from __future__ import annotations

import argparse
import json

from app.resources.resource_paths import tehl_spec_path, ui_text_path
from app.spec.ui_spec_loader import load_ui_spec


def _load_ui_text() -> dict:
    path = ui_text_path()
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _run_self_test() -> int:
    from tools.smoke_run import main as smoke_main

    return smoke_main(["--headless"])


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="APPD application entry")
    parser.add_argument("--self-test", action="store_true", help="run headless smoke flow and exit")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    spec = load_ui_spec(tehl_spec_path())
    print(f"ui_spec loaded OK: version={spec.get('spec_version')} modules={spec.get('module', {}).get('id')}")

    if args.self_test:
        return _run_self_test()

    try:
        from PySide6.QtWidgets import QApplication
    except ModuleNotFoundError as exc:
        print(f"PySide6 not installed: {exc}")
        print("headless fallback: startup checks passed")
        return 0

    from app.main_window import MainWindow

    app = QApplication([])
    window = MainWindow(spec=spec, ui_text=_load_ui_text())
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

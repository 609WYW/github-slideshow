from __future__ import annotations

import argparse
from typing import Any

from app.spec.ui_spec_loader import load_ui_spec


def validate_field(field: dict[str, Any], errors: list[str], context: str) -> None:
    required = ["id", "label", "type", "default", "widget"]
    for key in required:
        if key not in field:
            errors.append(f"{context}: missing {key}")
    if field.get("type") == "enum" and not field.get("items"):
        errors.append(f"{context}: enum requires items")


def validate_ui(spec: dict[str, Any], errors: list[str]) -> None:
    tabs = spec.get("ui", {}).get("tabs", [])
    if not tabs:
        errors.append("ui.tabs is empty")
        return
    for tab in tabs:
        if "id" not in tab or "groups" not in tab:
            errors.append(f"tab missing id/groups: {tab}")
            continue
        for group in tab.get("groups", []):
            if "id" not in group or "title" not in group or "fields" not in group:
                errors.append(f"group malformed in tab {tab.get('id')}")
                continue
            for field in group.get("fields", []):
                validate_field(field, errors, f"tab={tab['id']} group={group['id']} field={field.get('id')}")


def validate_spec(spec: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    validate_ui(spec, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args(argv)

    spec = load_ui_spec(args.path)
    errors = validate_spec(spec)
    if errors:
        print("spec validation FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    module_id = spec.get("module", {}).get("id", "?")
    print(f"ui_spec loaded OK: version={spec.get('spec_version')} modules={module_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

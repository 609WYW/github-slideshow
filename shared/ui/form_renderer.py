from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QSpinBox,
    QWidget,
)

from modules.tehl.ui.widgets import SciDoubleLineEdit


def _create_editor(field: dict[str, Any]) -> QWidget:
    widget_kind = field.get("widget", {}).get("kind", "")
    field_type = field.get("type")
    default = field.get("default")

    if widget_kind == "slider":
        w = QSlider(Qt.Orientation.Horizontal)
        w.setMinimum(int(float(field.get("min", 0))))
        w.setMaximum(int(float(field.get("max", 100))))
        w.setValue(int(float(default)))
        return w

    if widget_kind == "check_box" or field_type == "bool":
        w = QCheckBox()
        w.setChecked(bool(default))
        return w

    if widget_kind == "combo_box" or field_type == "enum":
        w = QComboBox()
        items = field.get("items", [])
        for item in items:
            w.addItem(str(item))
        if default in items:
            w.setCurrentText(str(default))
        return w

    if widget_kind == "sci_double_edit":
        return SciDoubleLineEdit(str(default))

    if field_type == "int" and widget_kind == "spin_box":
        w = QSpinBox()
        if "min" in field:
            w.setMinimum(int(float(field["min"])))
        if "max" in field:
            w.setMaximum(int(float(field["max"])))
        w.setValue(int(float(default)))
        return w

    w = QDoubleSpinBox()
    w.setDecimals(10)
    w.setMinimum(float(field.get("min", -1e20)))
    w.setMaximum(float(field.get("max", 1e20)))
    w.setValue(float(default))
    return w


def render_form(spec_group: dict[str, Any]) -> tuple[QGroupBox, dict[str, QWidget]]:
    box = QGroupBox(str(spec_group["title"]))
    form = QFormLayout(box)
    editors: dict[str, QWidget] = {}

    for field in spec_group.get("fields", []):
        editor = _create_editor(field)
        unit = str(field.get("unit", ""))
        row = QWidget(box)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.addWidget(editor)
        row_layout.addWidget(QLabel(unit, row))
        row_layout.addStretch(1)
        form.addRow(str(field["label"]), row)
        editors[str(field["id"])] = editor

    return box, editors

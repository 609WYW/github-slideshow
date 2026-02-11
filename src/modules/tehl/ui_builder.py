from __future__ import annotations

import json
from pathlib import Path
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
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from modules.tehl.plots import PlotPane


def load_tehl_spec(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _build_control_widget(control: dict[str, Any]) -> QWidget:
    ctype = control.get("type")
    if ctype == "bool":
        widget = QCheckBox()
        widget.setChecked(bool(control.get("default", False)))
        return widget

    if ctype == "enum":
        widget = QComboBox()
        options = control.get("options", [])
        widget.addItems(options)
        default = str(control.get("default", ""))
        if default in options:
            widget.setCurrentText(default)
        return widget

    widget = QDoubleSpinBox()
    widget.setDecimals(4)
    if control.get("min") is not None:
        widget.setMinimum(float(control["min"]))
    if control.get("max") is not None:
        widget.setMaximum(float(control["max"]))
    widget.setValue(float(control.get("default", 0.0)))
    return widget


def build_tehl_tab(page_spec: dict[str, Any]) -> QWidget:
    root = QWidget()
    layout = QHBoxLayout(root)
    layout.setContentsMargins(8, 8, 8, 8)
    layout.setSpacing(8)

    splitter = QSplitter(Qt.Orientation.Horizontal)
    layout.addWidget(splitter)

    left_panel = QWidget()
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(8, 8, 8, 8)
    left_layout.setSpacing(6)

    groups: dict[str, list[dict[str, Any]]] = {}
    for control in sorted(page_spec.get("controls", []), key=lambda item: item.get("order", 0)):
        groups.setdefault(control.get("group", "general"), []).append(control)

    for group_name, controls in groups.items():
        group_box = QGroupBox(group_name)
        form = QFormLayout(group_box)
        form.setSpacing(6)
        for control in controls:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)
            field = _build_control_widget(control)
            unit = QLabel(control.get("unit", "-"))
            row_layout.addWidget(field)
            row_layout.addWidget(unit)
            form.addRow(control.get("label", control.get("key", "")), row_widget)
        left_layout.addWidget(group_box)

    left_layout.addStretch(1)

    right_tabs = QTabWidget()
    for plot in page_spec.get("plots", []):
        right_tabs.addTab(PlotPane(plot.get("title", "plot"), plot.get("kind", "2d"), plot.get("source", "")), plot.get("title", "plot"))

    splitter.addWidget(left_panel)
    splitter.addWidget(right_tabs)
    splitter.setStretchFactor(1, 1)
    return root


def build_tehl_widget(spec: dict[str, Any]) -> QTabWidget:
    tabs = QTabWidget()
    for page in spec.get("pages", []):
        tabs.addTab(build_tehl_tab(page), page.get("title", page.get("id", "tab")))
    return tabs

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QWidget

from app.ui_strings import get_text


def build_center_stub() -> QWidget:
    container = QWidget()
    layout = QVBoxLayout(container)
    label = QLabel(get_text("page.placeholder"))
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)
    return container


def build_right_actions_stub() -> QWidget:
    container = QWidget()
    layout = QVBoxLayout(container)
    panel = QListWidget()
    panel.setObjectName("actions-panel")
    panel.setToolTip(get_text("panel.actions.title"))
    panel.addItem(get_text("panel.actions.life_analysis"))
    panel.addItem(get_text("panel.actions.pump_life"))
    panel.addItem(get_text("panel.actions.bearing_life"))
    layout.addWidget(panel)
    return container

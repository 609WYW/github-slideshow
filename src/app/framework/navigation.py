from __future__ import annotations

from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from app.ui_strings import get_text
from modules.base import ModuleDefinition


def build_navigation(modules: list[ModuleDefinition]) -> tuple[QWidget, QListWidget]:
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setContentsMargins(12, 12, 6, 12)
    layout.setSpacing(8)

    title = QLabel(get_text("nav.title"))
    layout.addWidget(title)

    nav = QListWidget()
    nav.setObjectName("navigation-list")
    for module in modules:
        item = QListWidgetItem(get_text(module.nav_text_key), nav)
        item.setData(32, module.key)
    nav.setCurrentRow(0)

    layout.addWidget(nav)
    return container, nav

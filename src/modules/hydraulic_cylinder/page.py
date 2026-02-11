from __future__ import annotations

from app.ui_strings import get_text


def build_page():
    from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

    page = QWidget()
    layout = QVBoxLayout(page)
    layout.setContentsMargins(12, 12, 12, 12)
    layout.setSpacing(8)
    layout.addWidget(QLabel(get_text("module.hydraulic_cylinder.title")))
    layout.addWidget(QLabel(get_text("module.placeholder")))
    layout.addStretch(1)
    return page

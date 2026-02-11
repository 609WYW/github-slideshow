from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from app.ui_strings import get_text


@dataclass(frozen=True)
class LoadSpectrumDefaultRow:
    index: int = 1
    max_pressure_mpa: float = 0.0
    frequency_per_hour: float = 100.0


def create_default_row() -> LoadSpectrumDefaultRow:
    return LoadSpectrumDefaultRow()


def create_load_spectrum_model() -> QStandardItemModel:
    model = QStandardItemModel()
    model.setColumnCount(3)
    model.setHorizontalHeaderLabels(
        [
            get_text("load_spectrum.table.index"),
            get_text("load_spectrum.table.max_pressure"),
            get_text("load_spectrum.table.frequency"),
        ]
    )

    row = create_default_row()
    items = [
        QStandardItem(str(row.index)),
        QStandardItem(str(int(row.max_pressure_mpa))),
        QStandardItem(str(int(row.frequency_per_hour))),
    ]
    for item in items:
        item.setEditable(True)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    model.appendRow(items)
    return model


class LoadSpectrumPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("load-spectrum-page")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(12, 12, 12, 12)
        root_layout.setSpacing(12)

        title = QLabel(get_text("load_spectrum.title"))
        root_layout.addWidget(title)

        self.table_view = QTableView(self)
        self.table_view.setObjectName("load-spectrum-table")
        self.table_view.setModel(create_load_spectrum_model())
        self.table_view.verticalHeader().setVisible(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.verticalHeader().setDefaultSectionSize(26)
        root_layout.addWidget(self.table_view)

        rated_row = QWidget(self)
        rated_layout = QHBoxLayout(rated_row)
        rated_layout.setContentsMargins(0, 0, 0, 0)
        rated_layout.setSpacing(8)

        rated_form = QFormLayout()
        rated_form.setContentsMargins(0, 0, 0, 0)
        rated_form.setSpacing(8)
        self.rated_pressure_input = QLineEdit(self)
        self.rated_pressure_input.setObjectName("rated-pressure-input")
        self.rated_pressure_input.setText("0")
        self.rated_pressure_input.setFixedHeight(26)
        rated_form.addRow(get_text("load_spectrum.rated_pressure"), self.rated_pressure_input)

        rated_layout.addLayout(rated_form)
        rated_layout.addWidget(QLabel(get_text("units.mpa")))
        rated_layout.addStretch(1)

        root_layout.addWidget(rated_row)

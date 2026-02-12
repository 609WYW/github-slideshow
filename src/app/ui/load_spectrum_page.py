from __future__ import annotations

import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.app.ui_text import UIText


class LoadSpectrumPage(QWidget):
    def __init__(self, ui_text: UIText, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._ui_text = ui_text

        root = QHBoxLayout(self)

        left = QWidget(self)
        left_layout = QVBoxLayout(left)

        group = QGroupBox(self._ui_text.get("pages.load_spectrum.title"), left)
        group_layout = QVBoxLayout(group)

        rated_row = QWidget(group)
        rated_layout = QFormLayout(rated_row)
        self._rated_pressure_input = QDoubleSpinBox(rated_row)
        self._rated_pressure_input.setRange(0.0, 1000.0)
        self._rated_pressure_input.setDecimals(3)
        self._rated_pressure_input.setValue(0.0)

        rated_cell = QWidget(rated_row)
        rated_cell_layout = QHBoxLayout(rated_cell)
        rated_cell_layout.setContentsMargins(0, 0, 0, 0)
        rated_cell_layout.addWidget(self._rated_pressure_input)
        rated_cell_layout.addWidget(QLabel("MPa", rated_row))
        rated_cell_layout.addStretch(1)

        rated_layout.addRow(self._ui_text.get("pages.load_spectrum.rated_pressure"), rated_cell)
        group_layout.addWidget(rated_row)

        self._table = QTableWidget(1, 3, group)
        self._table.setHorizontalHeaderLabels(
            [
                self._ui_text.get("pages.load_spectrum.table_headers.index"),
                self._ui_text.get("pages.load_spectrum.table_headers.max_pressure"),
                self._ui_text.get("pages.load_spectrum.table_headers.frequency"),
            ]
        )
        self._table.verticalHeader().setVisible(False)

        index_item = QTableWidgetItem("1")
        index_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self._table.setItem(0, 0, index_item)
        self._table.setItem(0, 1, QTableWidgetItem("0"))
        self._table.setItem(0, 2, QTableWidgetItem("100"))

        group_layout.addWidget(self._table)

        self._confirm_button = QPushButton(self._ui_text.get("pages.load_spectrum.confirm"), group)
        self._confirm_button.clicked.connect(self._show_current_data)
        group_layout.addWidget(self._confirm_button)

        left_layout.addWidget(group)
        left_layout.addStretch(1)

        right = QWidget(self)
        right_layout = QVBoxLayout(right)
        side_buttons = self._ui_text.get_any("pages.load_spectrum.side_buttons")
        if isinstance(side_buttons, list):
            for text in side_buttons:
                button = QPushButton(str(text), right)
                button.setEnabled(False)
                right_layout.addWidget(button)
        right_layout.addStretch(1)

        root.addWidget(left, 8)
        root.addWidget(right, 2)

    def _show_current_data(self) -> None:
        rows = []
        for row in range(self._table.rowCount()):
            index_item = self._table.item(row, 0)
            max_pressure_item = self._table.item(row, 1)
            freq_item = self._table.item(row, 2)
            rows.append(
                {
                    "序号": index_item.text() if index_item else "",
                    "最大压力(MPa)": max_pressure_item.text() if max_pressure_item else "",
                    "出现频率(1/小时)": freq_item.text() if freq_item else "",
                }
            )

        payload = {
            "额定压力(MPa)": self._rated_pressure_input.value(),
            "载荷谱": rows,
        }
        QMessageBox.information(
            self,
            self._ui_text.get("pages.load_spectrum.confirm"),
            json.dumps(payload, ensure_ascii=False, indent=2),
        )

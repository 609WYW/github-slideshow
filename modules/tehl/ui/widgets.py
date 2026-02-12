from __future__ import annotations

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QLineEdit


class SciDoubleLineEdit(QLineEdit):
    def __init__(self, text: str = "0", parent=None) -> None:
        super().__init__(text, parent)
        exp = QRegularExpression(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
        self.setValidator(QRegularExpressionValidator(exp, self))

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMessageBox

from app.ui_strings import get_text


@dataclass(frozen=True)
class ActionSpec:
    text_key: str
    callback_key: str | None = None
    checkable: bool = False
    checked: bool = False


def build_action(window: QMainWindow, spec: ActionSpec, callback: Callable[[], None]) -> QAction:
    action = QAction(get_text(spec.text_key), window)
    action.setCheckable(spec.checkable)
    if spec.checkable:
        action.setChecked(spec.checked)
    action.triggered.connect(callback)
    return action


def not_implemented_dialog(window: QMainWindow) -> None:
    QMessageBox.information(
        window,
        get_text("dialog.not_implemented.title"),
        get_text("dialog.not_implemented.body"),
    )


def build_specs(keys: Iterable[str]) -> list[ActionSpec]:
    return [ActionSpec(text_key=key, callback_key=key) for key in keys]

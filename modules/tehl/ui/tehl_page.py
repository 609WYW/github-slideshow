from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from shared.core.io import load_json, save_json
from shared.ui.form_renderer import render_form
from src.tehl.solver.slipper_tehl import SlipperTEHL


class TEHLSolverWorker(QThread):
    progress = Signal(int)
    result_ready = Signal(dict)
    failed = Signal(str)

    def __init__(self, params: dict[str, Any], parent=None) -> None:
        super().__init__(parent)
        self._params = params

    def run(self) -> None:
        try:
            for pct in (5, 20, 45, 70):
                self.progress.emit(pct)
                self.msleep(100)
            solver = SlipperTEHL(self._params)
            result = solver.run()
            self.progress.emit(95)
            self.msleep(50)
            self.result_ready.emit(result)
            self.progress.emit(100)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))


class PressureMapCanvas(QWidget):
    def __init__(self, title: str, parent=None) -> None:
        super().__init__(parent)
        self._title = title
        self._fig = Figure(figsize=(3.0, 2.5), tight_layout=True)
        self._canvas = FigureCanvasQTAgg(self._fig)

        layout = QVBoxLayout(self)
        layout.addWidget(self._canvas)

    def draw_map(self, z: np.ndarray, clip: bool) -> None:
        self._fig.clear()
        ax = self._fig.add_subplot(111)
        data = z.copy()
        if clip:
            p95 = float(np.nanpercentile(data, 95))
            data = np.clip(data, 0.0, p95)
        img = ax.imshow(data, origin="lower", aspect="auto", cmap="viridis")
        ax.set_title(self._title)
        ax.set_xlabel("θ index")
        ax.set_ylabel("r index")
        self._fig.colorbar(img, ax=ax)
        self._canvas.draw_idle()


class TEHLPage(QWidget):
    run_requested = Signal(str)

    PRESSURE_PLOT_KEYS = [
        ("Global Film Pressure (Pa)", "p_film", "global"),
        ("Global Contact Pressure (Pa)", "p_contact", "global"),
        ("Global Total Pressure (Pa)", "p_total", "global"),
        ("Local Film Pressure (Pa)", "p_film", "local"),
        ("Local Contact Pressure (Pa)", "p_contact", "local"),
        ("Local Total Pressure (Pa)", "p_total", "local"),
    ]

    def __init__(self, spec: dict[str, Any], parent=None) -> None:
        super().__init__(parent)
        self._spec = spec
        self._field_widgets: dict[str, QWidget] = {}
        self._state: dict[str, Any] = {}
        self._worker: TEHLSolverWorker | None = None
        self._pressure_canvases: list[PressureMapCanvas] = []

        root = QVBoxLayout(self)
        self._tabs = QTabWidget(self)
        root.addWidget(self._tabs)

        for tab in spec["ui"]["tabs"]:
            if tab["id"] == "pressures":
                tab_widget = self._build_pressures_tab(tab)
            else:
                tab_widget = self._build_generic_tab(tab)
            self._tabs.addTab(tab_widget, str(tab["title"]))

        for fid, widget in self._field_widgets.items():
            self._bind_field_signal(fid, widget)

        self._state = self._snapshot()

        actions = QHBoxLayout()
        self._progress = QProgressBar(self)
        self._progress.setRange(0, 100)
        self._progress.setValue(0)

        run_btn = QPushButton("Run TEHL", self)
        save_btn = QPushButton("Save Config JSON", self)
        load_btn = QPushButton("Load Config JSON", self)
        run_btn.clicked.connect(self._run_tehl)
        save_btn.clicked.connect(self._save_config)
        load_btn.clicked.connect(self._load_config)

        actions.addWidget(run_btn)
        actions.addWidget(save_btn)
        actions.addWidget(load_btn)
        actions.addWidget(self._progress)
        root.addLayout(actions)

    def _build_generic_tab(self, tab: dict[str, Any]) -> QWidget:
        tab_widget = QWidget(self)
        tab_layout = QVBoxLayout(tab_widget)
        for group in tab.get("groups", []):
            group_box, editors = render_form(group)
            self._field_widgets.update(editors)
            tab_layout.addWidget(group_box)
        tab_layout.addStretch(1)
        return tab_widget

    def _build_pressures_tab(self, tab: dict[str, Any]) -> QWidget:
        tab_widget = QWidget(self)
        layout = QVBoxLayout(tab_widget)

        for group in tab.get("groups", []):
            group_box, editors = render_form(group)
            self._field_widgets.update(editors)
            layout.addWidget(group_box)

        grid_holder = QWidget(tab_widget)
        grid = QGridLayout(grid_holder)
        for idx, (title, _key, _scope) in enumerate(self.PRESSURE_PLOT_KEYS):
            canvas = PressureMapCanvas(title, grid_holder)
            self._pressure_canvases.append(canvas)
            grid.addWidget(canvas, idx // 3, idx % 3)
        layout.addWidget(grid_holder)
        return tab_widget

    def _bind_field_signal(self, field_id: str, widget: QWidget) -> None:
        if hasattr(widget, "valueChanged"):
            widget.valueChanged.connect(lambda *_: self._update_state(field_id, widget))
        elif hasattr(widget, "currentTextChanged"):
            widget.currentTextChanged.connect(lambda *_: self._update_state(field_id, widget))
        elif hasattr(widget, "toggled"):
            widget.toggled.connect(lambda *_: self._update_state(field_id, widget))
        elif hasattr(widget, "textChanged"):
            widget.textChanged.connect(lambda *_: self._update_state(field_id, widget))

    def _update_state(self, field_id: str, widget: QWidget) -> None:
        if hasattr(widget, "isChecked"):
            self._state[field_id] = bool(widget.isChecked())
        elif hasattr(widget, "currentText"):
            self._state[field_id] = widget.currentText()
        elif hasattr(widget, "value"):
            self._state[field_id] = widget.value()
        elif hasattr(widget, "text"):
            self._state[field_id] = widget.text()

    def _snapshot(self) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for fid, widget in self._field_widgets.items():
            if hasattr(widget, "isChecked"):
                out[fid] = bool(widget.isChecked())
            elif hasattr(widget, "currentText"):
                out[fid] = widget.currentText()
            elif hasattr(widget, "value"):
                out[fid] = widget.value()
            elif hasattr(widget, "text"):
                out[fid] = widget.text()
        return out

    def _apply_snapshot(self, data: dict[str, Any]) -> None:
        for fid, value in data.items():
            widget = self._field_widgets.get(fid)
            if widget is None:
                continue
            if hasattr(widget, "setChecked") and isinstance(value, bool):
                widget.setChecked(value)
            elif hasattr(widget, "setCurrentText"):
                widget.setCurrentText(str(value))
            elif hasattr(widget, "setValue"):
                widget.setValue(float(value))
            elif hasattr(widget, "setText"):
                widget.setText(str(value))
        self._state = self._snapshot()

    def _run_tehl(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            self.run_requested.emit("TEHL solver is already running")
            return

        payload = self._snapshot()
        print("Run TEHL payload:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))

        self._worker = TEHLSolverWorker(payload, self)
        self._worker.progress.connect(self._progress.setValue)
        self._worker.result_ready.connect(self._on_solver_result)
        self._worker.failed.connect(self._on_solver_failed)
        self._worker.start()
        self.run_requested.emit(f"Run TEHL started: {len(payload)} parameters")

    def _on_solver_result(self, result: dict[str, np.ndarray]) -> None:
        clip_global = bool(self._snapshot().get("clip_global", True))
        clip_local = bool(self._snapshot().get("clip_local", False))

        r = result["r"]
        theta = result["theta"]
        nr, nth = len(r), len(theta)
        local_slice = (slice(nr // 4, 3 * nr // 4), slice(nth // 4, 3 * nth // 4))

        for canvas, (_title, key, scope) in zip(self._pressure_canvases, self.PRESSURE_PLOT_KEYS):
            data = result[key]
            if scope == "local":
                data = data[local_slice]
                canvas.draw_map(data, clip_local)
            else:
                canvas.draw_map(data, clip_global)

        self.run_requested.emit("Run TEHL finished: pressure maps updated")

    def _on_solver_failed(self, message: str) -> None:
        QMessageBox.critical(self, "Run TEHL failed", message)
        self.run_requested.emit(f"Run TEHL failed: {message}")

    def _save_config(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save Config", "tehl_config.json", "JSON (*.json)")
        if not path:
            return
        save_json(Path(path), self._snapshot())
        QMessageBox.information(self, "Saved", path)

    def _load_config(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Load Config", "", "JSON (*.json)")
        if not path:
            return
        data = load_json(Path(path))
        self._apply_snapshot(data)
        QMessageBox.information(self, "Loaded", path)

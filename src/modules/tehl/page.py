from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from modules.tehl.plots import PlotPane
from modules.tehl.solver import CancelToken, run_tehl_case
from modules.tehl.spec_extractor_matlab import write_spec
from modules.tehl.ui_builder import build_tehl_widget, load_tehl_spec


SPEC_PATH = Path("src/modules/tehl/ui_spec.yaml")


class SolverWorker(QObject):
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(self, config: dict[str, Any], token: CancelToken) -> None:
        super().__init__()
        self.config = config
        self.token = token

    def run(self) -> None:
        try:
            results = run_tehl_case(self.config, self.token)
            self.finished.emit(results)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))


class TEHLPage(QWidget):
    def __init__(self, spec: dict[str, Any]) -> None:
        super().__init__()
        self.spec = spec
        self.thread: QThread | None = None
        self.worker: SolverWorker | None = None
        self.cancel_token = CancelToken()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        actions_row = QWidget(self)
        actions_layout = QHBoxLayout(actions_row)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(6)

        self.solver_method_label = QLabel("Solver")
        self.solver_method_combo = QComboBox()
        self.solver_method_combo.addItems(["CTDMA", "TDMA"])

        self.run_button = QPushButton("Run")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setEnabled(False)
        self.run_button.clicked.connect(self.start_solver)
        self.cancel_button.clicked.connect(self.cancel_solver)
        actions_layout.addWidget(self.solver_method_label)
        actions_layout.addWidget(self.solver_method_combo)
        actions_layout.addWidget(self.run_button)
        actions_layout.addWidget(self.cancel_button)
        actions_layout.addStretch(1)

        layout.addWidget(actions_row)
        self.tehl_widget = build_tehl_widget(spec)
        layout.addWidget(self.tehl_widget)

    def _default_config(self) -> dict[str, Any]:
        config: dict[str, Any] = {
            "solver_method": "CTDMA",
            "rated_pressure_mpa": 21.0,
            "speed_rpm": 1500.0,
            "inlet_temp_c": 60.0,
            "duration_h": 100.0,
            "nx": 48,
            "ny": 36,
            "length_mm": 12.0,
            "width_mm": 10.0,
        }
        for page in self.spec.get("pages", []):
            for control in page.get("controls", []):
                key = control.get("key", "")
                default = control.get("default")
                if key and default is not None:
                    config[key] = default
        if "p_solver_method" in config:
            config["solver_method"] = str(config["p_solver_method"])
        config["solver_method"] = self.solver_method_combo.currentText()
        if "p_speed_rpm" in config:
            config["speed_rpm"] = float(config["p_speed_rpm"])
        if "p_rated_pressure_mpa" in config:
            config["rated_pressure_mpa"] = float(config["p_rated_pressure_mpa"])
        if "h_length_mm" in config:
            config["length_mm"] = float(config["h_length_mm"])
        if "h_width_mm" in config:
            config["width_mm"] = float(config["h_width_mm"])
        if "h_nx" in config:
            config["nx"] = int(float(config["h_nx"]))
        if "h_ny" in config:
            config["ny"] = int(float(config["h_ny"]))
        if "t_inlet_temp_c" in config:
            config["inlet_temp_c"] = float(config["t_inlet_temp_c"])
        if "t_duration_h" in config:
            config["duration_h"] = float(config["t_duration_h"])
        return config

    def start_solver(self) -> None:
        if self.thread is not None:
            return
        self.cancel_token = CancelToken()
        config = self._default_config()

        self.thread = QThread(self)
        self.worker = SolverWorker(config, self.cancel_token)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_finished)
        self.worker.failed.connect(self._on_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self._cleanup_worker)

        self.run_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.thread.start()

    def cancel_solver(self) -> None:
        self.cancel_token.cancel()
        self.cancel_button.setEnabled(False)

    def _on_finished(self, results: dict[str, Any]) -> None:
        for plot in self.findChildren(PlotPane):
            plot.update_from_results(results)
        self.run_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def _on_failed(self, _message: str) -> None:
        self.run_button.setEnabled(True)
        self.cancel_button.setEnabled(False)

    def _cleanup_worker(self) -> None:
        if self.worker is not None:
            self.worker.deleteLater()
        if self.thread is not None:
            self.thread.deleteLater()
        self.worker = None
        self.thread = None


def build_page() -> QWidget:
    if not SPEC_PATH.exists():
        write_spec(SPEC_PATH)

    spec = load_tehl_spec(SPEC_PATH)
    return TEHLPage(spec)

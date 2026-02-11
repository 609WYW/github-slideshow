from __future__ import annotations

import math
from typing import Any

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
    from matplotlib.figure import Figure
except Exception:  # noqa: BLE001
    FigureCanvasQTAgg = None
    Figure = None


class PlotPane(QWidget):
    def __init__(self, title: str, kind: str, source: str) -> None:
        super().__init__()
        self.kind = kind
        self.source = source

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        layout.addWidget(QLabel(title))

        self.figure = None
        self.canvas = None
        self.axis = None
        self.placeholder = None

        if FigureCanvasQTAgg is None or Figure is None:
            self.placeholder = QLabel(f"{kind}:{source}:placeholder")
            layout.addWidget(self.placeholder)
            return

        self.figure = Figure(figsize=(4, 3))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axis = self.figure.add_subplot(111, projection="3d" if kind == "3d" else None)
        layout.addWidget(self.canvas)
        self.render(None)

    def render(self, data: Any) -> None:
        if self.axis is None:
            if self.placeholder is not None and data is not None:
                self.placeholder.setText(f"{self.kind}:{self.source}:data-ready")
            return

        self.axis.clear()
        if self.kind == "3d":
            if isinstance(data, list) and data and isinstance(data[0], list):
                xs, ys, zs = [], [], []
                for j, row in enumerate(data):
                    for i, value in enumerate(row):
                        xs.append(float(i))
                        ys.append(float(j))
                        zs.append(float(value))
            else:
                xs = [i / 10.0 for i in range(40)]
                ys = [i / 10.0 for i in range(40)]
                zs = [math.sin(x) * math.cos(y) for x, y in zip(xs, ys)]
            self.axis.plot_trisurf(xs, ys, zs, cmap="viridis")
        else:
            if isinstance(data, dict) and "x" in data and "y" in data:
                self.axis.plot(data["x"], data["y"])
            elif isinstance(data, list) and data and isinstance(data[0], list):
                self.axis.imshow(data, aspect="auto", origin="lower", cmap="viridis")
            else:
                xs = [i / 10.0 for i in range(100)]
                ys = [math.sin(x) for x in xs]
                self.axis.plot(xs, ys)

        self.axis.set_title(self.source)
        self.canvas.draw()

    def update_from_results(self, results: dict[str, Any]) -> None:
        self.render(results.get(self.source))

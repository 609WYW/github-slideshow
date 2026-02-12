from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from modules.tehl.ui.tehl_page import TEHLPage


class PlaceholderPage(QWidget):
    def __init__(self, text: str, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(text))
        layout.addStretch(1)


class MainWindow(QMainWindow):
    def __init__(self, spec: dict[str, Any], ui_text: dict[str, Any] | None = None) -> None:
        super().__init__()
        title = "轴向柱塞泵设计软件(APPD)（试用版）"
        if ui_text and isinstance(ui_text.get("app"), dict):
            title = str(ui_text["app"].get("window_title", title))
        self.setWindowTitle(title)
        self.resize(1360, 880)

        container = QWidget(self)
        layout = QHBoxLayout(container)

        self.nav = QListWidget(container)
        self.stack = QStackedWidget(container)
        layout.addWidget(self.nav, 2)
        layout.addWidget(self.stack, 8)

        modules = [
            ("柱塞泵设计", PlaceholderPage("柱塞泵设计模块（Stage5 壳）")),
            ("摩擦副/TEHL", self._make_tehl_container(spec)),
            ("污染模块", PlaceholderPage("污染模块（Stage5 壳）")),
            ("电液伺服阀设计模块", PlaceholderPage("电液伺服阀设计模块（Stage5 壳）")),
            ("摆线泵模块", PlaceholderPage("摆线泵模块（Stage5 壳）")),
            ("齿轮泵模块", PlaceholderPage("齿轮泵模块（Stage5 壳）")),
            ("作动缸模块", PlaceholderPage("作动缸模块（Stage5 壳）")),
        ]

        for name, page in modules:
            self.nav.addItem(QListWidgetItem(name))
            self.stack.addWidget(page)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.currentRowChanged.connect(self._on_module_switch)
        self.nav.setCurrentRow(1)

        self.setCentralWidget(container)
        self.statusBar().showMessage("就绪")

    def _make_tehl_container(self, spec: dict[str, Any]) -> QWidget:
        self._tehl_page = TEHLPage(spec, self)
        self._tehl_page.run_requested.connect(self.statusBar().showMessage)
        return self._tehl_page

    def _on_module_switch(self, idx: int) -> None:
        item = self.nav.item(idx)
        if item:
            self.statusBar().showMessage(f"已切换模块：{item.text()}")

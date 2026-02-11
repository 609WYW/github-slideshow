from __future__ import annotations

import logging

from PySide6.QtWidgets import (
    QLabel,
    QListWidget,
    QMainWindow,
    QMenu,
    QSplitter,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from app.ui_strings import get_text

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(get_text("app.title"))
        self.resize(1366, 768)
        self._build_menu()
        self._build_toolbar()
        self._build_body()

    def _build_menu(self) -> None:
        bar = self.menuBar()

        menu_file = bar.addMenu(get_text("menu.file"))
        for key in (
            "menu.file.new_design",
            "menu.file.exit_design",
            "menu.file.open_model",
            "menu.file.save",
            "menu.file.save_as",
            "menu.file.exit_app",
        ):
            menu_file.addAction(get_text(key))

        menu_view = bar.addMenu(get_text("menu.view"))
        action_standard = menu_view.addAction(get_text("menu.view.standard_toolbar"))
        action_standard.setCheckable(True)
        action_standard.setChecked(True)
        action_window = menu_view.addAction(get_text("menu.view.window_toolbar"))
        action_window.setCheckable(True)
        action_window.setChecked(True)

        menu_tools = bar.addMenu(get_text("menu.tools"))
        self._add_actions(menu_tools, (
            "menu.tools.material_db",
            "menu.tools.export_word",
            "menu.tools.export_3d",
            "menu.tools.hypneu",
            "menu.tools.optimize",
            "menu.tools.material_match",
            "menu.tools.defaults",
        ))

        menu_server = bar.addMenu(get_text("menu.server"))
        self._add_actions(menu_server, ("menu.server.upload", "menu.server.download"))

        menu_help = bar.addMenu(get_text("menu.help"))
        self._add_actions(menu_help, ("menu.help.about", "menu.help.user_manual", "menu.help.tech_manual"))

    def _add_actions(self, menu: QMenu, keys: tuple[str, ...]) -> None:
        for key in keys:
            menu.addAction(get_text(key))

    def _build_toolbar(self) -> None:
        toolbar = QToolBar(get_text("menu.view.standard_toolbar"), self)
        self.addToolBar(toolbar)
        toolbar.addAction(get_text("menu.file.open_model"))
        toolbar.addAction(get_text("menu.file.save"))

    def _build_body(self) -> None:
        root = QWidget(self)
        layout = QVBoxLayout(root)

        splitter = QSplitter()
        nav = QListWidget()
        nav.addItem(get_text("nav.design_pages"))
        center = QLabel(get_text("page.placeholder"))
        right = QListWidget()
        right.addItems([
            get_text("panel.action.life_analysis"),
            get_text("panel.action.pump_life"),
            get_text("panel.action.bearing_life"),
        ])

        splitter.addWidget(nav)
        splitter.addWidget(center)
        splitter.addWidget(right)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)
        self.setCentralWidget(root)
        logger.info("Stage 0 main window ready")

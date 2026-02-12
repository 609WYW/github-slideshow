from __future__ import annotations

from functools import partial

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QToolBar,
    QWidget,
)

from src.app.ui.load_spectrum_page import LoadSpectrumPage
from src.app.ui.module_home_page import ModuleHomePage
from src.app.ui_text import UIText


class MainWindow(QMainWindow):
    MODULE_KEYS = [
        "piston_pump_design",
        "tehl",
        "contamination",
        "servo_valve",
        "gerotor_pump",
        "gear_pump",
        "actuator_cylinder",
    ]

    def __init__(self, ui_text: UIText) -> None:
        super().__init__()
        self._ui_text = ui_text
        self.setWindowTitle(self._ui_text.get("app.window_title"))
        self.resize(1280, 820)

        self._standard_toolbar = QToolBar(self._ui_text.get("menus.view.standard_toolbar"), self)
        self._window_toolbar = QToolBar(self._ui_text.get("menus.view.window_toolbar"), self)
        self.addToolBar(self._standard_toolbar)
        self.addToolBar(self._window_toolbar)

        self._build_menus_and_toolbars()
        self._build_module_layout()
        self._build_status_bar()

    def _build_menus_and_toolbars(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu(self._ui_text.get("menus.file.title"))
        file_actions = [
            ("menus.file.start_design", "file.start_design", "Ctrl+N"),
            ("menus.file.exit_design", "file.exit_design", "Ctrl+E"),
            ("menus.file.open_model", "file.open_model", "Ctrl+O"),
            ("menus.file.save", "file.save", "Ctrl+S"),
            ("menus.file.save_as", "file.save_as", None),
            ("menus.file.exit_program", "file.exit_program", None),
        ]
        for text_key, action_id_key, shortcut in file_actions:
            action = QAction(self._ui_text.get(text_key), self)
            if shortcut:
                action.setShortcut(QKeySequence(shortcut))
            action.triggered.connect(partial(self._on_action_triggered, action_id_key))
            if action_id_key == "file.exit_program":
                action.triggered.connect(self.close)
            file_menu.addAction(action)
            if action_id_key in {"file.start_design", "file.open_model"}:
                self._standard_toolbar.addAction(action)

        view_menu = menu_bar.addMenu(self._ui_text.get("menus.view.title"))
        view_standard_action = self._standard_toolbar.toggleViewAction()
        view_standard_action.setText(self._ui_text.get("menus.view.standard_toolbar"))
        view_standard_action.triggered.connect(partial(self._on_action_triggered, "view.standard_toolbar"))
        view_menu.addAction(view_standard_action)

        view_window_action = self._window_toolbar.toggleViewAction()
        view_window_action.setText(self._ui_text.get("menus.view.window_toolbar"))
        view_window_action.triggered.connect(partial(self._on_action_triggered, "view.window_toolbar"))
        view_menu.addAction(view_window_action)

        tools_menu = menu_bar.addMenu(self._ui_text.get("menus.tools.title"))
        tool_items = [
            ("menus.tools.material_database", "tools.material_database"),
            ("menus.tools.export_word", "tools.export_word"),
            ("menus.tools.export_3d", "tools.export_3d"),
            ("menus.tools.hypneu", "tools.hypneu"),
            ("menus.tools.optimize", "tools.optimize"),
            ("menus.tools.material_pairing", "tools.material_pairing"),
            ("menus.tools.default_params", "tools.default_params"),
        ]
        for text_key, action_id_key in tool_items:
            action = QAction(self._ui_text.get(text_key), self)
            action.triggered.connect(partial(self._on_action_triggered, action_id_key))
            tools_menu.addAction(action)

        server_menu = menu_bar.addMenu(self._ui_text.get("menus.server.title"))
        for text_key, action_id_key in [
            ("menus.server.upload_design", "server.upload_design"),
            ("menus.server.download_design", "server.download_design"),
        ]:
            action = QAction(self._ui_text.get(text_key), self)
            action.triggered.connect(partial(self._on_action_triggered, action_id_key))
            server_menu.addAction(action)

        help_menu = menu_bar.addMenu(self._ui_text.get("menus.help.title"))
        for text_key, action_id_key in [
            ("menus.help.about", "help.about"),
            ("menus.help.user_manual", "help.user_manual"),
            ("menus.help.technical_manual", "help.technical_manual"),
        ]:
            action = QAction(self._ui_text.get(text_key), self)
            action.triggered.connect(partial(self._on_action_triggered, action_id_key))
            help_menu.addAction(action)

    def _build_module_layout(self) -> None:
        content = QWidget(self)
        layout = QHBoxLayout(content)

        self._module_nav = QListWidget(content)
        self._module_nav.setMinimumWidth(220)
        self._module_nav.currentRowChanged.connect(self._on_module_changed)
        layout.addWidget(self._module_nav, 2)

        self._module_stack = QStackedWidget(content)
        layout.addWidget(self._module_stack, 8)

        for module_key in self.MODULE_KEYS:
            module_name = self._ui_text.get(f"modules.{module_key}")
            home_title = f"{module_name} - {self._ui_text.get('pages.home_suffix')}"
            placeholder_text = self._ui_text.get("pages.placeholder_message").format(module_name=module_name)

            item = QListWidgetItem(module_name)
            item.setData(Qt.ItemDataRole.UserRole, module_key)
            self._module_nav.addItem(item)

            if module_key == "piston_pump_design":
                page = LoadSpectrumPage(self._ui_text)
            else:
                page = ModuleHomePage(title=home_title, message=placeholder_text)
            self._module_stack.addWidget(page)

        self._module_nav.setCurrentRow(0)
        self.setCentralWidget(content)

    def _build_status_bar(self) -> None:
        self.statusBar().showMessage(self._ui_text.get("app.status_ready"))

    def _on_module_changed(self, index: int) -> None:
        if index < 0:
            return

        self._module_stack.setCurrentIndex(index)
        module_name = self._module_nav.item(index).text()
        self.statusBar().showMessage(
            self._ui_text.get("app.status_module_switched").format(module_name=module_name)
        )

    def _on_action_triggered(self, action_key: str) -> None:
        QMessageBox.information(
            self,
            "Action Triggered",
            f"action_id={self._ui_text.get(f'action_ids.{action_key}')}",
        )

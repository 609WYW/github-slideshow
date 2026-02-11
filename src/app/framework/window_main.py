from __future__ import annotations

from functools import partial
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from app.domain.io_project import load_project, save_project
from app.domain.project_model import LoadPoint, ProjectModel
from app.framework.actions import ActionSpec, build_action, build_specs, not_implemented_dialog
from app.framework.navigation import build_navigation
from app.framework.pages import LoadSpectrumPage
from app.ui_strings import get_text
from modules.registry import get_registered_modules


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(get_text("app.title"))
        self.resize(1366, 768)
        self.current_project_path: Path | None = None
        self.modules = get_registered_modules()

        self.standard_toolbar = QToolBar(get_text("toolbar.standard"), self)
        self.window_toolbar = QToolBar(get_text("toolbar.window"), self)

        self._build_toolbars()
        self._build_menus()
        self._build_layout()

    def _build_toolbars(self) -> None:
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.standard_toolbar)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.window_toolbar)

        toolbar_actions = {
            "menu.file.open_model": self.action_open_project,
            "menu.file.save": self.action_save_project,
            "menu.file.new_design": partial(not_implemented_dialog, self),
            "menu.file.save_as": self.action_save_project_as,
        }
        for key in ("menu.file.open_model", "menu.file.save"):
            self.standard_toolbar.addAction(build_action(self, ActionSpec(key), toolbar_actions[key]))
        for key in ("menu.file.new_design", "menu.file.save_as"):
            self.window_toolbar.addAction(build_action(self, ActionSpec(key), toolbar_actions[key]))

    def _build_menus(self) -> None:
        bar = self.menuBar()

        menu_file = bar.addMenu(get_text("menu.file"))
        self._add_action_group(
            menu_file,
            build_specs(
                (
                    "menu.file.new_design",
                    "menu.file.exit_design",
                    "menu.file.open_model",
                    "menu.file.save",
                    "menu.file.save_as",
                    "menu.file.exit_program",
                )
            ),
        )

        menu_view = bar.addMenu(get_text("menu.view"))
        standard_toggle = build_action(
            self,
            ActionSpec("menu.view.standard_toolbar", checkable=True, checked=True),
            lambda: self._toggle_toolbar(self.standard_toolbar),
        )
        window_toggle = build_action(
            self,
            ActionSpec("menu.view.window_toolbar", checkable=True, checked=True),
            lambda: self._toggle_toolbar(self.window_toolbar),
        )
        menu_view.addAction(standard_toggle)
        menu_view.addAction(window_toggle)

        menu_tools = bar.addMenu(get_text("menu.tools"))
        self._add_action_group(
            menu_tools,
            build_specs(
                (
                    "menu.tools.material_database",
                    "menu.tools.export_word",
                    "menu.tools.export_3d",
                    "menu.tools.hypneu",
                    "menu.tools.optimize",
                    "menu.tools.material_match",
                    "menu.tools.defaults",
                )
            ),
        )

        menu_server = bar.addMenu(get_text("menu.server"))
        self._add_action_group(menu_server, build_specs(("menu.server.upload", "menu.server.download")))

        menu_help = bar.addMenu(get_text("menu.help"))
        self._add_action_group(
            menu_help,
            build_specs(("menu.help.about", "menu.help.user_manual", "menu.help.tech_manual")),
        )

    def _callback_for_action(self, key: str):
        callbacks = {
            "menu.file.open_model": self.action_open_project,
            "menu.file.save": self.action_save_project,
            "menu.file.save_as": self.action_save_project_as,
            "menu.file.exit_program": self.close,
        }
        return callbacks.get(key, partial(not_implemented_dialog, self))

    def _add_action_group(self, menu, specs: list[ActionSpec]) -> None:
        for spec in specs:
            callback = self._callback_for_action(spec.callback_key or spec.text_key)
            menu.addAction(build_action(self, spec, callback))

    def _toggle_toolbar(self, toolbar: QToolBar) -> None:
        toolbar.setVisible(not toolbar.isVisible())

    def _build_layout(self) -> None:
        splitter = QSplitter(self)

        nav_container, self.navigation_list = build_navigation(self.modules)
        splitter.addWidget(nav_container)

        self.center_pages = QStackedWidget(self)
        self.load_spectrum_page = None
        for module in self.modules:
            page = module.page_factory()
            if module.key == "appd_main" and isinstance(page, LoadSpectrumPage):
                self.load_spectrum_page = page
            self.center_pages.addWidget(page)
        splitter.addWidget(self.center_pages)

        splitter.addWidget(self._build_right_panel())
        splitter.setStretchFactor(1, 1)
        self.setCentralWidget(splitter)

        self.navigation_list.currentRowChanged.connect(self._on_navigation_changed)
        self._on_navigation_changed(0)

    def _build_right_panel(self) -> QWidget:
        panel = QWidget(self)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(6, 12, 12, 12)
        layout.setSpacing(8)

        self.module_action_button = QPushButton(panel)
        self.module_action_button.setEnabled(False)
        self.module_action_button.setToolTip(get_text("panel.actions.trial_unavailable"))
        self.module_action_button.setMinimumHeight(28)
        layout.addWidget(self.module_action_button)

        for key in (
            "panel.actions.cylinder_life",
            "panel.actions.bearing_life",
            "panel.actions.pump_life",
            "panel.actions.pump_life_alt",
        ):
            button = QPushButton(get_text(key), panel)
            button.setEnabled(False)
            button.setToolTip(get_text("panel.actions.trial_unavailable"))
            button.setMinimumHeight(28)
            layout.addWidget(button)

        layout.addStretch(1)
        return panel

    def _on_navigation_changed(self, index: int) -> None:
        if index < 0 or index >= len(self.modules):
            return
        self.center_pages.setCurrentIndex(index)
        current = self.modules[index]
        self.module_action_button.setText(get_text(current.title_text_key))

    def _project_from_ui(self) -> ProjectModel:
        if self.load_spectrum_page is None:
            return ProjectModel(active_module=self.modules[self.navigation_list.currentRow()].key)

        model = self.load_spectrum_page.table_view.model()
        points: list[LoadPoint] = []
        for row in range(model.rowCount()):
            max_pressure_text = model.item(row, 1).text() if model.item(row, 1) else "0"
            freq_text = model.item(row, 2).text() if model.item(row, 2) else "0"
            points.append(
                LoadPoint(
                    max_pressure_mpa=float(max_pressure_text or 0),
                    freq_per_hour=float(freq_text or 0),
                )
            )

        rated_text = self.load_spectrum_page.rated_pressure_input.text().strip() or "0"
        active_module = self.modules[self.navigation_list.currentRow()].key
        return ProjectModel(
            load_spectrum=points or [LoadPoint(0.0, 100.0)],
            rated_pressure_mpa=float(rated_text),
            active_module=active_module,
        )

    def _apply_project_to_ui(self, project: ProjectModel) -> None:
        if self.load_spectrum_page is not None:
            table_model = self.load_spectrum_page.table_view.model()
            table_model.removeRows(0, table_model.rowCount())
            for idx, point in enumerate(project.load_spectrum, start=1):
                row_items = [
                    QStandardItem(str(idx)),
                    QStandardItem(str(point.max_pressure_mpa).rstrip("0").rstrip(".")),
                    QStandardItem(str(point.freq_per_hour).rstrip("0").rstrip(".")),
                ]
                for item in row_items:
                    item.setEditable(True)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table_model.appendRow(row_items)

            self.load_spectrum_page.rated_pressure_input.setText(
                str(project.rated_pressure_mpa).rstrip("0").rstrip(".") or "0"
            )

        module_keys = [module.key for module in self.modules]
        row = module_keys.index(project.active_module) if project.active_module in module_keys else 0
        self.navigation_list.setCurrentRow(row)

    def action_save_project(self) -> None:
        target = self.current_project_path
        if target is None:
            self.action_save_project_as()
            return

        try:
            save_project(target, self._project_from_ui())
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, get_text("dialog.file.error_title"), str(exc))

    def action_save_project_as(self) -> None:
        path_str, _ = QFileDialog.getSaveFileName(
            self,
            get_text("menu.file.save_as"),
            "",
            get_text("dialog.file.filter"),
        )
        if not path_str:
            return

        target = Path(path_str)
        if target.suffix != ".json" and not target.name.endswith(".apdd.json"):
            target = target.with_name(f"{target.name}.apdd.json")

        try:
            save_project(target, self._project_from_ui())
            self.current_project_path = target
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, get_text("dialog.file.error_title"), str(exc))

    def action_open_project(self) -> None:
        path_str, _ = QFileDialog.getOpenFileName(
            self,
            get_text("menu.file.open_model"),
            "",
            get_text("dialog.file.filter"),
        )
        if not path_str:
            return

        try:
            target = Path(path_str)
            project = load_project(target)
            self._apply_project_to_ui(project)
            self.current_project_path = target
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, get_text("dialog.file.error_title"), str(exc))

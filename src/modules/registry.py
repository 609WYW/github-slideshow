from __future__ import annotations

from modules.base import ModuleDefinition


def _build_appd_main_page():
    from modules.appd_main.page import build_page

    return build_page()


def _build_tehl_page():
    from modules.tehl.page import build_page

    return build_page()


def _build_contamination_page():
    from modules.contamination.page import build_page

    return build_page()


def _build_servo_valve_page():
    from modules.servo_valve.page import build_page

    return build_page()


def _build_cycloid_pump_page():
    from modules.cycloid_pump.page import build_page

    return build_page()


def _build_gear_pump_page():
    from modules.gear_pump.page import build_page

    return build_page()


def _build_hydraulic_cylinder_page():
    from modules.hydraulic_cylinder.page import build_page

    return build_page()


def get_registered_modules() -> list[ModuleDefinition]:
    return [
        ModuleDefinition(
            key="appd_main",
            nav_text_key="nav.item.appd_main",
            title_text_key="module.appd_main.title",
            page_factory=_build_appd_main_page,
        ),
        ModuleDefinition(
            key="tehl",
            nav_text_key="nav.item.tehl",
            title_text_key="module.tehl.title",
            page_factory=_build_tehl_page,
        ),
        ModuleDefinition(
            key="contamination",
            nav_text_key="nav.item.contamination",
            title_text_key="module.contamination.title",
            page_factory=_build_contamination_page,
        ),
        ModuleDefinition(
            key="servo_valve",
            nav_text_key="nav.item.servo_valve",
            title_text_key="module.servo_valve.title",
            page_factory=_build_servo_valve_page,
        ),
        ModuleDefinition(
            key="cycloid_pump",
            nav_text_key="nav.item.cycloid_pump",
            title_text_key="module.cycloid_pump.title",
            page_factory=_build_cycloid_pump_page,
        ),
        ModuleDefinition(
            key="gear_pump",
            nav_text_key="nav.item.gear_pump",
            title_text_key="module.gear_pump.title",
            page_factory=_build_gear_pump_page,
        ),
        ModuleDefinition(
            key="hydraulic_cylinder",
            nav_text_key="nav.item.hydraulic_cylinder",
            title_text_key="module.hydraulic_cylinder.title",
            page_factory=_build_hydraulic_cylinder_page,
        ),
    ]

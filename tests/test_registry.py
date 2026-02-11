from modules.registry import get_registered_modules


def test_registry_contains_required_modules() -> None:
    modules = get_registered_modules()
    keys = [module.key for module in modules]
    assert keys == [
        "appd_main",
        "tehl",
        "contamination",
        "servo_valve",
        "cycloid_pump",
        "gear_pump",
        "hydraulic_cylinder",
    ]


def test_registry_text_keys_are_defined() -> None:
    modules = get_registered_modules()
    assert all(module.nav_text_key.startswith("nav.item.") for module in modules)
    assert all(module.title_text_key.startswith("module.") for module in modules)

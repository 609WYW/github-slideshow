from app.models import default_routes


def test_module_routes_include_required_modules() -> None:
    keys = [r.key for r in default_routes()]
    assert keys == [
        "appd_main",
        "tehl",
        "contamination",
        "servo_valve",
        "cycloid_pump",
        "gear_pump",
        "hydraulic_cylinder",
    ]

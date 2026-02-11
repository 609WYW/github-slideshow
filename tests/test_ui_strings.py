from app.ui_strings import STRINGS_ZH_CN, get_text


def test_required_menu_labels_are_exact() -> None:
    assert get_text("menu.file") == "文件(F)"
    assert get_text("menu.view") == "视图(V)"
    assert get_text("menu.tools") == "工具"
    assert get_text("menu.server") == "访问服务器"
    assert get_text("menu.help") == "帮助(H)"


def test_required_keys_complete() -> None:
    required_keys = {
        "app.title",
        "menu.file",
        "menu.file.new_design",
        "menu.file.exit_design",
        "menu.file.open_model",
        "menu.file.save",
        "menu.file.save_as",
        "menu.file.exit_program",
        "menu.view",
        "menu.view.standard_toolbar",
        "menu.view.window_toolbar",
        "menu.tools",
        "menu.tools.material_database",
        "menu.tools.export_word",
        "menu.tools.export_3d",
        "menu.tools.hypneu",
        "menu.tools.optimize",
        "menu.tools.material_match",
        "menu.tools.defaults",
        "menu.server",
        "menu.server.upload",
        "menu.server.download",
        "menu.help",
        "menu.help.about",
        "menu.help.user_manual",
        "menu.help.tech_manual",
        "dialog.not_implemented.title",
        "dialog.not_implemented.body",
    }
    assert required_keys.issubset(set(STRINGS_ZH_CN.keys()))
    assert all(STRINGS_ZH_CN[key].strip() for key in required_keys)

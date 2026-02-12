from __future__ import annotations

from typing import Any

from shared.ui.form_renderer import render_form


def build_group_widget(spec_group: dict[str, Any]):
    return render_form(spec_group)

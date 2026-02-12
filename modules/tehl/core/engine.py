from __future__ import annotations

from modules.tehl.core.types import TEHLRunInput, TEHLRunOutput


def run_tehl(input_data: TEHLRunInput) -> TEHLRunOutput:
    _ = input_data
    return TEHLRunOutput(status="ok", kpis={"leakage_Q": 0.0, "friction_power": 0.0})

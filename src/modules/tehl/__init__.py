from .spec_extractor_matlab import build_tehl_spec, write_spec

__all__ = ["build_page", "build_tehl_spec", "write_spec"]


def build_page():
    from .page import build_page as _build_page

    return _build_page()

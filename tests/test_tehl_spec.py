import json
from pathlib import Path

from modules.tehl.spec_extractor_matlab import write_spec


def test_tehl_spec_exists_and_has_three_pages() -> None:
    spec_path = Path("src/modules/tehl/ui_spec.yaml")
    write_spec(spec_path)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    assert spec["schema_version"] == "4.0"
    assert len(spec["pages"]) == 3
    assert [page["id"] for page in spec["pages"]] == ["pressures", "film_3d", "thermal"]


def test_each_tehl_page_has_controls_and_plots() -> None:
    spec = json.loads(Path("src/modules/tehl/ui_spec.yaml").read_text(encoding="utf-8"))
    for page in spec["pages"]:
        assert len(page["controls"]) >= 5
        assert len(page["plots"]) >= 3
        assert all("key" in c and "default" in c and "unit" in c for c in page["controls"])
        assert all("kind" in p and "source" in p and "clip_key" in p and "caxis_key" in p for p in page["plots"])

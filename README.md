# pump-suite Stage 8

## 运行与验收
- `python -m tools.validate_spec modules/tehl/spec/ui_spec.yaml`
- `pytest -q modules/tehl/tests/test_spec_load.py`
- `python -m src.app.main`

## 打包（Windows）
- `python build_exe.py --clean`
- `ONECLICK_BUILD_EXE.bat`

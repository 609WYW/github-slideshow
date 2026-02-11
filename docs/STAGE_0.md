# Stage 0 - 项目初始化与资料清点

## 输入资料扫描结果
- 未在仓库中发现 APPD 截图、说明 PDF、MATLAB TEHL App `.m` 文件。
- 扫描命令：`rg --files -g '*.pdf' -g '*.m' -g '*.png' -g '*.jpg'`。
- 当前仅发现 reveal.js 测试图片，不属于 APPD 输入资料。

## Stage 0 目标
1. 初始化 Python/Qt 工程骨架。
2. 建立 UI 文案集中管理机制（中文文案集中于 `src/app/ui_strings/zh_cn.py`）。
3. 建立 TEHL `ui_spec.yaml` 占位文件，记录输入资料缺失状态。
4. 建立最小测试覆盖：项目保存/加载、文案加载、TEHL spec 校验、模块路由。

## Stage 0 阶段清单（本阶段允许修改）
- `pyproject.toml`
- `src/app/**`
- `src/modules/tehl/ui_spec.yaml`
- `tests/**`
- `scripts/ONECLICK_BUILD_EXE.bat`
- `docs/STAGE_0.md`

## 后续阶段入口条件
- 提供 APPD 界面截图、模块 PDF、MATLAB TEHL `.m` 源码后，才能进入像素级对齐实现。

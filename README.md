# APPD（Stage 0）

PySide6 空壳版 APPD 主程序，当前提供：

- 顶部菜单（文件/视图/工具/访问服务器/帮助）
- 两条可显示/隐藏的工具栏（通过“视图(V)”勾选项控制）
- 左侧导航、中央占位页、右侧按钮区占位
- 所有中文文案集中在 `src/app/ui_strings/zh_cn.py`

## 运行

```bash
python -m app.main
```

## 测试

```bash
pytest -q
```

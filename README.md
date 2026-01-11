# 中国A股股票筛选软件（Python 3.11）

本项目是面向中国A股（上交所/深交所/北交所）的批量筛选工具，支持多周期 MACD、EPS 增长、估值、市值、均线条件等配置化筛选，并输出 CSV/Excel/HTML 报告。

## 功能概览

- 多周期 MACD：季度线、月线、周线、日线（默认日线不作为过滤）
- 市值过滤：总市值 < 1000亿人民币（可配置字段口径）
- EPS（季度）环比增长且盈利（允许上一季度为负、本季度转正）
- 均线条件（如 MA20/MA60 排列、股价站上均线）
- 并发筛选、缓存、日志与进度条
- 可选 HTML 报告

## 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 快速运行

```bash
python -m screener run --config config.example.yaml
```

可覆盖参数：

```bash
python -m screener run --config config.example.yaml --max-workers 16 --use-cache false --export csv,xlsx
```

## 配置说明

配置文件为 `config.example.yaml`，其中关键字段：

- `data.provider`: `akshare` / `tushare` / `auto`
- `data.tushare_token`: 若填写则支持使用 Tushare
- `market_cap.field`: 默认 `total_market_cap`，亦可选择 `float_market_cap`
- `macd_filters.enable_daily_filter`: 日线过滤开关（默认关闭）
- `moving_average`: 均线配置与排列关系
- `score_weights`: 评分权重

## 数据源与字段口径

### AkShare（默认）
- 行情：`stock_zh_a_hist`
- 市值：`stock_zh_a_spot_em`（字段包含 `总市值`、`流通市值`）
- 财务：`stock_financial_analysis_indicator`

### Tushare（可选）
- 需要 `tushare_token`
- 市值字段 `total_mv`、`circ_mv` 需要换算（万元 -> 元）

字段映射在代码中实现，位置：
- `screener/data/akshare_provider.py`
- `screener/data/tushare_provider.py`

## 输出

默认输出到 `output/`：

- `screener_results.csv`
- `screener_results.xlsx`
- `screener_results.html`

输出字段包括：
- 代码、名称、市场、总市值
- 季/月/周 MACD（DIF/DEA/HIST）与归一化值
- EPS 最新/上一季度，净利润（如可用）
- MA20/MA60 等均线与过滤结果
- 信号评分（按权重配置）

## 常见问题

1. **AkShare 无法访问**：请确认网络可用，或切换使用 Tushare。
2. **字段缺失**：财务字段缺失时，会自动降级为仅 EPS 过滤。
3. **停牌/退市导致无数据**：工具会跳过该股票而不导致整体崩溃。

## 测试

```bash
pytest
```

## 目录结构

```
.
├── config.example.yaml
├── requirements.txt
├── screener
│   ├── __init__.py
│   ├── __main__.py
│   ├── app
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   └── config.py
│   ├── data
│   │   ├── __init__.py
│   │   ├── akshare_provider.py
│   │   ├── base.py
│   │   ├── cache.py
│   │   └── tushare_provider.py
│   ├── filters
│   │   ├── __init__.py
│   │   ├── financial_filters.py
│   │   ├── macd_filters.py
│   │   ├── ma_filters.py
│   │   └── score.py
│   ├── indicators
│   │   ├── __init__.py
│   │   ├── macd.py
│   │   ├── moving_average.py
│   │   └── resample.py
│   ├── tests
│   │   ├── test_financials.py
│   │   ├── test_macd.py
│   │   └── test_resample.py
│   └── utils
│       ├── logging.py
│       └── symbols.py
```

## 备注

- 本工具仅筛选 A 股：SH/SZ/BJ。
- 日线过滤默认关闭，符合“前三个周期非常好时，日线不用看”的要求。

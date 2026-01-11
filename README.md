# China A-Share Stock Screener

A configurable, multi-timeframe MACD screener for China A-shares (SH/SZ/BJ only). It uses AkShare by default and can switch to Tushare when a token is provided.

## Features
- Quarterly/Monthly/Weekly MACD filters with normalization
- Optional daily filter
- Market cap, EPS, and (optional) net profit checks
- Moving-average convergence/bullish modes
- SQLite-free CSV cache to avoid repeated downloads
- Concurrency, progress bar, structured logging
- CSV/XLSX/HTML export

## Project Structure
```
screener/
  app/           # CLI and orchestration
  data/          # data providers and cache
  indicators/    # MACD, MA, resample
  filters/       # screening rules & scoring
  utils/         # logging and symbol utilities
  tests/         # pytest tests
configs/         # sample config
```

## Windows 11 Setup (CMD/PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip setuptools wheel
pip install -r requirements.txt
```
If you hit build isolation issues, try:
```powershell
pip install --no-build-isolation -r requirements.txt
```

## Usage
```powershell
python -m screener run --config configs/config.example.yaml
```
Optional overrides:
```powershell
python -m screener run --config configs/config.example.yaml --max-workers 6 --use-cache --export csv,xlsx,html --limit 200
```

## Data Providers
- **AkShare (default)**: no token needed.
- **Tushare**: set `provider.name: tushare` and `provider.tushare_token` in config.

## Output
Results are written to `output/` with a timestamp. Each row includes MACD stats, EPS, MA status, and a score.

## Field Notes & Units
- `total_market_cap` and `float_market_cap` are in CNY.
- Tushare market cap is converted from million CNY to CNY.
- EPS is from the latest two quarters; net profit is optional and auto-degrades if unavailable.

## Common Errors
- **Network failures**: rerun, or enable cache.
- **Missing financials**: the screener skips the stock and logs the reason.
- **Permissions**: ensure the virtual env is activated and the cache/output folders are writable.

## Tests
```powershell
pytest
```

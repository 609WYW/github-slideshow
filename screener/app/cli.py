from __future__ import annotations

import argparse
from pathlib import Path

from screener.app.config import load_config
from screener.app.run import run_screen
from screener.utils.logging import setup_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="China A-share stock screener")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Run the screener")
    run_parser.add_argument("--config", required=True, help="Path to config YAML")
    run_parser.add_argument("--max-workers", type=int, default=None)
    run_parser.add_argument("--use-cache", action="store_true")
    run_parser.add_argument("--no-cache", action="store_true")
    run_parser.add_argument("--export", type=str, default=None, help="csv,xlsx,html")
    run_parser.add_argument("--limit", type=int, default=None)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        config = load_config(Path(args.config))
        if args.max_workers is not None:
            config.app.max_workers = args.max_workers
        if args.use_cache:
            config.app.use_cache = True
        if args.no_cache:
            config.app.use_cache = False
        if args.export:
            config.app.export = [item.strip() for item in args.export.split(",") if item.strip()]
        if args.limit is not None:
            config.app.limit = args.limit

        setup_logging(config.app.log_level)
        run_screen(config)


if __name__ == "__main__":
    main()

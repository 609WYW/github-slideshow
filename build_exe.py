from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC_PATH = ROOT / "build" / "appd.spec"
DIST_DIR = ROOT / "dist"
BUILD_DIR = ROOT / "build" / "pyinstaller"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def build(clean: bool) -> None:
    if clean:
        shutil.rmtree(DIST_DIR, ignore_errors=True)
        shutil.rmtree(BUILD_DIR, ignore_errors=True)

    run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--noconfirm",
            "--distpath",
            str(DIST_DIR),
            "--workpath",
            str(BUILD_DIR),
            str(SPEC_PATH),
        ]
    )


def self_test_exe() -> int:
    exe_path = DIST_DIR / "APPD" / ("APPD.exe" if sys.platform.startswith("win") else "APPD")
    if not exe_path.exists():
        print(f"self-test skipped: executable not found at {exe_path}")
        return 1

    cmd = [str(exe_path), "--self-test"]
    print("+", " ".join(cmd))
    completed = subprocess.run(cmd, check=False)
    return completed.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build APPD executable via PyInstaller")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--skip-self-test", action="store_true")
    args = parser.parse_args(argv)

    try:
        build(clean=args.clean)
    except subprocess.CalledProcessError as exc:
        print(f"build failed: {exc}")
        return 1

    if args.skip_self_test:
        return 0

    return self_test_exe()


if __name__ == "__main__":
    raise SystemExit(main())

@echo off
setlocal enabledelayedexpansion

echo [APPD] One-click build started.

where pyinstaller >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  echo [APPD] Using PyInstaller...
  pyinstaller --noconfirm --name APPD --windowed --paths src src\app\main.py
  if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
  echo [APPD] Output: dist\APPD\APPD.exe
  exit /b 0
)

where nuitka >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  echo [APPD] PyInstaller unavailable. Fallback to Nuitka...
  python -m nuitka --standalone --windows-console-mode=disable --output-dir=dist --output-filename=APPD.exe src\app\main.py
  if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%
  echo [APPD] Output under dist\
  exit /b 0
)

echo [APPD] No supported builder found. Please install PyInstaller or Nuitka.
exit /b 1

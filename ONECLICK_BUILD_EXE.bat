@echo off
setlocal
python build_exe.py --clean
if errorlevel 1 (
  echo Build failed.
  exit /b 1
)

echo Running executable self-test...
if exist dist\APPD\APPD.exe (
  dist\APPD\APPD.exe --self-test
  exit /b %errorlevel%
) else (
  echo dist\APPD\APPD.exe not found
  exit /b 1
)

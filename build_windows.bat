@echo off
setlocal

cd /d "%~dp0"

python -m pip install --upgrade pip
python -m pip install pyinstaller

python -m PyInstaller --clean --noconfirm --noconsole --onefile --name AutoDance app.py

if exist "dist\\AutoDance.exe" (
  echo.
  echo Build complete. Run dist\\AutoDance.exe
) else (
  echo.
  echo Build failed: dist\\AutoDance.exe not found.
  exit /b 1
)

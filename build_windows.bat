@echo off
setlocal

cd /d "%~dp0"

python -m pip install --upgrade pip
python -m pip install pyinstaller
python -m pip install opencv-python pillow imutils keyboard mss pywinauto pywin32

python -m PyInstaller --clean --noconfirm --noconsole --onefile --name AutoDance app.py ^
  --log-level=DEBUG > build_log.txt 2>&1

if exist "dist\\AutoDance.exe" (
  echo.
  echo Build complete. Run dist\\AutoDance.exe
) else (
  echo.
  echo Build failed: dist\\AutoDance.exe not found.
  echo Check build_log.txt for details.
  exit /b 1
)

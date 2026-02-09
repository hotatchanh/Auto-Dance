@echo off
setlocal

python -m pip install --upgrade pip
python -m pip install pyinstaller

pyinstaller --noconsole --onefile --name AutoDance app.py

echo.
echo Build complete. Run dist\AutoDance.exe

@echo off
echo Installing requirements...
python -m pip install -r requirements.txt
echo Building executable using PyInstaller...
python -m PyInstaller --onefile --clean --name PRN_spa PRN_analyzer.py
echo.
echo Executable built successfully!
echo You can run the application from dist\PRN_spa.exe

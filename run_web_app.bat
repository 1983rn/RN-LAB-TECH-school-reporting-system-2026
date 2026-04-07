@echo off
echo ===============================================
echo  RN_LAB_TECH Progress Reporting System - Web Version
echo  Created by: RN_LAB_TECH
echo ===============================================
echo.
echo Installing required packages...

REM Check for virtual environment and create if not present
IF NOT EXIST .venv\Scripts\activate.bat (
    echo Creating virtual environment...
    python -m venv .venv
    IF %ERRORLEVEL% NEQ 0 (
        echo Failed to create virtual environment. Please ensure Python is installed and in your PATH.
        pause
        exit /b
    )
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

pip install --upgrade pip
pip install -r requirements.txt
echo.
echo Starting web application...
echo.
echo Open your browser and go to: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
python start_app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Application failed to start. Check the error messages above.
    echo.
)
pause
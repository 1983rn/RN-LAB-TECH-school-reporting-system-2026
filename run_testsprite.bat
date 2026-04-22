@echo off
echo ========================================================
echo Running TestSprite Comprehensive Test Suite (via pytest)
echo ========================================================
echo.
echo Checking and installing pytest dependencies...
pip install pytest pytest-flask
echo.
echo Running tests...
python -m pytest testsprite_tests/ -v
echo.
pause

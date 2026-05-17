@echo off
echo ===================================================
echo Pushing All School Reporting System Changes to GitHub
echo ===================================================
echo.

echo 1. Staging all modifications...
git add .
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to stage changes.
    goto error
)

echo 2. Committing changes...
git commit -m "Fixed missing self._adapt_query() PostgreSQL syntax bug for get_all_marks_for_form and save_student_mark which caused 0 marks found"
if %ERRORLEVEL% neq 0 (
    echo [INFO] No changes to commit or commit failed.
)

echo 3. Pushing changes to GitHub (origin main)...
git push origin main
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to push changes to GitHub.
    goto error
)

echo.
echo ===================================================
echo SUCCESS: All changes successfully pushed to 1983rn/RN-LAB-TECH-school-reporting-system-2026!
echo ===================================================
echo.
pause
exit /b 0

:error
echo.
echo ===================================================
echo FAILURE: An error occurred during git sync operations.
echo ===================================================
echo.
pause
exit /b 1

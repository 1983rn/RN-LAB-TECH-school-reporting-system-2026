@echo off
echo ===============================================
echo  RN_LAB_TECH Subscription Update Script
echo  Updating subscription status for all schools
echo ===============================================
echo.

cd /d "%~dp0"
python update_subscriptions.py

echo.
echo Update completed. Check logs above for details.
pause
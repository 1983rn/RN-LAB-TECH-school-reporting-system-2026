@echo off
echo ========================================
echo NANJATI CDSS TERM 3 DATA RESTORATION
echo ========================================
echo.

echo Checking current database state...
python check_database_state.py
echo.

echo Starting Nanjati CDSS data restoration...
python restore_nanjati_term3_data.py
echo.

echo Verification complete. Check above for results.
echo.
echo Press any key to exit...
pause > nul
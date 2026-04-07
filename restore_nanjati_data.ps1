#!/usr/bin/env powershell

Write-Host "========================================" -ForegroundColor Green
Write-Host "NANJATI CDSS TERM 3 DATA RESTORATION" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Checking current database state..." -ForegroundColor Yellow
try {
    python check_database_state.py
} catch {
    Write-Host "Error running database check: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "Starting Nanjati CDSS data restoration..." -ForegroundColor Yellow
try {
    python restore_nanjati_term3_data.py
} catch {
    Write-Host "Error running restoration: $_" -ForegroundColor Red
}
Write-Host ""

Write-Host "Restoration process complete!" -ForegroundColor Green
Write-Host "You can now login to the system with:" -ForegroundColor Cyan
Write-Host "  Username: nanjati_cdss" -ForegroundColor White
Write-Host "  Password: nanjati2024" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter to exit"
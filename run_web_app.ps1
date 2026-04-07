#!/usr/bin/env powershell
# RN_LAB_TECH Progress Reporting System - Web Application Launcher
# Created by: RN_LAB_TECH

Write-Host "===============================================" -ForegroundColor Green
Write-Host " RN_LAB_TECH Progress Reporting System - Web Version" -ForegroundColor Green
Write-Host " Created by: RN_LAB_TECH" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Check for virtual environment and activate it
if (Test-Path -Path ".\.venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found. Please run setup first." -ForegroundColor Red
    exit 1
}

Write-Host "Installing required packages..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Starting web application..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Open your browser and go to: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

python start_app.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "" 
    Write-Host "❌ Application failed to start. Check the error messages above." -ForegroundColor Red
    Write-Host ""
}

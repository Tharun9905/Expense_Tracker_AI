#!/usr/bin/env pwsh

Write-Host "Starting Expense Tracker AI..." -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Please install Python 3.7+" -ForegroundColor Red
    exit 1
}

# Check if required packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$requiredPackages = @("Flask", "Werkzeug", "Pillow", "pytesseract")
foreach ($package in $requiredPackages) {
    try {
        pip show $package.ToLower() > $null 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ $package is installed" -ForegroundColor Green
        } else {
            Write-Host "✗ $package is missing" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ $package is missing" -ForegroundColor Red
    }
}

# Create data directory if it doesn't exist
if (!(Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" -Force | Out-Null
    Write-Host "✓ Created data directory" -ForegroundColor Green
}

# Start the application
Write-Host ""
Write-Host "Starting Flask application..." -ForegroundColor Green
Write-Host "Access the application at: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

try {
    python app.py
} catch {
    Write-Host "Error starting the application: $_" -ForegroundColor Red
    exit 1
}
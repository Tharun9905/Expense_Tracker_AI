# Tesseract OCR Quick Setup Script
# Run this script as Administrator: Right-click PowerShell > Run as Administrator
# Then: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
# Then: .\QUICK_TESSERACT_SETUP.ps1

Write-Host "================================"
Write-Host "Tesseract-OCR Setup Script"
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "INSTRUCTIONS:"
    Write-Host "1. Right-click on PowerShell"
    Write-Host "2. Select 'Run as Administrator'"
    Write-Host "3. Run: Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process"
    Write-Host "4. Then run this script again"
    exit 1
}

# Check if Tesseract is already installed
Write-Host "Checking if Tesseract is already installed..." -ForegroundColor Yellow
if (Test-Path "C:\Program Files\Tesseract-OCR\tesseract.exe") {
    Write-Host "✅ Tesseract is already installed at C:\Program Files\Tesseract-OCR" -ForegroundColor Green
    & "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
    Write-Host ""
    Write-Host "No need to install. OCR should be working now!" -ForegroundColor Green
    exit 0
}

# Check if Chocolatey is installed
Write-Host "Checking for Chocolatey..." -ForegroundColor Yellow
$chocoCheck = Get-Command choco -ErrorAction SilentlyContinue

if ($chocoCheck) {
    Write-Host "✅ Chocolatey found" -ForegroundColor Green
    Write-Host ""
    Write-Host "Installing Tesseract-OCR with Chocolatey..." -ForegroundColor Yellow
    
    try {
        choco install tesseract -y
        
        # Wait for installation
        Write-Host "Waiting for installation to complete..." -ForegroundColor Yellow
        Start-Sleep -Seconds 30
        
        # Verify installation
        if (Test-Path "C:\Program Files\Tesseract-OCR\tesseract.exe") {
            Write-Host "✅ Tesseract installed successfully!" -ForegroundColor Green
            & "C:\Program Files\Tesseract-OCR\tesseract.exe" --version
            exit 0
        } else {
            Write-Host "❌ Installation appeared to fail. Check C:\Program Files\Tesseract-OCR\" -ForegroundColor Red
            exit 1
        }
    }
    catch {
        Write-Host "❌ Chocolatey installation failed: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Falling back to manual installation..." -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  Chocolatey not found. Using manual installation method." -ForegroundColor Yellow
}

# Manual installation via direct download
Write-Host ""
Write-Host "================================"
Write-Host "Manual Installation Method"
Write-Host "================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "Since automated installation didn't work, please do this manually:"
Write-Host ""
Write-Host "1. Download Tesseract installer from:"
Write-Host "   https://github.com/UB-Mannheim/tesseract/wiki/Downloads"
Write-Host ""
Write-Host "2. Download: tesseract-ocr-w64-setup-v5.x.x.exe (64-bit)"
Write-Host "   or tesseract-ocr-w32-setup-v5.x.x.exe (32-bit)"
Write-Host ""
Write-Host "3. Run the installer with these settings:"
Write-Host "   - Install location: C:\Program Files\Tesseract-OCR"
Write-Host "   - Install language data: YES (at least English)"
Write-Host ""
Write-Host "4. After installation, restart PowerShell and this script will verify it"
Write-Host ""
Write-Host "Or use the direct download link:"
Write-Host "https://github.com/UB-Mannheim/tesseract/releases"
Write-Host ""
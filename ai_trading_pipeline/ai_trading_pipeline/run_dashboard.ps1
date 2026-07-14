# run_dashboard.ps1
# PowerShell script to start the Trading Dashboard with Bot
# Usage: .\run_dashboard.ps1

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  AI Trading Dashboard - Startup Script                         ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Get the Python executable path
$PYTHON_PATH = "C:\Users\$env:USERNAME\AppData\Local\Microsoft\WindowsApps\python.exe"

# Check if Python exists
if (!(Test-Path $PYTHON_PATH)) {
	Write-Host "❌ Error: Python not found at $PYTHON_PATH" -ForegroundColor Red
	Write-Host "Please ensure Python is installed from the Microsoft Store." -ForegroundColor Yellow
	Read-Host "Press Enter to exit"
	exit 1
}

Write-Host "✓ Python found: $PYTHON_PATH" -ForegroundColor Green

# Check if we're in the right directory
if (!(Test-Path "ai_trading_pipeline.py")) {
	Write-Host "❌ Error: Not in correct directory" -ForegroundColor Red
	Write-Host "Please run this script from: ai_trading_pipeline\ai_trading_pipeline\" -ForegroundColor Yellow
	Read-Host "Press Enter to exit"
	exit 1
}

Write-Host "✓ Directory verified`n" -ForegroundColor Green

# Check if requirements are installed
Write-Host "Checking dependencies..." -ForegroundColor White
$pip_check = & $PYTHON_PATH -m pip show fastapi 2>&1
if ($LASTEXITCODE -ne 0) {
	Write-Host "`n📦 Installing dependencies...`n" -ForegroundColor Yellow
	& $PYTHON_PATH -m pip install -r requirements.txt
	if ($LASTEXITCODE -ne 0) {
		Write-Host "`n❌ Failed to install dependencies" -ForegroundColor Red
		Read-Host "Press Enter to exit"
		exit 1
	}
}
Write-Host "✓ Dependencies are installed`n" -ForegroundColor Green

# Display startup information
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🚀 STARTING POWELL AI TRADING BOT WITH TRADINGVIEW DASHBOARD" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

Write-Host "📊 Dashboard URL:  " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000" -ForegroundColor Cyan

Write-Host "📡 API Endpoint:   " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8000/api/" -ForegroundColor Cyan

Write-Host "🔌 WebSocket:      " -NoNewline -ForegroundColor White
Write-Host "ws://localhost:8000/ws/stream" -ForegroundColor Cyan

Write-Host "`n📝 Logs:" -ForegroundColor White
Write-Host "   • Bot trading signals and status" -ForegroundColor Gray
Write-Host "   • API server logs" -ForegroundColor Gray
Write-Host "   • Chart update confirmations" -ForegroundColor Gray

Write-Host "`n⏹️  To stop: Press Ctrl+C`n" -ForegroundColor Yellow

Write-Host "════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Run the bot
& $PYTHON_PATH ai_trading_pipeline.py

if ($LASTEXITCODE -eq 0) {
	Write-Host "`n✓ Bot shut down normally" -ForegroundColor Green
} else {
	Write-Host "`n❌ Bot exited with error (code: $LASTEXITCODE)" -ForegroundColor Red
}

Read-Host "Press Enter to exit"

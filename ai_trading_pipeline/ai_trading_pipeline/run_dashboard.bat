@REM run_dashboard.bat
@REM Windows batch script to start the Trading Dashboard with Bot
@REM Usage: Double-click this file to start everything

@echo off
setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║  AI Trading Dashboard - Startup Script                         ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Get the Python executable path
set PYTHON_PATH=C:\Users\%USERNAME%\AppData\Local\Microsoft\WindowsApps\python.exe

REM Check if Python exists
if not exist "!PYTHON_PATH!" (
	echo ❌ Error: Python not found at !PYTHON_PATH!
	echo Please ensure Python is installed and accessible from the Windows Store.
	pause
	exit /b 1
)

echo ✓ Python found: !PYTHON_PATH!
echo.

REM Check if we're in the right directory
if not exist "ai_trading_pipeline.py" (
	echo ❌ Error: Not in correct directory
	echo Please run this script from: C:\Users\%USERNAME%\source\repos\ai_trading_pipeline\ai_trading_pipeline\
	pause
	exit /b 1
)

echo ✓ Directory verified
echo.

REM Check if requirements are installed
echo Checking dependencies...
"!PYTHON_PATH!" -m pip show fastapi >nul 2>&1
if errorlevel 1 (
	echo.
	echo 📦 Installing dependencies...
	"!PYTHON_PATH!" -m pip install -r requirements.txt
	if errorlevel 1 (
		echo ❌ Failed to install dependencies
		pause
		exit /b 1
	)
)
echo ✓ Dependencies are installed
echo.

REM Display startup information
echo ════════════════════════════════════════════════════════════════
echo 🚀 STARTING POWELL AI TRADING BOT WITH TRADINGVIEW DASHBOARD
echo ════════════════════════════════════════════════════════════════
echo.
echo 📊 Dashboard URL:  http://localhost:8000
echo 📡 API Endpoint:   http://localhost:8000/api/
echo 🔌 WebSocket:      ws://localhost:8000/ws/stream
echo.
echo 📝 Logs:
echo   • Bot trading signals and status
echo   • API server logs
echo   • Chart update confirmations
echo.
echo ⏹️  To stop: Press Ctrl+C
echo.
echo ════════════════════════════════════════════════════════════════
echo.

REM Run the bot
"!PYTHON_PATH!" ai_trading_pipeline.py

if errorlevel 1 (
	echo.
	echo ❌ Bot exited with error
	pause
	exit /b 1
) else (
	echo.
	echo ✓ Bot shut down normally
	pause
	exit /b 0
)

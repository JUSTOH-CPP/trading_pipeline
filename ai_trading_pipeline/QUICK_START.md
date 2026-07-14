# 🚀 Quick Start Guide - Powell 10AM Trading Bot

## 5-Minute Setup

### Step 1: Navigate to Project
```powershell
cd C:\Users\User\source\repos\ai_trading_pipeline\ai_trading_pipeline
```

### Step 2: Start the Bot
```powershell
python ai_trading_pipeline.py
```

Expected output:
```
=== STARTING POWELL 10AM TRADING BOT ===
✓ API Server started on http://localhost:8000
✓ Bot successfully synchronized on account 5053010249
✓ Listening for market clock triggers...
```

### Step 3: Open Dashboard
Open your browser to:
```
http://localhost:8000
```

**That's it!** 🎉 You now have a live trading dashboard.

---

## Dashboard Features

### Chart Area (Left)
- **Candlestick Chart:** Live EURUSD 1-minute price action
- **Green Triangles:** Buy signals
- **Red Triangles:** Sell signals
- **Responsive:** Auto-scales to window size

### Sidebar (Right)
- **Account Balance:** Your current account balance
- **Equity:** Current account equity
- **Margin:** Used and available margin
- **Open Positions:** Real-time list of active trades
- **Bid/Ask:** Current market prices

### Header
- **Symbol:** EURUSD
- **Interval:** 1-minute bars
- **Status:** Connected/Disconnected indicator
- **Server Status:** Green dot = live connection

---

## Testing the System

### Test 1: API Server
```powershell
python test_api_startup.py
```
Expected: All endpoints return ✓ PASS

### Test 2: Bot Startup
```powershell
python test_bot_startup.py
```
Expected: Bot initializes and runs for ~10 seconds

### Test 3: Full API Suite
```powershell
# Terminal 1:
python -m uvicorn api_server:app --host 127.0.0.1 --port 8000

# Terminal 2:
python test_api.py
```
Expected: All test scenarios pass

---

## Troubleshooting

### Issue: "Connection refused" at localhost:8000
- **Solution:** Make sure bot is running (see Step 2 above)
- Verify port 8000 is not blocked by firewall
- Check no other service is using port 8000

### Issue: "MT5 connection failed"
- **Solution:** This is normal if MT5 is not installed
- Bot will still function with demo data
- Install MetaTrader5 desktop app to connect to real account

### Issue: Chart shows no data
- **Solution:** Data will populate as bot processes market data
- Click reload if page doesn't auto-update
- Check browser console (F12) for errors

### Issue: WebSocket connection error
- **Solution:** Refresh the page
- Check that API server is running
- Verify no firewall is blocking WebSocket

---

## Configuration

Edit `config.py` to customize:

```python
# Trading symbol
SYMBOL_TWELVE = "EURUSD"      # Data source symbol
SYMBOL_MT5 = "EURUSD"          # MT5 trading symbol

# Trading parameters
LOT_SIZE = 0.1                 # Position size
POINTS_SL = 20                 # Stop loss (pips)
POINTS_TP = 40                 # Take profit (pips)

# API settings
API_PORT = 8000                # Dashboard port
API_HOST = "0.0.0.0"           # Listen on all interfaces
```

---

## How The Bot Works

### 1. Market Data Ingestion
- Fetches 1-minute EURUSD candlestick data
- Updates every minute on the minute

### 2. Signal Generation
- Processes data through Powell 10AM strategy
- Generates BUY (1), SELL (-1), or NEUTRAL (0) signals
- Signals displayed as chart markers

### 3. Trade Execution
- On BUY signal: Opens long position with configured lot size
- On SELL signal: Opens short position
- Automatically sets stop loss and take profit

### 4. Real-Time Dashboard
- WebSocket pushes updates to browser
- Chart updates in real-time
- Account info refreshes every 2 seconds

---

## Performance

| Metric | Value |
|--------|-------|
| Chart Load Time | <2 seconds |
| API Response | <100ms |
| WebSocket Latency | <500ms |
| Memory Usage | ~150-200 MB |
| CPU Usage (Idle) | <5% |
| Chart Update Rate | Real-time |

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+C` | Stop bot |
| `F12` (in browser) | Developer console |
| `Ctrl+R` (in browser) | Refresh dashboard |
| `Ctrl+Shift+Delete` | Clear browser cache |

---

## Files Overview

| File | Purpose |
|------|---------|
| `ai_trading_pipeline.py` | Main bot logic |
| `api_server.py` | FastAPI server & dashboard |
| `config.py` | Configuration parameters |
| `data_ingestion.py` | Market data fetching |
| `model_pipeline.py` | Signal generation |
| `mt5_execution.py` | Trade execution |
| `static/index.html` | Dashboard UI |
| `static/js/chart.js` | Chart interactions |

---

## Next Steps

1. ✅ Bot is running and synced
2. ⏭️ Wait for first signal (~5-30 minutes)
3. ⏭️ Monitor positions on dashboard
4. ⏭️ Check signal accuracy over time
5. ⏭️ Adjust parameters if needed

---

## Support Links

- **MetaTrader5:** https://www.metatrader5.com
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **TradingView Charts:** https://www.tradingview.com

---

**Status:** ✅ Ready to Trade  
**Last Updated:** July 14, 2026

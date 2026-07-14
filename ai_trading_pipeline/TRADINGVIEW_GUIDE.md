# TradingView Integration Guide

## Overview

Your AI Trading Pipeline now includes a fully integrated **TradingView Lightweight Charts** dashboard that displays real-time candlestick charts, trading signals, account information, and open positions.

## Architecture

```
┌─────────────────────────────┐
│   MetaTrader 5 Terminal     │
│   (Live Market Data)        │
└──────────────┬──────────────┘
			   │
			   ▼
┌──────────────────────────────────────────┐
│   Main Trading Bot                       │
│   (ai_trading_pipeline.py)               │
│   • Fetches data from MT5                │
│   • Generates trading signals            │
│   • Executes trades                      │
└──────────────┬──────────────────────────┘
			   │
	   ┌───────┴───────┐
	   │               │
	   ▼               ▼
┌─────────────┐  ┌─────────────────────────────┐
│Data Cache   │  │FastAPI Server               │
│(Thread-safe)│  │(api_server.py)              │
│ • Candles   │  │ • REST Endpoints            │
│ • Signals   │  │ • WebSocket Streaming       │
└─────────────┘  │ • Static File Serving       │
	   ▲         └─────────────┬───────────────┘
	   │                       │
	   └───────────────────────┘
				   │
				   ▼
		┌──────────────────────────┐
		│ Web Browser              │
		│ (Dashboard Frontend)     │
		│ • TradingView Charts     │
		│ • Account Stats          │
		│ • Open Positions         │
		│ • Signal Notifications   │
		└──────────────────────────┘
```

## Installation

### 1. Install Additional Dependencies

The dependencies have been updated to include `uvicorn` and `websockets`. Install them:

```bash
cd ai_trading_pipeline
pip install -r requirements.txt
```

### 2. Project Structure

Your project now includes:

```
ai_trading_pipeline/
├── api_server.py              # FastAPI server with REST endpoints
├── data_cache.py              # Thread-safe data caching layer
├── test_api.py                # API testing script
├── ai_trading_pipeline.py     # Main trading bot (modified)
├── data_ingestion.py          # Data fetching module
├── model_pipeline.py          # Signal generation
├── mt5_execution.py           # Trade execution
├── config.py                  # Configuration
├── requirements.txt           # Dependencies (updated)
└── static/
	├── index.html             # Dashboard HTML
	└── js/
		└── chart.js           # TradingView chart logic
```

## Usage

### Option 1: Run Bot with Dashboard (Recommended)

This starts both the trading bot and the API server:

```bash
cd ai_trading_pipeline
python ai_trading_pipeline.py
```

Output:
```
=== STARTING POWELL 10AM TRADING BOT ===
✓ API Server started on http://localhost:8000
Bot successfully synchronized on account 12345678.
Listening for market clock triggers...
```

Then open your browser and navigate to: **http://localhost:8000**

### Option 2: Run API Server Separately

If you want to run just the API server (without the trading bot):

```bash
cd ai_trading_pipeline
python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

Then navigate to: **http://localhost:8000**

### Option 3: Run Bot Without Dashboard

To disable the API server and run the bot standalone:

Edit `ai_trading_pipeline.py` and change:
```python
if __name__ == "__main__":
	run_automated_bot(enable_api=False)  # Disable API
```

## Dashboard Features

### 1. **Header**
- **Symbol Display**: Current trading symbol (e.g., EURUSD)
- **Live Bid/Ask**: Current market prices with spread
- **Server Status**: Indicates if dashboard is connected to bot

### 2. **Main Chart Area**
- **Candlestick Chart**: Full OHLCV data with TradingView rendering
- **Buy Signals**: Green triangle markers below candles
- **Sell Signals**: Red triangle markers above candles
- **Interactive Controls**:
  - Drag to pan
  - Scroll to zoom
  - Hover for price tooltip
  - Double-click to reset zoom

### 3. **Right Sidebar**

#### Account Section
- **Balance**: Total account balance
- **Equity**: Current account equity
- **P&L**: Profit/Loss (color-coded: green/red)
- **Margin Used**: Current margin usage percentage

#### Open Positions Section
- **Symbol**: Trading pair
- **Type**: BUY or SELL
- **Size**: Position volume
- **Entry Price**: Open price
- **Current Price**: Market price
- **P&L**: Position profit/loss

#### Recent Signals Section
- **Signal Type**: BUY or SELL
- **Time**: Signal generation time
- **Price**: Price at which signal was generated

### 4. **Real-Time Updates**
- Chart updates every second with new candles
- Positions update every 2 seconds
- Account stats update every 2 seconds
- Bid/Ask prices update every 1 second
- WebSocket notifications for new signals

## API Endpoints

### REST Endpoints

#### Get Chart Data
```bash
GET /api/chart-data
```

Response:
```json
{
  "candles": [
	{
	  "time": 1704067200,
	  "open": 1.0945,
	  "high": 1.0950,
	  "low": 1.0940,
	  "close": 1.0948,
	  "volume": 1500
	}
  ],
  "signals": [
	{
	  "time": 1704067200,
	  "signal": 1,
	  "price": 1.0948
	}
  ],
  "symbol": "EURUSD",
  "interval": "1min"
}
```

#### Get Account Info
```bash
GET /api/account-info
```

Response:
```json
{
  "login": 12345678,
  "balance": 10000.50,
  "equity": 10050.25,
  "profit": 50.25,
  "margin": 500.00,
  "margin_free": 9500.00,
  "currency": "USD"
}
```

#### Get Open Positions
```bash
GET /api/positions
```

Response:
```json
[
  {
	"ticket": 987654321,
	"symbol": "EURUSD",
	"type": "BUY",
	"volume": 0.5,
	"open_price": 1.0940,
	"current_price": 1.0948,
	"profit": 4.00,
	"sl": 1.0925,
	"tp": 1.0980
  }
]
```

#### Get Symbol Tick
```bash
GET /api/symbol-tick
```

Response:
```json
{
  "bid": 1.0948,
  "ask": 1.0950,
  "last": 1.0949,
  "volume": 5000,
  "time": 1704067200
}
```

### WebSocket Streaming

Connect to `ws://localhost:8000/ws/stream` for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/stream');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'update') {
	// Handle real-time candle/signal updates
	console.log('New candles:', data.candles);
	console.log('New signals:', data.signals);
  }
};
```

## Testing

### Run API Tests

```bash
cd ai_trading_pipeline
python test_api.py
```

This will test:
- ✓ Chart data endpoint
- ✓ Account info endpoint
- ✓ Positions endpoint
- ✓ Symbol tick endpoint
- ✓ Static file serving
- ✓ WebSocket connection

Expected output:
```
╔════════════════════════════════════════════════════════════════╗
║      AI Trading Dashboard - API Endpoint Test Suite             ║
╚════════════════════════════════════════════════════════════════╝

✓ PASS | Status Code 200
✓ PASS | Valid JSON Response
✓ PASS | Has 'candles' field
✓ PASS | Has 'signals' field
...

All tests passed! (6/6)

✅ Dashboard available at: http://localhost:8000
📊 WebSocket updates available at: ws://localhost:8000/ws/stream
```

## Configuration

### Dashboard Settings

Edit the JavaScript in `static/js/chart.js` to customize:

```javascript
// Update frequency (milliseconds)
setInterval(fetchAccountInfo, 2000);  // Account every 2 seconds
setInterval(fetchOpenPositions, 2000); // Positions every 2 seconds
setInterval(fetchSymbolTick, 1000);    // Bid/Ask every 1 second

// Maximum signals to display
const MAX_SIGNALS_DISPLAY = 5;

// Chart settings
chart = LightweightCharts.createChart(container, {
	// ... customize layout, colors, grid, etc.
});
```

### API Server Settings

Edit `ai_trading_pipeline.py` to customize:

```python
# Disable API server
run_automated_bot(enable_api=False)

# Change API host/port (currently 0.0.0.0:8000)
# Edit in ai_trading_pipeline.py:
api_thread = threading.Thread(
	target=api_server.run_api_server, 
	kwargs={"host": "0.0.0.0", "port": 8000},  # Change here
	daemon=True
)
```

## Data Cache Management

The data cache automatically:
- ✓ Keeps last 500 candlesticks in memory
- ✓ Keeps last 100 signals in memory
- ✓ Validates data freshness (60-second TTL)
- ✓ Thread-safe operations for concurrent access
- ✓ Automatic deduplication of candles

## Troubleshooting

### Issue: Dashboard Won't Load

1. **Check API server is running**
   ```bash
   curl http://localhost:8000/api/chart-data
   ```

2. **Check firewall**: Port 8000 and WebSocket must be accessible

3. **Check browser console** (F12) for JavaScript errors

### Issue: No Chart Data Displaying

1. **Verify MT5 connection**: Check bot console output shows "successfully synchronized"

2. **Check data cache**: Call `/api/chart-data` directly to see cached data

3. **Verify data is flowing**: Bot should print updates like:
   ```
   [14:30:45] Checked Bar: 2024-01-01 14:30:00 | Close: 1.0945 | Signal: 0
   ```

### Issue: Positions Not Updating

1. **Check MT5 positions**: Open positions should be visible in MT5 terminal

2. **Verify account access**: Some accounts may have restricted position queries

3. **Check API logs**: Monitor browser DevTools Network tab for failed requests

### Issue: WebSocket Not Connecting

1. **Check browser console**: Should show connection attempt

2. **Firewall**: Ensure WebSocket port (8000) is not blocked

3. **Protocol**: Use `ws://` for HTTP, `wss://` for HTTPS

## Performance Considerations

- **Chart Rendering**: TradingView Lightweight Charts is very efficient; can handle millions of candles
- **WebSocket Updates**: Updates broadcast to all connected clients; monitor with many users
- **Data Cache**: Limited to 500 candles and 100 signals in memory
- **API Latency**: Typically <10ms for REST endpoints
- **WebSocket Latency**: Typically <50ms for real-time updates

## Advanced: Deploying to Cloud

For cloud deployment (AWS, Azure, etc.):

1. **Update CORS settings** in `api_server.py`:
   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
	   CORSMiddleware,
	   allow_origins=["*"],  # Restrict in production
	   allow_credentials=True,
	   allow_methods=["*"],
	   allow_headers=["*"],
   )
   ```

2. **Run with production server** (instead of uvicorn):
   ```bash
   pip install gunicorn
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_server:app
   ```

3. **Use HTTPS/WSS** with reverse proxy (nginx)

4. **Environment variables** for sensitive data:
   ```python
   import os
   API_PORT = os.getenv("API_PORT", 8000)
   ```

## Support & Customization

The dashboard is fully customizable:

- **Modify colors**: Edit CSS in `static/index.html`
- **Add indicators**: Use TradingView Lightweight Charts API in `static/js/chart.js`
- **Change layout**: Modify grid structure in HTML/CSS
- **Add new endpoints**: Extend `api_server.py` with additional routes

## Next Steps

1. ✓ Install requirements
2. ✓ Start bot with API server
3. ✓ Open dashboard at http://localhost:8000
4. ✓ Monitor trades and signals in real-time
5. ✓ Test API endpoints with `test_api.py`
6. ✓ Customize dashboard appearance and settings
7. ✓ Deploy to cloud if needed

Enjoy your interactive trading dashboard! 🚀📈

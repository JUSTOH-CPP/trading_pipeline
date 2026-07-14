# QUICKSTART.md
# TradingView Dashboard - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd ai_trading_pipeline
pip install -r requirements.txt
```

### Step 2: Start the Trading Bot with Dashboard
```bash
python ai_trading_pipeline.py
```

You should see:
```
=== STARTING POWELL 10AM TRADING BOT ===
✓ API Server started on http://localhost:8000
Bot successfully synchronized on account 12345678.
Listening for market clock triggers...
[14:30:45] Checked Bar: 2024-01-01 14:30:00 | Close: 1.0945 | Signal: 0
```

### Step 3: Open Dashboard
Open your web browser and navigate to:
```
http://localhost:8000
```

## 📊 What You'll See

The dashboard displays:

1. **Live Candlestick Chart** (center)
   - Real-time price action with OHLC candles
   - Green candles = prices going up
   - Red candles = prices going down
   - Green ▲ triangles = BUY signals
   - Red ▼ triangles = SELL signals

2. **Account Information** (right sidebar, top)
   - Balance: Your account balance
   - Equity: Current account value
   - P&L: Profit/Loss (green = profit, red = loss)
   - Margin Used: How much margin you're using

3. **Open Positions** (right sidebar, middle)
   - Lists all active trades
   - Shows entry price, current price, and P&L for each trade
   - Clicking a position shows detailed info

4. **Recent Signals** (right sidebar, bottom)
   - Last 5 trading signals generated
   - Shows timestamp and price

## 🎮 Interacting with the Chart

- **Zoom In/Out**: Scroll mouse over chart
- **Pan Left/Right**: Click and drag on chart
- **Reset View**: Double-click on chart
- **Tooltip**: Hover over a candle to see OHLC details
- **Crosshair**: Shows current price level as you move mouse

## 🔄 Real-Time Updates

Dashboard updates automatically:
- ✓ Chart updates every new candle (1 minute)
- ✓ Account stats update every 2 seconds
- ✓ Positions update every 2 seconds
- ✓ Bid/Ask prices update every 1 second
- ✓ Signals shown with instant notifications

## 📱 Checking All Endpoints

To verify everything is working, run the test script:
```bash
python test_api.py
```

You should see something like:
```
✓ PASS | Status Code 200
✓ PASS | Valid JSON Response
✓ PASS | Has 'candles' field
✓ PASS | Has 'signals' field
✓ PASS | Candle structure valid
...

All tests passed! (6/6)
```

## 🌐 API Endpoints (For Advanced Users)

The dashboard uses these API endpoints:
- `/api/chart-data` - Get candlestick and signal data
- `/api/account-info` - Get account statistics
- `/api/positions` - Get open positions
- `/api/symbol-tick` - Get current bid/ask prices
- `/ws/stream` - WebSocket for real-time updates

## ⚙️ Configuration

### Change Trading Symbol

Edit `config.py`:
```python
ASSET_CLASS = "FOREX"  # or "INDEX"
```

### Change API Port

Edit `ai_trading_pipeline.py`:
```python
kwargs={"host": "0.0.0.0", "port": 8000}  # Change port here
```

### Enable/Disable Dashboard

To run bot WITHOUT dashboard:
```python
run_automated_bot(enable_api=False)
```

## 🐛 Troubleshooting

### Dashboard won't load?
1. Check bot is running (should see "✓ API Server started" message)
2. Try `http://localhost:8000` in your browser
3. Check firewall isn't blocking port 8000
4. Open browser DevTools (F12) and check console for errors

### No chart data?
1. Wait for first signal/candle update (within 1 minute)
2. Check MT5 terminal is running and connected
3. Call `/api/chart-data` directly to see if data is cached

### Positions not showing?
1. Open a position in MT5 terminal first
2. Check you have permission to view positions on your account
3. Refresh browser page (F5)

### WebSocket not connecting?
1. Check browser console for errors
2. Ensure you're not behind a restrictive firewall
3. Try disabling browser extensions that might interfere

## 📚 Full Documentation

For detailed documentation, see `TRADINGVIEW_GUIDE.md`

This includes:
- Full architecture overview
- All API endpoint specifications
- Advanced customization options
- Cloud deployment instructions
- Performance tuning

## 💡 Tips & Tricks

1. **Monitor Signals**: Look for green ▲ (BUY) and red ▼ (SELL) markers on chart
2. **Check P&L**: Green account stats mean you're profitable
3. **Position Size**: Watch the "Size" column to see your exposure
4. **Market Hours**: Signals only generate during trading hours (17:00 Nairobi Time)
5. **Spread**: Watch the bid/ask spread - wider spread means less liquidity

## 🎯 Next Steps

1. ✓ Dashboard is running
2. ✓ Monitoring price action in real-time
3. ✓ Seeing trading signals as they generate
4. ✓ Tracking account performance
5. Optional: Deploy to cloud for remote access
6. Optional: Customize dashboard appearance

## 📞 Support

If you encounter issues:
1. Check TRADINGVIEW_GUIDE.md Troubleshooting section
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Ensure MT5 terminal is running in background
4. Check that no other service uses port 8000

---

**Happy Trading! 📈🚀**

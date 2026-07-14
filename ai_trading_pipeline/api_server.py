# api_server.py
"""
FastAPI server for serving chart data and real-time trading signals to the frontend.
This runs in parallel with the main trading bot.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict
import pandas as pd
import json
import asyncio
from datetime import datetime
import threading
from queue import Queue
import data_ingestion
import model_pipeline
import config
import data_cache
import MetaTrader5 as mt5

# Global state management
app = FastAPI(title="Trading Dashboard API")

# Mount static files BEFORE defining routes
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    print(f"Warning: Could not mount static files: {e}")

# Data cache
class CandleData(BaseModel):
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: int

class SignalData(BaseModel):
    time: int
    signal: int  # 1 for BUY, -1 for SELL, 0 for NEUTRAL
    price: float

class ChartDataResponse(BaseModel):
    candles: List[CandleData]
    signals: List[SignalData]
    symbol: str
    interval: str

# Shared data structures (thread-safe through external queue)
latest_data = {
    "candles": [],
    "signals": [],
    "last_update": None,
    "symbol": config.SYMBOL_MT5,
    "interval": config.INTERVAL
}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")

manager = ConnectionManager()

# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Serve the main dashboard HTML file"""
    return FileResponse("static/index.html", media_type="text/html")

@app.get("/api/chart-data", response_model=ChartDataResponse)
async def get_chart_data():
    """
    Returns the latest candlestick data and trading signals for chart rendering.
    Uses cached data for efficiency.
    """
    cache = data_cache.get_cache()
    metadata = cache.get_metadata() or {}
    return ChartDataResponse(
        candles=[CandleData(**candle) for candle in cache.get_candles(limit=500)],
        signals=[SignalData(**signal) for signal in cache.get_signals(limit=50)],
        symbol=metadata.get("symbol") or config.SYMBOL_MT5,
        interval=metadata.get("interval") or config.INTERVAL
    )

@app.get("/api/account-info")
async def get_account_info():
    """
    Returns MT5 account information (balance, equity, etc.)
    """
    account_info = mt5.account_info()
    if account_info:
        return {
            "login": account_info.login,
            "balance": account_info.balance,
            "equity": account_info.equity,
            "profit": account_info.profit,
            "margin": account_info.margin,
            "margin_free": account_info.margin_free,
            "currency": account_info.currency
        }
    return {"error": "MT5 not initialized"}

@app.get("/api/positions")
async def get_open_positions():
    """
    Returns all open positions in the MT5 account
    """
    positions = mt5.positions_get()
    if positions:
        return [
            {
                "ticket": pos.ticket,
                "symbol": pos.symbol,
                "type": "BUY" if pos.type == mt5.ORDER_TYPE_BUY else "SELL",
                "volume": pos.volume,
                "open_price": pos.price_open,
                "current_price": pos.price_current,
                "profit": pos.profit,
                "sl": pos.sl,
                "tp": pos.tp
            }
            for pos in positions
        ]
    return []

@app.get("/api/symbol-tick")
async def get_symbol_tick():
    """
    Returns current bid/ask prices for the active symbol
    """
    tick = mt5.symbol_info_tick(config.SYMBOL_MT5)
    if tick:
        return {
            "bid": tick.bid,
            "ask": tick.ask,
            "last": tick.last,
            "volume": tick.volume,
            "time": tick.time
        }
    return {"error": "Unable to fetch tick data"}

# ============================================================================
# WEBSOCKET ENDPOINT FOR REAL-TIME UPDATES
# ============================================================================

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time candlestick and signal updates.
    Clients receive updates as they occur from the trading bot.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            # Echo or process client commands if needed
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# ============================================================================
# DATA UPDATE FUNCTIONS (Called by main bot or background thread)
# ============================================================================

def update_chart_data(df: pd.DataFrame, processed_df: pd.DataFrame):
    """
    Updates the data cache with fresh candles and signals.
    Call this from the main trading bot after fetching new data.

    Args:
        df: Raw dataframe from data_ingestion
        processed_df: Processed dataframe with signals from model_pipeline
    """
    try:
        # Update global cache
        data_cache.update_cache_from_dataframe(
            df, 
            processed_df, 
            symbol=config.SYMBOL_MT5,
            interval=config.INTERVAL
        )

        # Broadcast latest updates to WebSocket clients
        cache = data_cache.get_cache()
        latest_candles = cache.get_candles(limit=5)
        latest_signals = cache.get_signals(limit=1)

        asyncio.create_task(manager.broadcast({
            "type": "update",
            "candles": latest_candles,
            "signals": latest_signals,
            "timestamp": datetime.now().isoformat()
        }))

    except Exception as e:
        print(f"Error updating chart data: {e}")

def sync_data_from_bot(get_data_callback):
    """
    Background task to periodically fetch data from the trading bot.
    Use this if you want the API server to autonomously fetch data.

    Args:
        get_data_callback: Function that returns (raw_df, processed_df) tuple
    """
    while True:
        try:
            raw_df, processed_df = get_data_callback()
            if not raw_df.empty:
                update_chart_data(raw_df, processed_df)
            asyncio.sleep(1)  # Update every 1 second
        except Exception as e:
            print(f"Error in sync_data_from_bot: {e}")
            asyncio.sleep(5)

# ============================================================================
# STARTUP AND SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize MT5 connection on server startup"""
    if not mt5.initialize():
        print("Warning: MT5 could not be initialized on API server startup")
    print("API Server started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on server shutdown"""
    mt5.shutdown()
    print("API Server shutdown")

# ============================================================================
# HELPER FUNCTION TO RUN SERVER
# ============================================================================

def run_api_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Standalone function to run the API server.

    Usage in main bot:
        import threading
        api_thread = threading.Thread(target=api_server.run_api_server, daemon=True)
        api_thread.start()
    """
    import uvicorn
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    # Run the server
    run_api_server(host="0.0.0.0", port=8000)

# data_ingestion.py
import pandas as pd
import MetaTrader5 as mt5
import config

def get_historical_data(symbol: str, interval: str = "1min", outputsize: int = 100) -> pd.DataFrame:
    """
    Fetches historical candle bars directly from the connected MT5 Broker Terminal.
    """
    # Map the interval string to MT5 timeframe constants
    timeframe = mt5.TIMEFRAME_M1 if interval == "1min" else mt5.TIMEFRAME_M1
    
    # Fetch bars from MT5 directly
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, outputsize)
    
    if rates is None or len(rates) == 0:
        print(f"⚠️ MT5 Data Fetch Failed for symbol: {symbol}. Check if symbol is visible in Market Watch.")
        return pd.DataFrame()
        
    # Convert structural rates matrix to Pandas DataFrame
    df = pd.DataFrame(rates)
    
    # MT5 returns time as a Unix timestamp; convert it to an editable datetime object
    df['datetime'] = pd.to_datetime(df['time'], unit='s')
    
    # Rename columns to match what model_pipeline.py expects
    df = df.rename(columns={"open": "open", "high": "high", "low": "low", "close": "close", "tick_volume": "volume"})
    
    # Sort chronologically (oldest to newest)
    df = df.sort_values(by='datetime', ascending=True).reset_index(drop=True)
    
    return df
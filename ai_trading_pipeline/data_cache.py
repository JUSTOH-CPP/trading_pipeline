# data_cache.py
"""
Thread-safe data caching layer for efficient API serving.
Holds the most recent candlestick and signal data.
"""

import threading
from typing import Optional, Dict, List
import pandas as pd
from datetime import datetime, timedelta

class DataCache:
    """Thread-safe cache for candlestick and signal data"""

    def __init__(self, max_candles: int = 500, cache_ttl_seconds: int = 60):
        """
        Initialize the data cache.

        Args:
            max_candles: Maximum candlesticks to keep in memory
            cache_ttl_seconds: Time-to-live for cached data before invalidation
        """
        self._lock = threading.RLock()
        self._candles: List[Dict] = []
        self._signals: List[Dict] = []
        self._last_update: Optional[datetime] = None
        self._max_candles = max_candles
        self._cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self._metadata = {
            "symbol": None,
            "interval": None,
            "total_updates": 0
        }

    def set_candles(self, candles: List[Dict], symbol: str = None, interval: str = None):
        """
        Update candlestick data in cache.

        Args:
            candles: List of candlestick data dicts with keys: time, open, high, low, close, volume
            symbol: Trading symbol (optional)
            interval: Timeframe (optional)
        """
        with self._lock:
            # Remove duplicates by time
            existing_times = {c['time'] for c in self._candles}
            new_candles = [c for c in candles if c['time'] not in existing_times]

            # Append and trim to max size
            self._candles.extend(new_candles)
            self._candles = sorted(self._candles, key=lambda x: x['time'])
            if len(self._candles) > self._max_candles:
                self._candles = self._candles[-self._max_candles:]

            # Update metadata
            if symbol:
                self._metadata["symbol"] = symbol
            if interval:
                self._metadata["interval"] = interval

            self._last_update = datetime.now()
            self._metadata["total_updates"] += 1

    def add_signal(self, time: int, signal: int, price: float):
        """
        Add a trading signal to the cache.

        Args:
            time: Unix timestamp
            signal: 1 for BUY, -1 for SELL, 0 for NEUTRAL
            price: Price at signal generation
        """
        with self._lock:
            # Avoid duplicate signals at same time
            if not any(s['time'] == time for s in self._signals):
                self._signals.append({
                    'time': time,
                    'signal': signal,
                    'price': price
                })

                # Keep recent signals only (last 100)
                if len(self._signals) > 100:
                    self._signals = self._signals[-100:]

    def get_candles(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Retrieve candles from cache.

        Args:
            limit: Max number of candles to return (None for all)

        Returns:
            List of candlestick data
        """
        with self._lock:
            if limit:
                return self._candles[-limit:].copy()
            return self._candles.copy()

    def get_signals(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Retrieve signals from cache.

        Args:
            limit: Max number of signals to return (None for all)

        Returns:
            List of signal data
        """
        with self._lock:
            if limit:
                return self._signals[-limit:].copy()
            return self._signals.copy()

    def get_latest_candle(self) -> Optional[Dict]:
        """Get the most recent candlestick"""
        with self._lock:
            return self._candles[-1].copy() if self._candles else None

    def get_latest_signal(self) -> Optional[Dict]:
        """Get the most recent signal"""
        with self._lock:
            return self._signals[-1].copy() if self._signals else None

    def get_metadata(self) -> Dict:
        """Get cache metadata"""
        with self._lock:
            return {
                **self._metadata,
                "last_update": self._last_update.isoformat() if self._last_update else None,
                "candle_count": len(self._candles),
                "signal_count": len(self._signals)
            }

    def is_valid(self) -> bool:
        """Check if cache has fresh data"""
        with self._lock:
            if not self._last_update:
                return False
            return datetime.now() - self._last_update < self._cache_ttl

    def clear(self):
        """Clear all cached data"""
        with self._lock:
            self._candles.clear()
            self._signals.clear()
            self._last_update = None
            self._metadata["total_updates"] = 0

    def from_dataframe(self, df: pd.DataFrame, symbol: str = None, interval: str = None):
        """
        Load candles from pandas DataFrame.

        Args:
            df: DataFrame with columns: datetime, open, high, low, close, volume
            symbol: Trading symbol (optional)
            interval: Timeframe (optional)
        """
        candles = []
        for _, row in df.iterrows():
            try:
                candle = {
                    'time': int(row['datetime'].timestamp()),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row.get('volume', 0))
                }
                candles.append(candle)
            except Exception as e:
                print(f"Warning: Could not convert candle from DataFrame: {e}")

        self.set_candles(candles, symbol, interval)

    def get_ohlcv_array(self) -> List[Dict]:
        """
        Get OHLCV array format suitable for charting.

        Returns:
            List of dicts with: time, open, high, low, close, volume
        """
        return self.get_candles()


# Global cache instance
_global_cache = DataCache(max_candles=500, cache_ttl_seconds=60)


def get_cache() -> DataCache:
    """Get the global data cache instance"""
    return _global_cache


def update_cache_from_dataframe(raw_df: pd.DataFrame, processed_df: pd.DataFrame, 
                                symbol: str = None, interval: str = None):
    """
    Helper to update global cache from trading bot dataframes.

    Args:
        raw_df: Raw data from data_ingestion
        processed_df: Processed data with signals from model_pipeline
        symbol: Trading symbol (optional)
        interval: Timeframe (optional)
    """
    cache = get_cache()

    # Update candles from processed dataframe
    cache.from_dataframe(processed_df, symbol, interval)

    # Extract and add signals
    if 'powell_signal' in processed_df.columns:
        for _, row in processed_df.iterrows():
            signal = row.get('powell_signal', 0)
            if signal != 0:
                cache.add_signal(
                    time=int(row['datetime'].timestamp()),
                    signal=int(signal),
                    price=float(row['close'])
                )

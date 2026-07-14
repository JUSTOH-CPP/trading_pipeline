# model_pipeline.py
import pandas as pd
import numpy as np

def generate_powell_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes manipulation and structure shifts relative to the 10:00 AM NY Open.
    Synchronized for Nairobi Time (UTC+3) -> NY 10:00 AM occurs at 17:00 Local.
    """
    df = df.copy()
    df['powell_signal'] = 0
    df['hour_min'] = df['datetime'].dt.strftime('%H:%M')
    
    # 1. Lock the NY Open Line using Nairobi Local Time (17:00)
    df['is_10am'] = df['hour_min'] == "17:00"
    df['powell_open_line'] = df.apply(lambda row: row['open'] if row['is_10am'] else np.nan, axis=1)
    df['powell_open_line'] = df['powell_open_line'].ffill()
    
    if df['powell_open_line'].isna().all():
        return df

    # Loop over the dataframe to calculate indicators safely
    for i in range(5, len(df)):
        current_time = df.iloc[i]['datetime']
        
        # 2. Operational Window: Only trade during the 17:00 Nairobi Local Hour (5:01 PM - 5:59 PM)
        if current_time.hour != 17 or current_time.minute == 0:
            continue
            
        open_anchor = df.iloc[i]['powell_open_line']
        if pd.isna(open_anchor):
            continue

        # Look back over a 5-minute rolling window
        window = df.iloc[i-5:i]
        recent_high = window['high'].max()
        recent_low = window['low'].min()
        
        current_close = df.iloc[i]['close']
        current_open = df.iloc[i]['open']
        
        # BULLISH ENTRY: Liquidity swept below open line, followed by a structure break up
        was_below_open = (window['low'] < open_anchor).any()
        mss_bullish = current_close > recent_high
        
        if was_below_open and mss_bullish and current_close > open_anchor:
            if current_close > current_open:
                df.at[df.index[i], 'powell_signal'] = 1
                continue

        # BEARISH ENTRY: Liquidity swept above open line, followed by a structure break down
        was_above_open = (window['high'] > open_anchor).any()
        mss_bearish = current_close < recent_low
        
        if was_above_open and mss_bearish and current_close < open_anchor:
            if current_close < current_open:
                df.at[df.index[i], 'powell_signal'] = -1
                continue
                
    return df
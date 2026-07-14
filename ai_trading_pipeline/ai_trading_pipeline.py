# ai_trading_pipeline.py
import time
import datetime
import config
import data_ingestion
import model_pipeline
import mt5_execution
import MetaTrader5 as mt5
import threading

# Import API server (optional)
try:
    import api_server
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False

# Global cache for API server (thread-safe through queues)
api_data_cache = {
    "raw_df": None,
    "processed_df": None,
    "lock": threading.Lock()
}

def run_automated_bot(enable_api=True):
    print("=== STARTING POWELL 10AM TRADING BOT ===")

    # Start API server in background thread if enabled
    api_thread = None
    if enable_api and API_AVAILABLE:
        try:
            api_thread = threading.Thread(
                target=api_server.run_api_server, 
                kwargs={"host": "0.0.0.0", "port": 8000},
                daemon=True
            )
            api_thread.start()
            print("✓ API Server started on http://localhost:8000")
        except Exception as e:
            print(f"Warning: Could not start API server: {e}")

    if not mt5_execution.initialize_mt5():
        print("Bot startup aborted due to MT5 connection failure.")
        return

    print(f"Bot successfully synchronized on account {mt5.account_info().login if mt5.account_info() else 'Active'}.")
    print("Listening for market clock triggers...")

    last_processed_minute = -1

    try:
        while True:
            current_time = datetime.datetime.now()

            # Run the system sequence precisely at the change of each minute
            if current_time.minute != last_processed_minute:
                last_processed_minute = current_time.minute

                # Fetch data stream
                raw_df = data_ingestion.get_historical_data(
                    symbol=config.SYMBOL_TWELVE, 
                    interval=config.INTERVAL, 
                    outputsize=100
                )

                if not raw_df.empty:
                    # Pass through model pipeline
                    processed_df = model_pipeline.generate_powell_signals(raw_df)

                    # Cache data for API server (thread-safe)
                    with api_data_cache["lock"]:
                        api_data_cache["raw_df"] = raw_df.copy()
                        api_data_cache["processed_df"] = processed_df.copy()

                    # Push data to API server if available
                    if API_AVAILABLE:
                        try:
                            api_server.update_chart_data(raw_df, processed_df)
                        except Exception as e:
                            print(f"Note: API server data sync skipped: {e}")

                    latest_candle = processed_df.iloc[-1]
                    latest_time = latest_candle['datetime'].strftime('%Y-%m-%d %H:%M:%S')
                    latest_signal = latest_candle['powell_signal']

                    # Clean heartbeat log output
                    sys_stamp = current_time.strftime("%H:%M:%S")
                    print(f"[{sys_stamp}] Checked Bar: {latest_time} | Close: {latest_candle['close']} | Signal: {latest_signal}")

                    # Route execution signal if valid
                    if latest_signal == 1 or latest_signal == -1:
                        print(f"🚨 Strategy signal detected! Routing trade to MT5...")
                        mt5_execution.execute_market_order(
                            symbol=config.SYMBOL_MT5,
                            signal=latest_signal,
                            lot_size=config.LOT_SIZE,
                            points_sl=config.POINTS_SL,
                            points_tp=config.POINTS_TP
                        )

            # Low CPU sleep check interval
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nBot execution paused manually by user.")
    finally:
        mt5.shutdown()
        print("MetaTrader 5 connection safely closed.")

if __name__ == "__main__":
    # Run bot with API server enabled (set to False to disable API)
    run_automated_bot(enable_api=True)
    run_automated_bot()
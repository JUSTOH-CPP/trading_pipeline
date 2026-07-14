# test_execution.py
import time
import config
import mt5_execution
import MetaTrader5 as mt5

def run_dry_test():
    print("=== STARTING MT5 BROKER CONNECTIVITY DRY-RUN ===")
    
    # 1. Initialize local desktop engine connection
    if not mt5_execution.initialize_mt5():
        print("❌ Test Aborted: Could not establish a link to the active MT5 Desktop App.")
        return

    print(f"Connected to MT5! Active Account: {mt5.account_info().login if mt5.account_info() else 'Unknown'}")
    
    # 2. Extract current asset settings from your active config.py matrix
    target_symbol = config.SYMBOL_MT5
    test_lots = config.LOT_SIZE
    sl_points = config.POINTS_SL
    tp_points = config.POINTS_TP
    
    print(f"\nAttempting to route a direct validation buy order...")
    print(f"Targeting Asset: {target_symbol} | Size: {test_lots} Lots | SL: {sl_points} pts | TP: {tp_points} pts")
    
    # 3. Force-trigger a direct BUY market order (signal = 1)
    trade_result = mt5_execution.execute_market_order(
        symbol=target_symbol,
        signal=1,  # 1 forces an immediate BUY execution
        lot_size=test_lots,
        points_sl=sl_points,
        points_tp=tp_points
    )
    
    # 4. Handle final verification reporting
    if trade_result and trade_result.retcode == mt5.TRADE_RETCODE_DONE:
        print("\n🎉 CONNECTION TEST SUCCESSFUL!")
        print("Go look at your physical MT5 terminal screen or FundedNext dashboard.")
        print("You should see an open position with your hard stop loss and take profit attached.")
    else:
        print("\n❌ Order failed to clear broker server hardware.")
        
    # Shutdown link safely
    mt5.shutdown()

if __name__ == "__main__":
    run_dry_test()

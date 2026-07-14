# mt5_execution.py
import MetaTrader5 as mt5
import config

def initialize_mt5() -> bool:
    """
    Connects to the desktop MT5 client using config details if provided.
    """
    if mt5.initialize():
        # Authenticate if credentials are set up inside config.py
        if config.MT5_LOGIN and config.MT5_PASSWORD:
            login_success = mt5.login(
                login=config.MT5_LOGIN, 
                password=config.MT5_PASSWORD, 
                server=config.MT5_SERVER
            )
            return login_success
        return True
    return False

def execute_market_order(symbol: str, signal: int, lot_size: float, points_sl: int, points_tp: int):
    """
    Submits a market execution request to the broker server terminal.
    """
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(f"Error: Symbol {symbol} not found.")
        return

    if not symbol_info.visible:
        mt5.symbol_select(symbol, True)

    point = mt5.symbol_info(symbol).point
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return

    if signal == 1:
        order_type = mt5.ORDER_TYPE_BUY
        price = tick.ask
        sl = price - (points_sl * point)
        tp = price + (points_tp * point)
    elif signal == -1:
        order_type = mt5.ORDER_TYPE_SELL
        price = tick.bid
        sl = price + (points_sl * point)
        tp = price - (points_tp * point)
    else:
        return

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 101000,
        "comment": "Powell 10AM Bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC  # Match filling rules for prop firms
    }

    result = mt5.order_send(request)
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        comment = result.comment if result else "No server response"
        print(f"❌ Order Rejected: {comment}")
    else:
        print(f"✅ Order Filled! Ticket: {result.order} at {result.price}")
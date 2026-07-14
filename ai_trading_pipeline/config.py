# Toggle between "FOREX" or "INDEX" to automatically re-configure the bot
ASSET_CLASS = "FOREX"  

# Twelve Data Credentials
TWELVE_DATA_API_KEY = "746a30f11c7a4614b7878680ed13a7e8"

# FundedNext MT5 Demo Account Details 
# (Leave as None if you are already logged into the desktop terminal software)
MT5_LOGIN = None
MT5_PASSWORD = None
MT5_SERVER = None

# Asset Configuration Matrix
ASSET_MATRIX = {
    "FOREX": {
        "SYMBOL_TWELVE": "EURUSD",
        "SYMBOL_MT5": "EURUSD",
        "LOT_SIZE": 0.5,            # Standard currency lot sizing
        "STOP_LOSS_POINTS": 150,    # 15 Pips
        "TAKE_PROFIT_POINTS": 450,  # 45 Pips (1:3 Risk-to-Reward)
    },
    "INDEX": {
        "SYMBOL_TWELVE": "NDX100",     # ETF tracker highly supported on Twelve Data free tiers
        "SYMBOL_MT5": "NDX100",     # FundedNext exact MT5 index contract ticker
        "LOT_SIZE": 1.0,            
        "STOP_LOSS_POINTS": 2500,   # Wide cushion for index volatility
        "TAKE_PROFIT_POINTS": 7500, 
    },
   

}

# Exported runtime variables
ACTIVE_SETTING = ASSET_MATRIX.get(ASSET_CLASS, ASSET_MATRIX["FOREX"])

SYMBOL_TWELVE = ACTIVE_SETTING["SYMBOL_TWELVE"]
SYMBOL_MT5 = ACTIVE_SETTING["SYMBOL_MT5"]
LOT_SIZE = ACTIVE_SETTING["LOT_SIZE"]
POINTS_SL = ACTIVE_SETTING["STOP_LOSS_POINTS"]
POINTS_TP = ACTIVE_SETTING["TAKE_PROFIT_POINTS"]
INTERVAL = "1min"
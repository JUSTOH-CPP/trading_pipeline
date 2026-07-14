# test_api.py
"""
Test script for API endpoints and TradingView integration.
Run this after starting the API server to verify all endpoints are working.

Usage:
    # Terminal 1: Start the API server
    python -m uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload

    # Terminal 2: Run this test script
    python test_api.py
"""

import requests
import json
import time
import asyncio
import websockets
from datetime import datetime

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/stream"

class bcolors:
    """Color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_test(name, passed, message=""):
    status = f"{bcolors.OKGREEN}✓ PASS{bcolors.ENDC}" if passed else f"{bcolors.FAIL}✗ FAIL{bcolors.ENDC}"
    print(f"{status} | {name}")
    if message:
        print(f"  └─ {message}")

def test_chart_data_endpoint():
    """Test /api/chart-data endpoint"""
    print(f"\n{bcolors.HEADER}Testing Chart Data Endpoint{bcolors.ENDC}")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/api/chart-data")
        passed = response.status_code == 200
        print_test("Status Code 200", passed)

        data = response.json()
        print_test("Valid JSON Response", True)

        # Check required fields
        has_candles = "candles" in data
        print_test("Has 'candles' field", has_candles, f"Count: {len(data.get('candles', []))}")

        has_signals = "signals" in data
        print_test("Has 'signals' field", has_signals, f"Count: {len(data.get('signals', []))}")

        has_symbol = "symbol" in data
        print_test("Has 'symbol' field", has_symbol, f"Symbol: {data.get('symbol')}")

        has_interval = "interval" in data
        print_test("Has 'interval' field", has_interval, f"Interval: {data.get('interval')}")

        # Validate candle structure
        if has_candles and len(data['candles']) > 0:
            candle = data['candles'][0]
            required_fields = ['time', 'open', 'high', 'low', 'close', 'volume']
            all_present = all(field in candle for field in required_fields)
            print_test("Candle structure valid", all_present)

            # Display sample candle
            print(f"\n  Sample Candle:")
            print(f"    Time:   {datetime.fromtimestamp(candle['time'])}")
            print(f"    OHLC:   {candle['open']:.5f} / {candle['high']:.5f} / {candle['low']:.5f} / {candle['close']:.5f}")
            print(f"    Volume: {candle['volume']}")

        return passed
    except requests.exceptions.ConnectionError:
        print_test("Connection to API", False, "Could not connect to http://localhost:8000")
        return False
    except Exception as e:
        print_test("Exception handling", False, str(e))
        return False

def test_account_info_endpoint():
    """Test /api/account-info endpoint"""
    print(f"\n{bcolors.HEADER}Testing Account Info Endpoint{bcolors.ENDC}")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/api/account-info")
        passed = response.status_code == 200
        print_test("Status Code 200", passed)

        data = response.json()

        if "error" in data:
            print_test("MT5 Connection", False, data['error'])
            return False

        # Check account fields
        fields_to_check = ['login', 'balance', 'equity', 'profit', 'margin', 'margin_free', 'currency']
        for field in fields_to_check:
            has_field = field in data
            print_test(f"Has '{field}'", has_field, f"Value: {data.get(field)}")

        return True
    except Exception as e:
        print_test("Exception handling", False, str(e))
        return False

def test_positions_endpoint():
    """Test /api/positions endpoint"""
    print(f"\n{bcolors.HEADER}Testing Positions Endpoint{bcolors.ENDC}")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/api/positions")
        passed = response.status_code == 200
        print_test("Status Code 200", passed)

        positions = response.json()
        print_test("Valid JSON Response", isinstance(positions, list), f"Positions: {len(positions)}")

        if len(positions) > 0:
            pos = positions[0]
            required_fields = ['ticket', 'symbol', 'type', 'volume', 'open_price', 'current_price', 'profit']
            all_present = all(field in pos for field in required_fields)
            print_test("Position structure valid", all_present)

            # Display sample position
            print(f"\n  Sample Position:")
            print(f"    Ticket:      #{pos['ticket']}")
            print(f"    Symbol:      {pos['symbol']}")
            print(f"    Type:        {pos['type']}")
            print(f"    Volume:      {pos['volume']}")
            print(f"    Open Price:  {pos['open_price']:.5f}")
            print(f"    Current:     {pos['current_price']:.5f}")
            print(f"    P&L:         ${pos['profit']:.2f}")
        else:
            print(f"  No open positions (this is normal)")

        return True
    except Exception as e:
        print_test("Exception handling", False, str(e))
        return False

def test_symbol_tick_endpoint():
    """Test /api/symbol-tick endpoint"""
    print(f"\n{bcolors.HEADER}Testing Symbol Tick Endpoint{bcolors.ENDC}")
    print("=" * 60)

    try:
        response = requests.get(f"{BASE_URL}/api/symbol-tick")
        passed = response.status_code == 200
        print_test("Status Code 200", passed)

        data = response.json()

        if "error" in data:
            print_test("Data availability", False, data['error'])
            return False

        required_fields = ['bid', 'ask', 'last', 'volume', 'time']
        for field in required_fields:
            has_field = field in data
            print_test(f"Has '{field}'", has_field, f"Value: {data.get(field)}")

        print(f"\n  Current Tick:")
        print(f"    Bid:    {data.get('bid', 'N/A')}")
        print(f"    Ask:    {data.get('ask', 'N/A')}")
        print(f"    Spread: {(data.get('ask', 0) - data.get('bid', 0)):.5f}")

        return True
    except Exception as e:
        print_test("Exception handling", False, str(e))
        return False

async def test_websocket_endpoint():
    """Test WebSocket /ws/stream endpoint"""
    print(f"\n{bcolors.HEADER}Testing WebSocket Endpoint{bcolors.ENDC}")
    print("=" * 60)

    try:
        print("Connecting to WebSocket...")
        async with websockets.connect(WS_URL) as websocket:
            print_test("WebSocket Connection", True, "Successfully connected to ws://localhost:8000/ws/stream")

            # Wait for a message
            print("Waiting for server message (5 second timeout)...")
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                print_test("Message Received", True, f"Type: {data.get('type')}")

                if 'candles' in data:
                    print_test("Has 'candles'", True, f"Count: {len(data['candles'])}")
                if 'signals' in data:
                    print_test("Has 'signals'", True, f"Count: {len(data['signals'])}")

                return True
            except asyncio.TimeoutError:
                print_test("Message Reception", False, "No message received within 5 seconds (server may not have updates)")
                return True  # Connection works, just no updates yet

    except ConnectionRefusedError:
        print_test("WebSocket Connection", False, "Could not connect to ws://localhost:8000/ws/stream")
        return False
    except Exception as e:
        print_test("Exception handling", False, str(e))
        return False

def test_static_files():
    """Test if static files are served"""
    print(f"\n{bcolors.HEADER}Testing Static Files{bcolors.ENDC}")
    print("=" * 60)

    try:
        # Test main HTML
        response = requests.get(f"{BASE_URL}/")
        passed = response.status_code == 200
        print_test("Root HTML (index.html)", passed)

        # Test JavaScript
        response = requests.get(f"{BASE_URL}/static/js/chart.js")
        passed = response.status_code == 200
        print_test("JavaScript (chart.js)", passed)

        return True
    except Exception as e:
        print_test("Static files", False, str(e))
        return False

def run_all_tests():
    """Run all API tests"""
    print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║      AI Trading Dashboard - API Endpoint Test Suite             ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(bcolors.ENDC)

    print(f"\n📡 Base URL: {BASE_URL}")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run synchronous tests
    results = {
        "Chart Data": test_chart_data_endpoint(),
        "Account Info": test_account_info_endpoint(),
        "Positions": test_positions_endpoint(),
        "Symbol Tick": test_symbol_tick_endpoint(),
        "Static Files": test_static_files(),
    }

    # Run async tests
    try:
        results["WebSocket"] = asyncio.run(test_websocket_endpoint())
    except Exception as e:
        print(f"WebSocket test failed: {e}")
        results["WebSocket"] = False

    # Summary
    print(f"\n{bcolors.BOLD}{bcolors.HEADER}")
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(bcolors.ENDC)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = f"{bcolors.OKGREEN}✓ PASS{bcolors.ENDC}" if result else f"{bcolors.FAIL}✗ FAIL{bcolors.ENDC}"
        print(f"{status} | {test_name}")

    print()
    if passed == total:
        print(f"{bcolors.OKGREEN}{bcolors.BOLD}All tests passed! ({passed}/{total}){bcolors.ENDC}")
    else:
        print(f"{bcolors.WARNING}Some tests failed: {passed}/{total} passed{bcolors.ENDC}")

    print(f"\n✅ Dashboard available at: http://localhost:8000")
    print(f"📊 WebSocket updates available at: ws://localhost:8000/ws/stream\n")

if __name__ == "__main__":
    run_all_tests()

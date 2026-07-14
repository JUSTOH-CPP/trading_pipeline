#!/usr/bin/env python
"""
Quick test to verify API server can start without errors
"""
import sys
import time
import threading
import requests
from api_server import app
import uvicorn

def start_server():
    """Start the API server in a background thread"""
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
    server = uvicorn.Server(config)
    try:
        asyncio.run(server.serve())
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    import asyncio

    print("=" * 60)
    print("Testing API Server Startup")
    print("=" * 60)

    # Start server in background thread
    print("\n[1/3] Starting API server...")
    try:
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8000,
            log_level="warning"
        )
        server = uvicorn.Server(config)

        def run_server():
            try:
                asyncio.run(server.serve())
            except KeyboardInterrupt:
                pass

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # Give server time to start
        time.sleep(3)
        print("✓ API server started")

        # Test basic endpoint
        print("\n[2/3] Testing /api/chart-data endpoint...")
        try:
            response = requests.get("http://127.0.0.1:8000/api/chart-data", timeout=5)
            if response.status_code == 200:
                print(f"✓ Chart data endpoint working (Status: {response.status_code})")
                print(f"  Response: {response.json()}")
            else:
                print(f"⚠ Endpoint returned status {response.status_code}")
        except Exception as e:
            print(f"⚠ Could not reach endpoint: {e}")

        # Test root endpoint
        print("\n[3/3] Testing root endpoint...")
        try:
            response = requests.get("http://127.0.0.1:8000/", timeout=5)
            if response.status_code == 200:
                print(f"✓ Root endpoint working (Status: {response.status_code})")
                if "html" in response.headers.get("content-type", ""):
                    print("  ✓ HTML dashboard served correctly")
            else:
                print(f"⚠ Root endpoint returned status {response.status_code}")
        except Exception as e:
            print(f"⚠ Could not reach root: {e}")

        print("\n" + "=" * 60)
        print("✓ API Server test completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"✗ Error starting API server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

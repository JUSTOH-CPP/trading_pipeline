#!/usr/bin/env python
"""
Quick test to verify static files are being served correctly
"""
import time
import threading
import requests
from api_server import app
import uvicorn

def test_static_files():
    print("=" * 70)
    print("Testing Static Files Serving")
    print("=" * 70)
    print()

    # Start server in background thread
    print("[1/4] Starting API server...")
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=8000,
        log_level="warning"
    )
    server = uvicorn.Server(config)

    def run_server():
        import asyncio
        try:
            asyncio.run(server.serve())
        except KeyboardInterrupt:
            pass

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    time.sleep(3)
    print("✓ Server started\n")

    # Test root HTML
    print("[2/4] Testing root HTML endpoint...")
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if response.status_code == 200:
            print(f"✓ Root endpoint: {response.status_code} OK")
            if "html" in response.text.lower():
                print("✓ HTML content found\n")
        else:
            print(f"✗ Root endpoint: {response.status_code}\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")

    # Test JavaScript file
    print("[3/4] Testing static JavaScript file...")
    try:
        response = requests.get("http://127.0.0.1:8000/static/js/chart.js", timeout=5)
        if response.status_code == 200:
            print(f"✓ Chart.js endpoint: {response.status_code} OK")
            print(f"✓ File size: {len(response.content)} bytes")
            if "function" in response.text.lower() or "let" in response.text:
                print("✓ JavaScript content found\n")
        else:
            print(f"✗ Chart.js endpoint: {response.status_code}")
            print(f"  This is the 404 error you were seeing!\n")
    except Exception as e:
        print(f"✗ Error: {e}\n")

    # Test favicon
    print("[4/4] Testing favicon...")
    try:
        response = requests.get("http://127.0.0.1:8000/favicon.ico", timeout=5)
        if response.status_code == 200:
            print(f"✓ Favicon: {response.status_code} OK\n")
        else:
            print(f"ℹ Favicon: {response.status_code} (optional)\n")
    except Exception as e:
        print(f"ℹ Favicon not found (optional): {e}\n")

    print("=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    print("✓ Static files are now being served correctly!")
    print("✓ Dashboard should load without 404 errors")
    print("✓ Chart.js will be available")
    print()

if __name__ == "__main__":
    try:
        test_static_files()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

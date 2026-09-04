#!/usr/bin/env python3
"""
UA Alert Forecast & Live Vector Radar System.
Unified Single-File Standalone & Desktop Application.
"""
import argparse
import logging
import multiprocessing
import os
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
import uvicorn

logger = logging.getLogger("app.runner")

def is_port_available(host: str, port: int) -> bool:
    """Check if a local port is available for binding."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) != 0

def find_available_port(host: str, preferred_port: int) -> int:
    """Find preferred port or next free available port."""
    if is_port_available(host, preferred_port):
        return preferred_port
    
    # Try preferred + 1 up to + 50
    for p in range(preferred_port + 1, preferred_port + 50):
        if is_port_available(host, p):
            return p
            
    # Fallback to system assigned free port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

def wait_for_server(url: str, timeout: float = 12.0) -> bool:
    """Wait until server responds to HTTP requests."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "UA-Alert-HealthCheck"})
            with urllib.request.urlopen(req, timeout=1.0) as res:
                if res.status in (200, 304):
                    return True
        except Exception:
            time.sleep(0.2)
    return False

def main():
    multiprocessing.freeze_support()

    # Safety check for windowed/GUI environment where streams might be None
    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w')

    parser = argparse.ArgumentParser(description="UA Alert Forecast & Live Vector Radar System")
    parser.add_argument("--port", "-p", type=int, default=None, help="Port to run web server on (default: 8080 or next free)")
    parser.add_argument("--host", "-H", type=str, default=None, help="Host to bind to (default: 127.0.0.1 for desktop, 0.0.0.0 if specified)")
    parser.add_argument("--browser", "-b", action="store_true", help="Launch in default system web browser instead of native desktop window")
    parser.add_argument("--headless", "-s", action="store_true", help="Run in headless background/server mode without opening any window or browser")

    # Filter out macOS Finder arguments like -psn_0_...
    clean_argv = [arg for arg in sys.argv[1:] if not arg.startswith("-psn")]
    args, _ = parser.parse_known_args(clean_argv)

    env_host = os.environ.get("HOST")
    host = args.host or env_host or "127.0.0.1"
    
    env_port = os.environ.get("PORT")
    preferred_port = args.port or (int(env_port) if env_port else 8080)
    port = find_available_port(host, preferred_port)
    
    server_url = f"http://localhost:{port}" if host in ("127.0.0.1", "0.0.0.0") else f"http://{host}:{port}"

    print("=" * 68)
    print("🇺🇦 UA ALERT FORECAST & AIRBORNE RADAR SYSTEM 2026 PRO")
    print(f"🚀 Autonomous Desktop Engine: {server_url}")
    print("📡 Monitoring 26 open sources with real-time vector kinematics")
    print("=" * 68)

    # Configure uvicorn server
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="warning",
        access_log=False
    )
    server = uvicorn.Server(config)

    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    # Wait for server readiness
    wait_for_server(f"{server_url}/api/regions")

    # Headless mode
    if args.headless or os.environ.get("HEADLESS", "").lower() in ("1", "true"):
        print(f"✨ Server running in headless mode at {server_url}. Press Ctrl+C to stop.")
        try:
            while not server.should_exit:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nShutting down server...")
            server.should_exit = True
        return

    # Browser-only mode
    if args.browser:
        print(f"🌐 Opening default browser at {server_url}...")
        webbrowser.open(server_url)
        try:
            while not server.should_exit:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nShutting down server...")
            server.should_exit = True
        return

    # Try native desktop window via pywebview
    try:
        import webview
        print("🖥️  Opening native desktop window...")
        window = webview.create_window(
            title="UA Alert Forecast & Vector Radar System",
            url=server_url,
            width=1340,
            height=860,
            min_size=(960, 600)
        )
        webview.start()
        server.should_exit = True
    except Exception as e:
        print(f"⚠️  Native window unavailable ({e}). Opening in web browser instead...")
        webbrowser.open(server_url)
        try:
            while not server.should_exit:
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\nShutting down server...")
            server.should_exit = True

if __name__ == "__main__":
    main()


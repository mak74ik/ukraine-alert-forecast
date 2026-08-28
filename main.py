#!/usr/bin/env python3
"""
UA Alert Forecast & Live Vector Radar System.
Single-command standalone entrypoint.
"""
import sys
import os
import uvicorn

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("=" * 65)
    print("🇺🇦 UA ALERT FORECAST & AIRBORNE RADAR SYSTEM 2026 PRO")
    print(f"🚀 Starting autonomous web server on http://localhost:{port}")
    print("📡 Monitoring 26 open sources with real-time vector kinematics")
    print("=" * 65)
    
    uvicorn.run("app.main:app", host=host, port=port, log_level="info", access_log=False)

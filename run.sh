#!/bin/bash
set -e

echo "🇺🇦 UA Alert Forecast & Monitor System"
echo "======================================="

# Create virtualenv if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "🔄 Installing dependencies..."
./venv/bin/pip install -q --upgrade pip
./venv/bin/pip install -q -r requirements.txt

echo "🚀 Starting Autonomous Radar & Forecast Server on http://localhost:8080"
./venv/bin/python main.py

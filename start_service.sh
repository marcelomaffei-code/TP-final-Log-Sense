#!/bin/bash

# LogSense Startup Script for AWS EC2

set -e

echo "=== Starting LogSense ==="

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "main.py not found. Please ensure you are in the correct directory."
    exit 1
fi

echo "Starting LogSense application..."
python3 main.py

echo "=== LogSense Stopped ==="

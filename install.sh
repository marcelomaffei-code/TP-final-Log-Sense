#!/bin/bash

# LogSense Installation Script for AWS EC2
# Compatible with Ubuntu 20.04+ and Amazon Linux

set -e

echo "=== LogSense Installation Script ==="
echo "Updating system packages..."

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "Cannot detect OS. Exiting."
    exit 1
fi

# Update packages
if [ "$OS" = "ubuntu" ] || [ "$OS" = "amzn" ]; then
    sudo yum update -y || sudo apt update -y
    sudo yum install -y python3 python3-pip git || sudo apt install -y python3 python3-pip git
else
    echo "Unsupported OS: $OS"
    exit 1
fi

echo "Installing Python 3 and pip..."
python3 --version
pip3 --version

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip

# No external dependencies required for this project
# All structures are implemented from scratch

echo "=== Installation Complete ==="
echo "To start the application, run: ./start_service.sh"

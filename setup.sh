#!/bin/bash

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Compile C++ sniffer
echo "Compiling C++ sniffer..."
if pkg-config --exists libzmq; then
    echo "Found libzmq via pkg-config."
    g++ sniffer.cpp -o sniffer $(pkg-config --cflags --libs libzmq)
elif [ -d "/opt/homebrew/include" ]; then
    echo "pkg-config failed, trying Homebrew paths..."
    g++ sniffer.cpp -o sniffer -I/opt/homebrew/include -L/opt/homebrew/lib -lzmq
else
    echo "Could not find libzmq. Please install it (brew install zeromq)."
    exit 1
fi

if [ $? -eq 0 ]; then
    echo "Compilation successful!"
else
    echo "Compilation failed."
    exit 1
fi

echo "Setup complete!"
echo "To run the project:"
echo "1. Terminal 1: source venv/bin/activate && python3 brain.py"
echo "2. Terminal 2: sudo ./sniffer"

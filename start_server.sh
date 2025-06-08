#!/bin/bash

# Check if .venv folder exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
    echo "Installing required libraries..."
    source .venv/bin/activate
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Failed to install required libraries."
        deactivate
        exit 1
    fi
    deactivate
fi

# Activate the virtual environment
source .venv/bin/activate
# Start the server
echo "Starting the server..."
python3 app.py
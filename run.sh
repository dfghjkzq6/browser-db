#!/bin/bash
# Browser Storage Database API Runner

echo "Starting Browser Storage Database API..."
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo "Starting Flask server on http://localhost:5000"
python3 app.py

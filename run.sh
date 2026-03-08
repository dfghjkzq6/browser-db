#!/bin/bash
# Browser Storage Database API Runner

echo "Starting Browser Storage Database API..."
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo "Starting FastAPI server on http://localhost:8000"
echo "Dashboard will be available at: http://localhost:8000"
echo "API Documentation will be available at: http://localhost:8000/docs"
python3 main.py

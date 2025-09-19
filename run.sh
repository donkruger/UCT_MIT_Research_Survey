#!/bin/bash
#
# Research Survey Template - Startup Script
#

echo "========================================"
echo "Research Survey Template"
echo "========================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip."
    exit 1
fi

# Install dependencies if not already installed
echo "📦 Checking dependencies..."
pip3 install -q streamlit reportlab 2>/dev/null

# Check if Streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit is not installed. Running: pip install streamlit reportlab"
    pip3 install streamlit reportlab
fi

# Run the application
echo "🚀 Starting Research Survey Application..."
echo "   URL: http://localhost:8501"
echo "   Press Ctrl+C to stop"
echo "========================================"
streamlit run app/main.py

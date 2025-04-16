#!/bin/bash
echo "Starting SustainaTrend Application..."
echo ""
echo "This window will remain open while the application is running."
echo "To stop the application, close this window or press Ctrl+C."
echo ""

# Activate virtual environment if it exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "Activated virtual environment."
else
    echo "Virtual environment not found. Using system Python."
fi

# Start the application
python start_app.py

# Keep the window open if there's an error
if [ $? -ne 0 ]; then
    echo ""
    echo "Application exited with error code $?"
    echo "Press Enter to close this window..."
    read
fi 
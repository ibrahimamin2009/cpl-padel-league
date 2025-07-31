#!/bin/bash

echo "Setting up CPL - Chiniot Padel League Management System..."
echo "=========================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
SECRET_KEY=your-secret-key-change-in-production
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
EOF
    echo "Please update the .env file with your email credentials for notifications."
fi

# Remove old database if it exists
echo "Cleaning up old database..."
rm -f cpl.db
rm -f instance/cpl.db
find . -name "*.db" -delete 2>/dev/null

echo ""
echo "=========================================================="
echo "CPL Setup Complete!"
echo "=========================================================="
echo ""
echo "Starting Flask application..."
echo "The application will be available at: http://127.0.0.1:8000"
echo ""
echo "Admin credentials: admin / admin123"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Start the application
python3 app.py 
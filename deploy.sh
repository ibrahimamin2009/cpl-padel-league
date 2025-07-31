#!/bin/bash

# 🏆 CPL - Chiniot Padel League Deployment Script
# This script sets up and runs the CPL application

set -e  # Exit on any error

echo "🏆 CPL - Chiniot Padel League"
echo "======================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if Python 3 is installed
check_python() {
    print_status "Checking Python installation..."
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Found Python $PYTHON_VERSION"
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 is not installed. Please install pip."
        exit 1
    fi
    print_status "Found pip3"
}

# Create virtual environment
setup_venv() {
    print_status "Setting up virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_status "Virtual environment activated"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_status "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    python3 -c "
from app import app, create_tables
with app.app_context():
    create_tables()
print('Database initialized successfully')
"
}

# Add dummy data (optional)
add_dummy_data() {
    print_header "Would you like to add dummy teams for testing? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Adding dummy teams..."
        python3 add_dummy_teams.py
        print_status "Dummy teams added successfully"
    else
        print_status "Skipping dummy data addition"
    fi
}

# Test the application
test_application() {
    print_header "Would you like to run tests? (y/n)"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Running tier system test..."
        python3 test_tier_system.py
        echo ""
        print_status "Running consecutive challenge rule test..."
        python3 test_consecutive_rule_fixed.py
        echo ""
        print_status "Tests completed"
    else
        print_status "Skipping tests"
    fi
}

# Start the application
start_application() {
    print_header "Starting CPL application..."
    print_status "The application will be available at: http://localhost:5000"
    print_status "Press Ctrl+C to stop the application"
    echo ""
    python3 app.py
}

# Main deployment function
deploy() {
    print_header "🚀 CPL Deployment Script"
    echo ""
    
    # Check prerequisites
    check_python
    check_pip
    
    # Setup environment
    setup_venv
    activate_venv
    install_dependencies
    
    # Initialize application
    init_database
    
    # Optional steps
    add_dummy_data
    test_application
    
    # Start application
    start_application
}

# Help function
show_help() {
    echo "CPL Deployment Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -s, --setup     Only setup the environment (don't start the app)"
    echo "  -t, --test      Run tests only"
    echo "  -d, --dummy     Add dummy data only"
    echo ""
    echo "Examples:"
    echo "  $0              # Full deployment and start"
    echo "  $0 --setup      # Setup only"
    echo "  $0 --test       # Run tests only"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -s|--setup)
        print_header "🔧 CPL Setup Only"
        check_python
        check_pip
        setup_venv
        activate_venv
        install_dependencies
        init_database
        print_status "Setup completed successfully!"
        exit 0
        ;;
    -t|--test)
        print_header "🧪 CPL Testing"
        activate_venv
        test_application
        exit 0
        ;;
    -d|--dummy)
        print_header "👥 CPL Dummy Data"
        activate_venv
        add_dummy_data
        exit 0
        ;;
    "")
        deploy
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac 
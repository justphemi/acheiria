#!/bin/bash

# Acheiria Setup Script for macOS
# This script sets up your Mac for building and running Acheiria

echo "======================================"
echo "   Acheiria Setup for macOS"
echo "======================================"
echo ""

# Check if Python 3.14 is installed
echo "1. Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found Python $PYTHON_VERSION"

if [[ ! "$PYTHON_VERSION" =~ ^3\.1[4-9] ]]; then
    echo "   ⚠️  Warning: Python 3.14+ recommended, but will try to continue..."
fi

# Check if pip is available
echo ""
echo "2. Checking pip..."
if ! command -v pip3 &> /dev/null; then
    echo "   Installing pip..."
    python3 -m ensurepip --upgrade
else
    echo "   ✓ pip is installed"
fi

# Create virtual environment
echo ""
echo "3. Creating virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists"
    read -p "   Do you want to recreate it? (y/n): " recreate
    if [ "$recreate" = "y" ]; then
        rm -rf venv
        python3 -m venv venv
        echo "   ✓ Virtual environment recreated"
    fi
else
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "4. Activating virtual environment..."
source venv/bin/activate
echo "   ✓ Virtual environment activated"

# Upgrade pip
echo ""
echo "5. Upgrading pip..."
pip install --upgrade pip
echo "   ✓ pip upgraded"

# Install requirements
echo ""
echo "6. Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "   ✓ Dependencies installed"
else
    echo "   ⚠️  requirements.txt not found. Installing core dependencies..."
    pip install flet google-generativeai pyautogui pyperclip pynput pillow
    echo "   ✓ Core dependencies installed"
fi

# Install system dependencies for keyboard/mouse control
echo ""
echo "7. Checking macOS permissions..."
echo "   ⚠️  IMPORTANT: You need to grant accessibility permissions"
echo "   Go to: System Settings → Privacy & Security → Accessibility"
echo "   Add Terminal (or your IDE) to the list of allowed apps"
echo ""

# Create necessary folders
echo "8. Creating project folders..."
mkdir -p app
mkdir -p assets
touch app/__init__.py
echo "   ✓ Folders created"

# Create config template
echo ""
echo "9. Creating configuration file..."
if [ ! -f "config.json" ]; then
    cat > config.json << 'EOF'
{
  "api_keys": {
    "primary": "",
    "secondary": ""
  },
  "typing_speed": 65,
  "theme": "dark",
  "fold_delay": 5,
  "window_position": {
    "x": 100,
    "y": 100
  },
  "first_run": true
}
EOF
    echo "   ✓ config.json created"
else
    echo "   config.json already exists"
fi

echo ""
echo "======================================"
echo "   Setup Complete! ✓"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Place your logo files in the 'assets' folder"
echo "2. Run 'source venv/bin/activate' to activate the environment"
echo "3. Run 'python3 main.py' to start the app"
echo ""
echo "To grant accessibility permissions:"
echo "→ System Settings → Privacy & Security → Accessibility"
echo "→ Add Terminal (or your Python IDE)"
echo ""
#!/bin/bash

# Exit on error
set -e

echo "Starting setup for Gesture to Text on Raspberry Pi..."

# 1. Update system packages
echo "Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install system dependencies
# libgl1 is often needed for OpenCV
# python3-venv for creating virtual environments
echo "Installing system dependencies..."
sudo apt-get install -y python3-pip python3-venv libgl1 libatlas-base-dev libglib2.0-0 libsm6 libxext6 libxrender-dev

# 3. Create Virtual Environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment 'venv'..."
    python3 -m venv venv
else
    echo "Virtual environment 'venv' already exists."
fi

# 4. Activate Virtual Environment
echo "Activating virtual environment..."
source venv/bin/activate

# 5. Install Python dependencies
echo "Installing Python dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt

# 6. Setup Complete
echo "========================================"
echo "========================================"
echo "Verifying OpenCV installation..."
python3 -c "import cv2; print('OpenCV version:', cv2.__version__)" || echo "WARNING: OpenCV import failed!"
echo "Setup Complete!"
echo "To run the project:"
echo "1. source venv/bin/activate"
echo "2. python main.py"
echo "========================================"

#!/bin/bash

# Navigate to project directory
cd "$(dirname "$0")"

# Activate the virtual environment
source .venv/bin/activate

# Fix macOS Qt/PySide6 platform plugin pathing
export QT_QPA_PLATFORM_PLUGIN_PATH=$(python -c "import PySide6, os; print(os.path.join(os.path.dirname(PySide6.__file__), 'Qt', 'plugins'))")
export QT_QPA_PLATFORM=cocoa

# Set Python path to find your src directory
export PYTHONPATH=$PYTHONPATH:$(pwd)/src

# Run your application
python src/main.py

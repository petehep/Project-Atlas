#!/bin/bash

# Navigate to project root (wherever this script lives)
cd "$(dirname "$0")"

# Activate virtual environment
# Note: renamed to .venv to prevent iCloud Drive from corrupting Qt plugins
source .venv/bin/activate

# Set PYTHONPATH so Python finds the src/ packages
export PYTHONPATH=$(pwd)/src

# Set Qt plugin path for PySide6 on macOS
export QT_QPA_PLATFORM_PLUGIN_PATH=$(python3 -c "import PySide6, os; print(os.path.join(os.path.dirname(PySide6.__file__), 'Qt', 'plugins', 'platforms'))")
export QT_QPA_PLATFORM=cocoa

# Launch Atlas
python3 src/main.py

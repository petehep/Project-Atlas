@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

REM ================================================================
REM  run_atlas.bat  --  Project ATLAS  |  Windows CMD Launcher
REM
REM  LOCATION: project_atlas\windows\run_atlas.bat
REM  USAGE:    Double-click, or run from CMD / PowerShell.
REM            This script navigates to the project root automatically.
REM            DO NOT move this file out of the windows\ subfolder.
REM ================================================================

REM -- Navigate to project root (one level above this script)
cd /d "%~dp0.."
echo [ATLAS] Working directory: %CD%

REM ----------------------------------------------------------------
REM  Pre-flight checks
REM ----------------------------------------------------------------

REM -- Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python not found in PATH.
    echo         Install Python 3.12 from https://python.org/downloads/
    echo         IMPORTANT: Tick "Add Python to PATH" during install.
    echo.
    pause
    exit /b 1
)

REM -- Check virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo.
    echo [ERROR] Virtual environment not found at .venv\
    echo         Run the following commands from the project root:
    echo.
    echo           python -m venv .venv
    echo           .venv\Scripts\activate.bat
    echo           pip install -r requirements.txt
    echo.
    echo         See windows\SETUP_WINDOWS.md for full instructions.
    echo.
    pause
    exit /b 1
)

REM -- Check src\main.py exists (sanity check we are in the right folder)
if not exist "src\main.py" (
    echo.
    echo [ERROR] src\main.py not found. Are you in the right directory?
    echo         Expected project root: a folder containing src\, .venv\, requirements.txt
    echo.
    pause
    exit /b 1
)

REM ----------------------------------------------------------------
REM  Environment setup
REM ----------------------------------------------------------------

REM -- Activate virtual environment
call .venv\Scripts\activate.bat
echo [ATLAS] Virtual environment activated.

REM -- Set PYTHONPATH so Python finds the src/ packages
set PYTHONPATH=%PYTHONPATH%;%CD%\src
echo [ATLAS] PYTHONPATH set.

REM -- Resolve Qt plugin path for this PySide6 install
REM    On Windows, PySide6 keeps plugins at: site-packages\PySide6\plugins
for /f "delims=" %%P in ('python -c "import PySide6, os; print(os.path.join(os.path.dirname(PySide6.__file__), 'plugins'))"') do (
    set QT_PLUGIN_PATH=%%P
)
echo [ATLAS] Qt plugin path: !QT_PLUGIN_PATH!

REM ----------------------------------------------------------------
REM  Launch Atlas
REM ----------------------------------------------------------------
echo.
echo [ATLAS] Launching Atlas v1.6 ...
echo ================================================================
echo.

python src\main.py

REM ----------------------------------------------------------------
REM  Exit handling
REM ----------------------------------------------------------------
set EXIT_CODE=%ERRORLEVEL%
echo.
echo ================================================================
if %EXIT_CODE% neq 0 (
    echo [ATLAS] Atlas exited with error code %EXIT_CODE%.
    echo         Scroll up for the Python traceback.
    echo.
    pause
) else (
    echo [ATLAS] Atlas closed cleanly.
)

ENDLOCAL

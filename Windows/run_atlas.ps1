# ================================================================
#  run_atlas.ps1  --  Project ATLAS  |  Windows PowerShell Launcher
#
#  LOCATION: project_atlas\windows\run_atlas.ps1
#  USAGE:    Right-click > "Run with PowerShell"
#            OR from a PS terminal: .\windows\run_atlas.ps1
#            This script navigates to the project root automatically.
#            DO NOT move this file out of the windows\ subfolder.
#
#  FIRST TIME: You may need to allow script execution:
#    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# ================================================================

$ErrorActionPreference = "Stop"

# ----------------------------------------------------------------
#  Navigate to project root (parent of this script's folder)
# ----------------------------------------------------------------
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot
Write-Host "[ATLAS] Project root: $ProjectRoot" -ForegroundColor Cyan

# ----------------------------------------------------------------
#  Pre-flight checks
# ----------------------------------------------------------------

# Check Python
try {
    $pyVersion = & python --version 2>&1
    Write-Host "[ATLAS] Found: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "" 
    Write-Host "[ERROR] Python not found in PATH." -ForegroundColor Red
    Write-Host "        Install Python 3.12 from https://python.org/downloads/" -ForegroundColor Red
    Write-Host "        IMPORTANT: Tick 'Add Python to PATH' during install." -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check virtual environment
$VenvActivate = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"
if (-not (Test-Path $VenvActivate)) {
    Write-Host ""
    Write-Host "[ERROR] Virtual environment not found at .venv\" -ForegroundColor Red
    Write-Host "        Run the following from the project root in a terminal:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "          python -m venv .venv" -ForegroundColor White
    Write-Host "          .venv\Scripts\Activate.ps1" -ForegroundColor White
    Write-Host "          pip install -r requirements.txt" -ForegroundColor White
    Write-Host ""
    Write-Host "        See windows\SETUP_WINDOWS.md for full instructions." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check src\main.py
if (-not (Test-Path (Join-Path $ProjectRoot "src\main.py"))) {
    Write-Host ""
    Write-Host "[ERROR] src\main.py not found. Wrong directory?" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# ----------------------------------------------------------------
#  Environment setup
# ----------------------------------------------------------------

# Activate virtual environment
& $VenvActivate
Write-Host "[ATLAS] Virtual environment activated." -ForegroundColor Green

# Set PYTHONPATH
$env:PYTHONPATH = "$env:PYTHONPATH;$ProjectRoot\src"
Write-Host "[ATLAS] PYTHONPATH configured." -ForegroundColor Green

# Resolve Qt plugin path for this PySide6 install
$QtPluginPath = & python -c "import PySide6, os; print(os.path.join(os.path.dirname(PySide6.__file__), 'plugins'))"
$env:QT_PLUGIN_PATH = $QtPluginPath
Write-Host "[ATLAS] Qt plugin path: $QtPluginPath" -ForegroundColor Green

# ----------------------------------------------------------------
#  Launch Atlas
# ----------------------------------------------------------------
Write-Host ""
Write-Host "[ATLAS] Launching Atlas v1.6 ..." -ForegroundColor Cyan
Write-Host "================================================================"
Write-Host ""

$MainScript = Join-Path $ProjectRoot "src\main.py"
& python $MainScript
$exitCode = $LASTEXITCODE

# ----------------------------------------------------------------
#  Exit handling
# ----------------------------------------------------------------
Write-Host ""
Write-Host "================================================================"
if ($exitCode -ne 0) {
    Write-Host "[ATLAS] Atlas exited with error code $exitCode." -ForegroundColor Red
    Write-Host "        Scroll up for the Python traceback." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
} else {
    Write-Host "[ATLAS] Atlas closed cleanly." -ForegroundColor Green
}

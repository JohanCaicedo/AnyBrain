@echo off
title AnyBrain - Automated Knowledge Engine
color 0B
cls

echo ==========================================================
echo        AnyBrain - LOCAL RAG & EMBEDDING TOOL
echo ==========================================================
echo.

:: ---------------------------------------------------------
:: STEP 1: CHECK PYTHON
:: ---------------------------------------------------------
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [CRITICAL ERROR] Python not found.
    echo.
    echo Please install Python 3.10 or 3.11.
    echo Download: https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation.
    echo.
    pause
    exit
)

echo [OK] Python detected.
echo.

:: ---------------------------------------------------------
:: STEP 2: CHECK/CREATE VIRTUAL ENVIRONMENT
:: ---------------------------------------------------------
if not exist "venv" (
    color 0E
    echo [NOTICE] First time running AnyBrain.
    echo Creating virtual environment and installing dependencies...
    echo (This process may take a few minutes).
    echo.
    
    :: Create venv
    python -m venv venv
    
    :: Activate and install
    call venv\Scripts\activate
    
    echo Upgrading pip...
    python -m pip install --upgrade pip
    
    echo Installing requirements...
    pip install -r requirements.txt
    
    color 0B
    echo.
    echo [SUCCESS] AnyBrain installation complete.
    echo.
) else (
    echo [OK] Virtual environment found. Starting...
    call venv\Scripts\activate
)

:: ---------------------------------------------------------
:: STEP 3: RUN APPLICATION
:: ---------------------------------------------------------

if not exist "src\config.py" (
    echo [ALERT] src\config.py not found. Please check repository structure.
    pause
    exit
)

echo.
echo [1/2] AnyBrain is scanning for new documents...
python src/ingest.py

echo.
echo [2/2] Launching Interface...
echo (Browser will open automatically)
echo.

chainlit run src/app.py -w --port 8000

pause
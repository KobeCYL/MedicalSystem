@echo off
echo ========================================
echo   Medical Diagnosis System - Auto Start
echo ========================================
echo.

REM Check if Conda environment exists
echo [INFO] Checking Conda environment...
call conda activate llm_pro >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Conda environment 'llm_pro' not found
    echo [INFO] Please create the environment with: conda create -n llm_pro python=3.8
    pause
    exit /b 1
)

REM Activate Conda environment
echo [INFO] Activating Conda environment: llm_pro
call conda activate llm_pro

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in Conda environment
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo [INFO] Checking Python dependencies...
python -c "import flask, streamlit, aiofiles" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Missing required Python packages
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    echo [SUCCESS] Dependencies installed successfully
)

echo.
echo [INFO] Starting Flask backend API service...
start "Flask API Server" cmd /k "conda activate llm_pro && python app.py"

REM Wait for Flask service to start
timeout /t 3 /nobreak >nul

echo [INFO] Starting Streamlit frontend interface...
start "Streamlit Frontend" cmd /k "conda activate llm_pro && streamlit run streamlit_app.py"

echo.
echo ========================================
echo [SUCCESS] All services started!
echo ========================================
echo Backend API: http://localhost:5000
echo Frontend UI: http://localhost:8501
echo.
echo Note: Services are running in 'llm_pro' Conda environment
echo.
echo Press any key to close this window...
pause >nul
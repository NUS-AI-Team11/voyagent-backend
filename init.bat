@echo off
REM VoyageAgent project initialization script (Windows)

echo.
echo ============================================================
echo       VoyageAgent - Intelligent Travel Planning System
echo ============================================================
echo.

REM Check Python version
echo Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.9 or higher.
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

REM Create virtual environment
echo.
echo Creating Python virtual environment...
if exist venv (
    echo Virtual environment already exists, skipping.
) else (
    python -m venv venv
    echo Virtual environment created.
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated.

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo pip upgraded.

REM Install dependencies
echo.
echo Installing project dependencies...
pip install -r requirements.txt >nul 2>&1
echo Dependencies installed.

REM Configure environment variables
echo.
echo Configuring environment variables...
if exist .env (
    echo .env file already exists, skipping.
) else (
    copy .env.example .env >nul
    echo .env file created.
    echo    Please edit .env and add your API keys.
)

REM Run framework tests
echo.
echo Running framework integrity tests...
python test_framework.py

echo.
echo ============================================================
echo                    Initialization complete!
echo ============================================================
echo.
echo Next steps:
echo    1. Edit .env and configure your API keys
echo    2. Run tests: pytest tests/ -v
echo    3. Start the app: python main.py
echo.
echo Learn more:
echo    - Architecture: docs/architecture.md
echo    - Project docs: README.md
echo    - Framework report: FRAMEWORK_REPORT.md
echo.
echo Happy coding!
echo.

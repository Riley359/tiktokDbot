@echo off
echo Installing TikTok Scraper Dependencies...
echo ========================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

:: Install requirements
echo Installing required packages...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

:: Install playwright browsers
echo Installing playwright browsers...
python -m playwright install

if errorlevel 1 (
    echo ERROR: Failed to install playwright browsers
    pause
    exit /b 1
)

echo.
echo ✓ Dependencies and browsers installed successfully!
echo.
echo Next steps:
echo 1. Get your TikTok sessionid from browser cookies
echo 2. Edit src/config.py and paste your sessionid
echo 3. Run: python scraper.py
echo.
pause

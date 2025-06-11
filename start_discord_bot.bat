@echo off
title TikTok Discord Bot
echo ===================================
echo    TikTok Discord Bot Launcher
echo ===================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if bot_config.py exists
if not exist "bot_config.py" (
    echo [ERROR] bot_config.py not found
    echo Run quick_start.py first to set up configuration
    pause
    exit /b 1
)

REM Check if discord_bot.py exists
if not exist "discord_bot.py" (
    echo [ERROR] discord_bot.py not found
    echo Please ensure all bot files are present
    pause
    exit /b 1
)

echo [INFO] Starting TikTok Discord Bot...
echo [INFO] Press Ctrl+C to stop the bot
echo.

REM Run the Discord bot
python discord_bot.py

echo.
echo [INFO] Bot has stopped
pause

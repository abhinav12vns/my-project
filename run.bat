@echo off
echo =======================================
echo   Instagram Auto Poster Bot - Setup
echo =======================================
echo.
echo Step 1: Installing required packages...
pip install -r requirements.txt
echo.
echo Step 2: Starting the bot...
echo (Keep this window open. Bot runs in background.)
echo.
python instagram_bot.py
echo.
echo Bot stopped.
pause

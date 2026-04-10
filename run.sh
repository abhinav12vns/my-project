#!/bin/bash
echo "======================================="
echo "  Instagram Auto Poster Bot - Setup"
echo "======================================="
echo ""
echo "Step 1: Installing required packages..."
pip3 install -r requirements.txt
echo ""
echo "Step 2: Starting the bot..."
echo "(Keep this window open. Bot runs until you close it.)"
echo ""
python3 instagram_bot.py

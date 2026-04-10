=============================================
  INSTAGRAM AUTO POSTER BOT — INSTRUCTIONS
=============================================

WHAT THIS BOT DOES:
  ✅ Downloads videos from your main channel
  ✅ Uploads 3 videos per day to all 10 accounts
  ✅ Posts original captions automatically
  ✅ Never repeats a video on the same account
  ✅ Waits between uploads to avoid Instagram ban

=============================================
  STEP 1 — INSTALL PYTHON (one time only)
=============================================

If you don't have Python installed:
  1. Go to https://www.python.org/downloads/
  2. Download Python 3.11 or newer
  3. During install → CHECK "Add Python to PATH"

=============================================
  STEP 2 — FILL IN YOUR ACCOUNTS
=============================================

Open config.json with Notepad and fill in:

  "main_account" → Username & password of the channel
                   you want to download videos FROM

  "upload_accounts" → Username & password of all 10
                      accounts you want to post TO

  "posting_times" → Times to post each day
                    Default: 9AM, 2PM, 7PM
                    Format must be "HH:MM" (24-hour)

Example:
  "username": "mypage123",
  "password": "mypassword456"

Save the file when done.

=============================================
  STEP 3 — RUN THE BOT
=============================================

WINDOWS:
  → Double-click "run.bat"
  → Keep the window open

MAC / LINUX:
  → Open Terminal in this folder
  → Type: bash run.sh
  → Keep the window open

The bot will:
  1. Immediately download videos from main channel
  2. Upload at 9AM, 2PM, and 7PM every day
  3. Show activity in the terminal window
  4. Also save everything to bot_log.txt

=============================================
  FILES CREATED AUTOMATICALLY
=============================================

downloaded_videos/   → All downloaded video files
posted_log.json      → Tracks what was posted where
video_queue.json     → List of videos to post
bot_log.txt          → Full activity log
session_*.json       → Saved login sessions (safe)

DO NOT delete these files while bot is running!

=============================================
  IF SOMETHING GOES WRONG
=============================================

Check bot_log.txt — it shows exactly what happened
and which account had an error.

Common issues:
  ❌ "Login FAILED" → Check username/password in config.json
  ❌ "No videos available" → Check main account username
  ❌ "Video file missing" → Delete video_queue.json and restart

=============================================
  FOR 24/7 RUNNING (Recommended for clients)
=============================================

Run on a VPS server so your laptop can be off:
  - DigitalOcean: https://digitalocean.com (~$5/month)
  - Hetzner: https://hetzner.com (~$4/month)
  - Upload all files to server and run: python3 instagram_bot.py

=============================================

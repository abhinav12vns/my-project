"""
==============================================
  QUICK TEST SCRIPT
  Tests downloading 1 video + uploading to 1 account
  Uses instagrapi for both download and upload
==============================================
"""

import json
from pathlib import Path
from instagrapi import Client

DOWNLOAD_FOLDER = Path("downloaded_videos")
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

MAIN_USERNAME = config["main_account"]["username"]
TEST_ACCOUNT  = config["upload_accounts"][0]

print("=" * 50)
print("  INSTAGRAM BOT — QUICK TEST")
print("=" * 50)
print(f"  Downloading from : @{MAIN_USERNAME}")
print(f"  Uploading to     : @{TEST_ACCOUNT['username']}")
print("=" * 50)
print()

# ── Login once, use for both download and upload ──────
cl = Client()
session_file = Path(f"session_{TEST_ACCOUNT['username']}.json")

if session_file.exists():
    cl.load_settings(session_file)

print(f"🔑 Logging in as @{TEST_ACCOUNT['username']}...")
cl.login(TEST_ACCOUNT["username"], TEST_ACCOUNT["password"])
cl.dump_settings(session_file)
print(f"   ✅ Logged in\n")


# ── STEP 1: Download 1 video ──────────────────────────
print("📥 STEP 1: Downloading 1 video from @" + MAIN_USERNAME + "...")
print("   (This may take 30-60 seconds)\n")

video_path   = None
caption_text = ""

try:
    user_id = cl.user_id_from_username(MAIN_USERNAME)
    medias  = cl.user_medias(user_id, amount=20)

    for media in medias:
        if media.media_type == 2:  # 2 = video
            print(f"   Found video  : {media.pk}")
            print(f"   Caption      : {str(media.caption_text or '')[:60]}...")

            downloaded = cl.video_download(media.pk, folder=DOWNLOAD_FOLDER)
            video_path   = downloaded
            caption_text = media.caption_text or ""
            print(f"   ✅ Downloaded : {video_path}")
            break

    if not video_path:
        print("   ❌ No videos found. Check the username in config.json")
        exit(1)

except Exception as e:
    print(f"   ❌ Download failed: {e}")
    exit(1)


# ── STEP 2: Upload ────────────────────────────────────
print()
print(f"📤 STEP 2: Uploading to @{TEST_ACCOUNT['username']}...")
print("   (This may take 1-2 minutes)\n")

try:
    cl.video_upload(str(video_path), caption=caption_text)
    print(f"   ✅ Uploaded to @{TEST_ACCOUNT['username']}!")

except Exception as e:
    print(f"   ❌ Upload failed: {e}")
    print()
    print("   Common fixes:")
    print("   - Check username/password in config.json")
    print("   - Make sure the account is not restricted")
    exit(1)


print()
print("=" * 50)
print("  TEST PASSED! Everything is working.")
print("  Now run: python3 instagram_bot.py")
print("=" * 50)

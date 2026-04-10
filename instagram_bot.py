"""
==============================================
  Instagram Auto Poster Bot
  - Downloads from source account (last 6 months only)
  - Uploads to all accounts, 3x/day
  - Never repeats the same post
==============================================
"""

import json
import time
import random
import schedule
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from instagrapi import Client

# ─────────────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("bot_log.txt", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────────────────
try:
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
except FileNotFoundError:
    log.error("config.json not found!")
    exit(1)

MAIN_USERNAME   = config["main_account"]["username"]
UPLOAD_ACCOUNTS = config["upload_accounts"]
POSTING_TIMES   = config.get("posting_times", ["09:00", "14:00", "19:00"])
DOWNLOAD_FOLDER = Path("downloaded_videos")
LOG_FILE        = Path("posted_log.json")
QUEUE_FILE      = Path("video_queue.json")
SIX_MONTHS_AGO  = datetime.now(timezone.utc) - timedelta(days=180)

DOWNLOAD_FOLDER.mkdir(exist_ok=True)


# ─────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────
def load_posted_log():
    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_posted_log(data):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def load_queue():
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE, "r") as f:
            return json.load(f)
    return []

def save_queue(queue):
    with open(QUEUE_FILE, "w") as f:
        json.dump(queue, f, indent=2)

def login_client(username, password):
    cl = Client()
    session_file = Path(f"session_{username}.json")
    if session_file.exists():
        try:
            cl.load_settings(session_file)
            cl.login(username, password)
            log.info(f"   Logged in (saved session): @{username}")
            return cl
        except Exception:
            log.warning(f"   Session expired for @{username}, logging in fresh...")
    try:
        cl.login(username, password)
        cl.dump_settings(session_file)
        log.info(f"   Logged in fresh: @{username}")
        return cl
    except Exception as e:
        log.error(f"   Login FAILED for @{username}: {e}")
        return None


# ─────────────────────────────────────────────────────
#  STEP 1: DOWNLOAD VIDEOS (last 6 months, no repeats)
# ─────────────────────────────────────────────────────
def download_new_videos():
    log.info("━" * 50)
    log.info(f"Downloading videos from @{MAIN_USERNAME} (last 6 months)...")

    # Use first upload account to access Instagram
    first_acc = UPLOAD_ACCOUNTS[0]
    cl = login_client(first_acc["username"], first_acc["password"])
    if not cl:
        log.error("Cannot download — login failed.")
        return

    try:
        queue        = load_queue()
        existing_ids = {v["id"] for v in queue}
        new_count    = 0

        user_id = cl.user_id_from_username(MAIN_USERNAME)
        log.info(f"   Found user ID: {user_id}")

        # Fetch up to 200 recent posts, filter to last 6 months
        medias = cl.user_medias(user_id, amount=200)
        log.info(f"   Fetched {len(medias)} recent posts. Filtering videos from last 6 months...")

        for media in medias:
            # Skip if older than 6 months
            post_date = media.taken_at
            if post_date.tzinfo is None:
                post_date = post_date.replace(tzinfo=timezone.utc)
            if post_date < SIX_MONTHS_AGO:
                continue

            # Skip non-videos (media_type 2 = video, 1 = photo, 8 = album)
            if media.media_type != 2:
                continue

            video_id = str(media.pk)

            if video_id in existing_ids:
                continue  # Already in queue

            try:
                downloaded_path = cl.video_download(media.pk, folder=DOWNLOAD_FOLDER)
                caption = media.caption_text or ""

                # Save caption to a text file
                caption_path = DOWNLOAD_FOLDER / f"{video_id}_caption.txt"
                with open(caption_path, "w", encoding="utf-8") as f:
                    f.write(caption)

                queue.append({
                    "id":           video_id,
                    "video_path":   str(downloaded_path),
                    "caption_path": str(caption_path),
                    "posted_at":    post_date.isoformat(),
                    "added_at":     datetime.now().isoformat()
                })
                existing_ids.add(video_id)
                new_count += 1
                log.info(f"   Downloaded: {video_id} (posted {post_date.strftime('%Y-%m-%d')})")

                time.sleep(2)  # Be polite to Instagram's servers

            except Exception as e:
                log.error(f"   Could not download {video_id}: {e}")
                continue

        save_queue(queue)
        log.info(f"Done. {new_count} new video(s) added. Total in queue: {len(queue)}")

    except Exception as e:
        log.error(f"Download error: {e}")


# ─────────────────────────────────────────────────────
#  STEP 2: UPLOAD NEXT VIDEO TO ALL ACCOUNTS
# ─────────────────────────────────────────────────────
def upload_one_batch():
    log.info("━" * 50)
    log.info("Starting upload batch...")

    queue      = load_queue()
    posted_log = load_posted_log()

    if not queue:
        log.warning("Queue empty! Downloading first...")
        download_new_videos()
        queue = load_queue()

    if not queue:
        log.error("No videos in queue. Check main account username.")
        return

    # Find the next video that hasn't been posted to all accounts
    next_video = None
    for video in queue:
        vid_id     = video["id"]
        all_posted = all(
            vid_id in posted_log.get(acc["username"], [])
            for acc in UPLOAD_ACCOUNTS
        )
        if not all_posted:
            next_video = video
            break

    if not next_video:
        log.info("All queued videos posted everywhere! Downloading more...")
        download_new_videos()
        return

    vid_id     = next_video["id"]
    video_path = next_video["video_path"]

    if not Path(video_path).exists():
        log.error(f"Video file missing: {video_path}")
        return

    caption = ""
    try:
        with open(next_video["caption_path"], "r", encoding="utf-8") as f:
            caption = f.read().strip()
    except Exception:
        pass

    log.info(f"Video  : {vid_id}")
    log.info(f"Caption: {caption[:80]}{'...' if len(caption) > 80 else ''}")

    for i, account in enumerate(UPLOAD_ACCOUNTS):
        username = account["username"]

        if vid_id in posted_log.get(username, []):
            log.info(f"   [{i+1}] @{username} — already posted, skipping.")
            continue

        log.info(f"   [{i+1}/{len(UPLOAD_ACCOUNTS)}] Uploading to @{username}...")

        cl = login_client(username, account["password"])
        if not cl:
            log.error(f"   Skipping @{username} — login failed.")
            continue

        try:
            cl.video_upload(video_path, caption=caption)

            if username not in posted_log:
                posted_log[username] = []
            posted_log[username].append(vid_id)
            save_posted_log(posted_log)

            log.info(f"   Posted to @{username}!")

        except Exception as e:
            log.error(f"   Failed @{username}: {e}")

        # Wait between accounts to avoid spam detection
        if i < len(UPLOAD_ACCOUNTS) - 1:
            delay = random.randint(90, 180)
            log.info(f"   Waiting {delay // 60}m {delay % 60}s before next account...")
            time.sleep(delay)

    log.info("Batch done!")


# ─────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────
def start_bot():
    log.info("")
    log.info("=" * 50)
    log.info("   Instagram Auto Poster Bot")
    log.info("=" * 50)
    log.info(f"   Source account : @{MAIN_USERNAME}")
    log.info(f"   Upload accounts: {len(UPLOAD_ACCOUNTS)}")
    log.info(f"   Posting times  : {', '.join(POSTING_TIMES)}")
    log.info(f"   Date filter    : posts from {SIX_MONTHS_AGO.strftime('%Y-%m-%d')} onwards")
    log.info("=" * 50)

    # Download on startup
    download_new_videos()

    # Re-download fresh videos daily at midnight
    schedule.every().day.at("00:01").do(download_new_videos)

    # Schedule uploads
    for t in POSTING_TIMES:
        schedule.every().day.at(t).do(upload_one_batch)
        log.info(f"Scheduled upload at {t}")

    log.info("\nBot running! Press Ctrl+C to stop.\n")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    start_bot()

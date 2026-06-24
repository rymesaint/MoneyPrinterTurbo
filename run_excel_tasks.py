import os
import sys
import csv
import time
import argparse
from datetime import datetime, timezone
from loguru import logger

# Ensure the project root is in the path for proper app imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.schema import VideoParams
from app.services import task as tm
from app.utils import utils

def get_youtube_uploads_count_today():
    # Read history file and count uploads for today's date
    history_file = os.path.join("storage", "youtube_upload_history.json")
    if not os.path.exists(history_file):
        return 0
    import json
    try:
        with open(history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
    except Exception:
        return 0
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    count = sum(1 for item in history if item.get("date") == today_str)
    return count

def record_youtube_upload():
    history_file = os.path.join("storage", "youtube_upload_history.json")
    os.makedirs("storage", exist_ok=True)
    import json
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            pass
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    history.append({"date": today_str, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to record upload history: {e}")

def load_tasks(csv_path):
    if not os.path.exists(csv_path):
        return []
    tasks = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tasks.append(row)
    return tasks

def save_tasks(csv_path, tasks, fieldnames):
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in tasks:
            writer.writerow(row)

def execute_task(row, youtube_schedule=False):
    logger.info(f"Starting scheduled task ID {row.get('id', 'unknown')}: {row.get('video_subject')}")
    
    # Map row fields to VideoParams
    video_subject = row.get("video_subject", "").strip()
    if not video_subject:
        raise ValueError("video_subject cannot be empty")
        
    video_script = row.get("video_script", "").strip()
    voice_name = row.get("voice_name", "").strip()
    
    try:
        voice_rate = float(row.get("voice_rate", "1.0"))
    except ValueError:
        voice_rate = 1.0
        
    bgm_file = row.get("bgm_file", "").strip()
    video_aspect_str = row.get("video_aspect", "9:16").strip()
    intro_video_path = row.get("intro_video_path", "").strip()
    schedule_time_str = row.get("schedule_time", "").strip()
    
    bgm_type = "random"
    if bgm_file:
        if bgm_file.lower() == "ccmixter":
            bgm_type = "ccmixter"
            bgm_file = ""
        else:
            bgm_type = "custom"

    # Formulate publish_at for YouTube scheduling
    publish_at = None
    if youtube_schedule and schedule_time_str:
        try:
            local_dt = datetime.strptime(schedule_time_str, "%Y-%m-%d %H:%M:%S").astimezone()
            publish_at = local_dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            logger.info(f"Scheduling YouTube upload for: {publish_at} (derived from local schedule_time: {schedule_time_str})")
        except Exception as e:
            logger.warning(f"Failed to parse schedule_time for YouTube scheduling: {e}")

    # Handle match_materials_to_script configuration from config.toml
    # Or default to True for maximum uniqueness/cohesion
    from app.config import config
    match_materials = config.app.get("match_materials_to_script", True)

    params = VideoParams(
        video_subject=video_subject,
        video_script=video_script,
        voice_name=voice_name,
        voice_rate=voice_rate,
        bgm_file=bgm_file,
        bgm_type=bgm_type,
        video_aspect=video_aspect_str,
        match_materials_to_script=match_materials,
        intro_video_path=intro_video_path if intro_video_path else None,
        publish_at=publish_at
    )
    
    task_id = f"sched-{row.get('id', utils.get_uuid())}"
    
    # Run the pipeline
    result = tm.start(task_id=task_id, params=params, stop_at="video")
    if not result:
        raise Exception("Task processing returned empty result")
    
    # Try to find output files or YouTube video IDs
    videos = result.get("videos", [])
    youtube_results = result.get("youtube_results", [])
    
    output_info = []
    if youtube_results:
        for yt in youtube_results:
            if yt.get("success"):
                output_info.append(f"YouTube ID: {yt.get('video_id')}")
            else:
                output_info.append(f"YouTube Error: {yt.get('error')}")
    
    if videos:
        output_info.append(f"File: {os.path.basename(videos[0])}")
        
    return ", ".join(output_info) if output_info else "Success"

def run_schedule(csv_path, youtube_schedule=False):
    if not os.path.exists(csv_path):
        example_path = "tasks_schedule.example.csv"
        if os.path.exists(example_path):
            logger.info(f"Creating {csv_path} from {example_path}")
            import shutil
            shutil.copy(example_path, csv_path)
        else:
            logger.error(f"Schedule file not found: {csv_path}. Please create it first.")
            return

    tasks = load_tasks(csv_path)
    if not tasks:
        logger.info("No tasks found in schedule.")
        return

    # Keep track of fieldnames to save correctly
    fieldnames = list(tasks[0].keys())
    
    updated = False
    for row in tasks:
        if row.get("status", "").strip().lower() != "pending":
            continue
            
        schedule_time_str = row.get("schedule_time", "").strip()
        should_run = False
        
        if youtube_schedule:
            should_run = True
        elif not schedule_time_str:
            should_run = True  # Run immediately if no time set
        else:
            try:
                schedule_time = datetime.strptime(schedule_time_str, "%Y-%m-%d %H:%M:%S")
                if datetime.now() >= schedule_time:
                    should_run = True
            except ValueError:
                logger.error(f"Invalid date format for task {row.get('id')}: '{schedule_time_str}'. Expected 'YYYY-MM-DD HH:MM:SS'")
                row["status"] = "failed"
                row["result"] = "Invalid date format"
                updated = True
                continue

        if should_run:
            # Check daily YouTube upload limit
            from app.config import config
            youtube_enabled = config.youtube.get("enabled", False)
            youtube_auto_upload = config.youtube.get("auto_upload", False)
            
            if youtube_enabled and youtube_auto_upload:
                max_uploads = config.youtube.get("max_uploads_per_day", 5)
                uploads_today = get_youtube_uploads_count_today()
                if uploads_today >= max_uploads:
                    logger.warning(f"Daily YouTube upload limit reached ({uploads_today}/{max_uploads}). Exiting program to prevent API quota/spam ban.")
                    sys.exit(0)

            # Mark running immediately & save to prevent race condition
            row["status"] = "running"
            save_tasks(csv_path, tasks, fieldnames)
            
            try:
                res_desc = execute_task(row, youtube_schedule=youtube_schedule)
                row["status"] = "completed"
                row["result"] = res_desc
                logger.success(f"Task {row.get('id')} completed successfully: {res_desc}")
                if "YouTube ID:" in res_desc:
                    record_youtube_upload()
            except Exception as e:
                row["status"] = "failed"
                row["result"] = str(e)
                logger.error(f"Task {row.get('id')} failed: {e}")
            
            updated = True
            save_tasks(csv_path, tasks, fieldnames)

    if not updated:
        logger.info("No pending tasks due for execution at this time.")

def main():
    parser = argparse.ArgumentParser(description="MoneyPrinterTurbo Excel/CSV Task Scheduler")
    parser.add_argument("--csv", default="tasks_schedule.csv", help="Path to schedule CSV file")
    parser.add_argument("--loop", action="store_true", help="Run in an infinite check loop")
    parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds for loop mode")
    parser.add_argument("--youtube-schedule", action="store_true", help="Generate all videos immediately and schedule them on YouTube using schedule_time")
    args = parser.parse_args()

    logger.info("Initializing task scheduler...")
    if args.loop:
        logger.info(f"Running in loop mode. Checking every {args.interval} seconds.")
        try:
            while True:
                run_schedule(args.csv, youtube_schedule=args.youtube_schedule)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")
    else:
        logger.info("Running in single-run mode.")
        run_schedule(args.csv, youtube_schedule=args.youtube_schedule)

if __name__ == "__main__":
    main()

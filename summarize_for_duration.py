#!/usr/bin/env python3
"""
Run the ChatFile summarizer for a fixed duration, then exit.

This is a separate, safe runner so it doesn't interfere with the
existing time-windowed daemon in summarize_transcoded_files.py.

Usage examples:
    # Run for 2 hours (default), check every 15s when idle
    python summarize_for_duration.py

    # Run for 90 minutes
    python summarize_for_duration.py --minutes 90

    # Customize idle sleep between checks
    python summarize_for_duration.py --minutes 120 --sleep 30
"""
import argparse
import time
from datetime import datetime, timedelta

# Reuse the existing batch logic without altering the main daemon
from summarize_transcoded_files import process_one_batch


def main():
    parser = argparse.ArgumentParser(description="Run summarizer for a fixed duration, then exit")
    parser.add_argument('--minutes', type=int, default=120, help='How long to run (in minutes). Default: 120')
    parser.add_argument('--sleep', type=int, default=15, help='Sleep seconds between checks when idle (default: 15)')
    args = parser.parse_args()

    duration = max(1, args.minutes)
    end_time = datetime.now() + timedelta(minutes=duration)

    print("🚀 Timed ChatFile Summarizer")
    print("=" * 40)
    print(f"⏲️  Will run for {duration} minutes (until {end_time.strftime('%H:%M')})")
    print("Press Ctrl+C to stop early")

    try:
        while datetime.now() < end_time:
            had_work = process_one_batch()
            # If we had work, short sleep to keep momentum; otherwise idle sleep
            time.sleep(1 if had_work else args.sleep)
    except KeyboardInterrupt:
        print("\n🛑 Stopping timed summarizer...")
    finally:
        print("✅ Timed run finished")


if __name__ == '__main__':
    main()

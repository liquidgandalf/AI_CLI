#!/usr/bin/env python3
"""
Background summarizer for processed ChatFile attachments.

This script finds files that have been successfully processed (has_been_processed=2)
but do not yet have an AI summary (ai_summary is NULL/empty), and generates a
short summary using the configured Ollama model.

Usage:
    python summarize_transcoded_files.py --once    # Process one batch and exit
    python summarize_transcoded_files.py --loop    # Run continuously (daemon mode)
    python summarize_transcoded_files.py --sleep 15 --loop

Status fields:
    status_summary: 0=pending, 1=processing, 2=done, 3=failed

Notes:
- We mark status_summary=1 before calling the AI to avoid double work.
- On success, we store ai_summary and set status_summary=2.
- On failure, we set status_summary=3 and move on; no infinite loops.
"""
import os
import sys
import time
import argparse
import json
import requests
from typing import Optional

# Ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, ChatFile

# Config (kept consistent with app.py defaults)
OLLAMA_URL = os.environ.get('OLLAMA_URL', "http://localhost:11434/api/generate")
DEFAULT_MODEL = os.environ.get('OLLAMA_MODEL', "gpt-oss:20b")
AI_TIMEOUT_SECONDS = int(os.environ.get('AI_TIMEOUT_SECONDS', '600'))
MAX_INPUT_CHARS = int(os.environ.get('SUMMARY_MAX_INPUT_CHARS', '24000'))  # keep prompt manageable
SUMMARY_TARGET_WORDS = int(os.environ.get('SUMMARY_TARGET_WORDS', '150'))

SYSTEM_PROMPT = (
    "You are a helpful assistant. Summarize the provided file content clearly and concisely, "
    "focusing on key points, structure, and any actionable items. If the content appears to be "
    "a transcript, provide a brief overview with main topics. Keep it around "
    f"{SUMMARY_TARGET_WORDS} words."
)


def build_prompt(content: str) -> str:
    # Truncate to avoid context overflow
    text = content.strip()
    if len(text) > MAX_INPUT_CHARS:
        head = text[: MAX_INPUT_CHARS // 2]
        tail = text[-MAX_INPUT_CHARS // 2 :]
        text = head + "\n... [content truncated] ...\n" + tail
    return (
        f"System: {SYSTEM_PROMPT}\n\n"
        "User: Please summarize the following file content.\n\n"
        f"CONTENT:\n{text}\n\n"
        "Assistant:"
    )


def call_ollama(prompt: str) -> Optional[str]:
    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "stream": False,
        # Optional: set options to keep responses short-ish
        "options": {"temperature": 0.2}
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=AI_TIMEOUT_SECONDS)
        resp.raise_for_status()
        data = resp.json()
        # Ollama /api/generate returns {'response': '...'} when stream=False
        return data.get("response") or data.get("text") or ""
    except Exception as e:
        print(f"❌ AI call failed: {e}")
        return None


def get_next_to_summarize(db) -> Optional[ChatFile]:
    # Only files that were processed successfully and have content
    q = (
        db.query(ChatFile)
        .filter(ChatFile.has_been_processed == 2)
        .filter((ChatFile.ai_summary == None) | (ChatFile.ai_summary == ""))
        .filter((ChatFile.status_summary == None) | (ChatFile.status_summary == 0) | (ChatFile.status_summary == 3))
        .order_by(ChatFile.upload_date.desc())
    )
    chat_file = q.first()
    if not chat_file:
        return None
    # Mark as processing and commit so other workers won't pick it up
    chat_file.status_summary = 1
    db.commit()
    return chat_file


def summarize_one(chat_file: ChatFile) -> bool:
    if not chat_file.transcoded_raw_file:
        print(f"⚠️  No transcoded_raw_file for file ID {chat_file.id}, skipping")
        return False
    prompt = build_prompt(chat_file.transcoded_raw_file)
    summary = call_ollama(prompt)
    if summary is None or not summary.strip():
        return False
    chat_file.ai_summary = summary.strip()
    chat_file.status_summary = 2
    return True


def process_one_batch() -> bool:
    db = get_db()
    try:
        item = get_next_to_summarize(db)
        if not item:
            print("📭 No files pending summarization")
            return False
        print(f"🧾 Summarizing file ID={item.id} name={item.original_filename}")
        ok = summarize_one(item)
        if ok:
            db.commit()
            print("✅ Summary saved")
        else:
            # mark failed
            item.status_summary = 3
            # append note in human_notes but don't erase existing notes
            note = (item.human_notes or "") + f"\nSummary failed at runtime."
            item.human_notes = note.strip()
            db.commit()
            print("💥 Summary failed; marked as failed")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Summarize processed ChatFile contents")
    parser.add_argument('--once', action='store_true', help='Process one batch and exit')
    parser.add_argument('--loop', action='store_true', help='Run continuously (daemon mode)')
    parser.add_argument('--sleep', type=int, default=15, help='Sleep seconds between batches in loop mode (default: 15)')
    args = parser.parse_args()

    if not args.once and not args.loop:
        print("❌ Please specify either --once or --loop")
        sys.exit(1)

    print("🚀 ChatFile Summarizer")
    print("=" * 40)

    if args.once:
        print("📋 Running in one-shot mode")
        had_work = process_one_batch()
        print("✅ Completed" if had_work else "📭 Nothing to do")
    else:
        print(f"🔄 Running in daemon mode (checking every {args.sleep}s)")
        print("Press Ctrl+C to stop")
        try:
            while True:
                had_work = process_one_batch()
                time.sleep(1 if had_work else args.sleep)
        except KeyboardInterrupt:
            print("\n🛑 Stopping summarizer...")
            print("✅ Shutdown complete")


if __name__ == '__main__':
    main()

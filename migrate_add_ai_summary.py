#!/usr/bin/env python3
"""
Add ai_summary and status_summary columns to chat_files if they don't exist.
Safe for SQLite. Run once: python migrate_add_ai_summary.py
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'ai_chat.db')

COLUMNS = {
    'ai_summary': "TEXT",
    'status_summary': "INTEGER DEFAULT 0 NOT NULL"
}

def column_exists(conn, table, column):
    cur = conn.execute(f"PRAGMA table_info({table})")
    return any(row[1] == column for row in cur.fetchall())

def main():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Make sure you've initialized it.")
        return
    conn = sqlite3.connect(DB_PATH)
    try:
        added = []
        for col, coltype in COLUMNS.items():
            if not column_exists(conn, 'chat_files', col):
                sql = f"ALTER TABLE chat_files ADD COLUMN {col} {coltype}"
                conn.execute(sql)
                added.append(col)
        if added:
            conn.commit()
            print(f"Added columns: {', '.join(added)}")
        else:
            print("Columns already exist. No changes.")
    finally:
        conn.close()

if __name__ == '__main__':
    main()

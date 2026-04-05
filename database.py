# database.py
import sqlite3
from datetime import datetime

DB_PATH = "study.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feature TEXT,
        score INTEGER,
        total INTEGER,
        difficulty TEXT,
        topic TEXT,
        source_chunk INTEGER,
        timestamp TEXT
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS flashcard_reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        front TEXT,
        back TEXT,
        correct INTEGER,
        timestamp TEXT
    )""")
    conn.commit()
    conn.close()

def log_progress(feature, score, total, difficulty=None, topic=None, source_chunk=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO progress (feature, score, total, difficulty, topic, source_chunk, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (feature, score, total, difficulty, topic, source_chunk, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def log_flashcard_review(front, back, correct):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO flashcard_reviews (front, back, correct, timestamp) VALUES (?, ?, ?, ?)",
        (front, back, int(bool(correct)), datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_progress(limit=50):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT feature, score, total, difficulty, topic, timestamp FROM progress ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
import sqlite3

def init_db():
    conn = sqlite3.connect("study.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        feature TEXT,
        score INTEGER,
        total INTEGER
    )""")
    conn.commit()
    conn.close()

def log_progress(feature, score, total):
    conn = sqlite3.connect("study.db")
    c = conn.cursor()
    c.execute("INSERT INTO progress (feature, score, total) VALUES (?, ?, ?)",
              (feature, score, total))
    conn.commit()
    conn.close()

def get_progress():
    conn = sqlite3.connect("study.db")
    c = conn.cursor()
    c.execute("SELECT feature, score, total FROM progress")
    rows = c.fetchall()
    conn.close()
    return rows

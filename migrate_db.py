import sqlite3

conn = sqlite3.connect("study.db")
c = conn.cursor()

for sql in [
    "ALTER TABLE progress ADD COLUMN difficulty TEXT",
    "ALTER TABLE progress ADD COLUMN topic TEXT",
    "ALTER TABLE progress ADD COLUMN source_chunk INTEGER",
    "ALTER TABLE progress ADD COLUMN timestamp TEXT"
]:
    try:
        c.execute(sql)
        print(f"Added: {sql}")
    except Exception as e:
        print(f"Skipped: {sql} ({e})")

conn.commit()
conn.close()
print("Migration complete")
import sqlite3

conn = sqlite3.connect("database/vct.db")
cursor = conn.cursor()

tables = ["events", "matches", "maps", "players"]

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table}: {count:,}")

conn.close()
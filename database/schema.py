import sqlite3
from pathlib import Path

DB_PATH = Path("database/vct.db")

DB_PATH.parent.mkdir(exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# -----------------------------
# Events
# -----------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY,
    event_name TEXT
)
""")

# -----------------------------
# Matches
# -----------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS matches (
    match_id INTEGER PRIMARY KEY,
    event_id INTEGER,
    date TEXT,
    team1 TEXT,
    team2 TEXT,
    winner TEXT,

    FOREIGN KEY(event_id)
        REFERENCES events(event_id)
)
""")

# -----------------------------
# Maps
# -----------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS maps (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    match_id INTEGER,

    map_name TEXT,

    team1_score INTEGER,

    team2_score INTEGER,

    winner TEXT,

    FOREIGN KEY(match_id)
        REFERENCES matches(match_id)
)
""")

# -----------------------------
# Players
# -----------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS players (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    match_id INTEGER,

    map_name TEXT,

    team TEXT,

    player TEXT,

    agent TEXT,

    rating REAL,

    acs INTEGER,

    kills INTEGER,

    deaths INTEGER,

    assists INTEGER,

    adr INTEGER,

    kast REAL,

    hs_pct REAL,

    fk INTEGER,

    fd INTEGER,

    FOREIGN KEY(match_id)
        REFERENCES matches(match_id)
)
""")

conn.commit()
conn.close()

print("Database created successfully!")
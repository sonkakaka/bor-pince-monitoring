"""
Adatbázis inicializáló szkript (opcionális, a subscriber automatikusan létrehozza)
"""

import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "./data/pince.db")


def init():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meresek (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            homerseklet REAL,
            paratartalom REAL,
            homerseklet_riasztas INTEGER DEFAULT 0,
            paratartalom_riasztas INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS riasztasok (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            tipus TEXT NOT NULL,
            uzenet TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print(f"Adatbázis inicializálva: {DB_PATH}")


if __name__ == "__main__":
    init()
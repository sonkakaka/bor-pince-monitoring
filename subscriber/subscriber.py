"""
MQTT Subscriber
Fogadja az MQTT üzeneteket, feldolgozza, tárolja SQLite-ban,
és riasztást generál küszöbérték-túllépés esetén.
"""

import json
import os
import sqlite3
import sys
from datetime import datetime

import paho.mqtt.client as mqtt

# Konfiguráció
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
DB_PATH = os.getenv("DB_PATH", "/data/pince.db")
TOPIC_BASE = "pince/szenzor1"

# Küszöbértékek (vörösbor)
HOMERSEKLET_MIN = 14.0
HOMERSEKLET_MAX = 16.0
PARATARTALOM_MIN = 70.0
PARATARTALOM_MAX = 80.0


def init_db():
    """Adatbázis inicializálása."""
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
    print(f"[SUBSCRIBER] Adatbázis inicializálva: {DB_PATH}")


def mentes(timestamp, homerseklet, paratartalom, h_riasztas, p_riasztas):
    """Mérés mentése az adatbázisba."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meresek (timestamp, homerseklet, paratartalom,
                            homerseklet_riasztas, paratartalom_riasztas)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, homerseklet, paratartalom, h_riasztas, p_riasztas))
    conn.commit()
    conn.close()


def riasztas_mentes(timestamp, tipus, uzenet):
    """Riasztás mentése az adatbázisba."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO riasztasok (timestamp, tipus, uzenet)
        VALUES (?, ?, ?)
    """, (timestamp, tipus, uzenet))
    conn.commit()
    conn.close()


# Állapot (utolsó mérés)
allapot = {
    "homerseklet": None,
    "paratartalom": None,
    "timestamp": None,
}


def on_connect(client, userdata, flags, rc):
    print(f"[SUBSCRIBER] Csatlakozva (rc={rc})")
    client.subscribe(f"{TOPIC_BASE}/#", qos=1)


def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        payload = json.loads(msg.payload.decode())
    except json.JSONDecodeError:
        print(f"[SUBSCRIBER] Hibás JSON: {msg.payload}")
        return

    if topic.endswith("/homerseklet"):
        allapot["homerseklet"] = payload["value"]
        allapot["timestamp"] = payload["timestamp"]
        print(f"[SUBSCRIBER] Hőmérséklet: {payload['value']}°C")
    elif topic.endswith("/paratartalom"):
        allapot["paratartalom"] = payload["value"]
        allapot["timestamp"] = payload["timestamp"]
        print(f"[SUBSCRIBER] Páratartalom: {payload['value']}%")
    elif topic.endswith("/anomalia"):
        print(f"[SUBSCRIBER] ANOMÁLIA jelzés!")
        riasztas_mentes(payload["timestamp"], "anomalia", "Szimulált anomália")
        return

    # Ha mindkét érték megvan, mentjük
    if allapot["homerseklet"] is not None and allapot["paratartalom"] is not None:
        h = allapot["homerseklet"]
        p = allapot["paratartalom"]
        ts = allapot["timestamp"]

        h_riasztas = 1 if (h < HOMERSEKLET_MIN or h > HOMERSEKLET_MAX) else 0
        p_riasztas = 1 if (p < PARATARTALOM_MIN or p > PARATARTALOM_MAX) else 0

        mentes(ts, h, p, h_riasztas, p_riasztas)

        if h_riasztas:
            uzenet = f"Hőmérséklet riasztás: {h}°C (határ: {HOMERSEKLET_MIN}-{HOMERSEKLET_MAX})"
            print(f"[RIASZTÁS] {uzenet}")
            riasztas_mentes(ts, "homerseklet", uzenet)

        if p_riasztas:
            uzenet = f"Páratartalom riasztás: {p}% (határ: {PARATARTALOM_MIN}-{PARATARTALOM_MAX})"
            print(f"[RIASZTÁS] {uzenet}")
            riasztas_mentes(ts, "paratartalom", uzenet)


def main():
    init_db()

    client = mqtt.Client(client_id="bor-subscriber")
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[SUBSCRIBER] Csatlakozás: {MQTT_BROKER}:{MQTT_PORT}")
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print(f"[SUBSCRIBER] Hiba: {e}")
        sys.exit(1)

    client.loop_forever()


if __name__ == "__main__":
    main()
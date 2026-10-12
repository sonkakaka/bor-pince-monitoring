"""
MQTT Publisher
A szimulátor által generált adatokat publikálja az MQTT brokerre.
"""

import time
import json
import os
import sys
from datetime import datetime

import paho.mqtt.client as mqtt

# A szimulátor importálása (szülő mappából)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'simulator'))
from szimulator import PinceSzimulator


# Konfiguráció
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
TOPIC_BASE = "pince/szenzor1"
PUBLISH_INTERVAL = 5  # másodperc


def main():
    print(f"[PUBLISHER] Csatlakozás: {MQTT_BROKER}:{MQTT_PORT}")

    # MQTT kliens létrehozása
    client = mqtt.Client(client_id="bor-publisher")

    # Csatlakozás
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print("[PUBLISHER] Csatlakozva!")
    except Exception as e:
        print(f"[PUBLISHER] Hiba a csatlakozáskor: {e}")
        sys.exit(1)

    client.loop_start()

    # Szimulátor
    szim = PinceSzimulator()

    try:
        while True:
            # Mérés generálása
            adat = szim.meres()

            # Hőmérséklet publikálása
            client.publish(
                f"{TOPIC_BASE}/homerseklet",
                json.dumps({
                    "value": adat["homerseklet"],
                    "unit": "C",
                    "timestamp": adat["timestamp"],
                }),
                qos=1,
            )

            # Páratartalom publikálása
            client.publish(
                f"{TOPIC_BASE}/paratartalom",
                json.dumps({
                    "value": adat["paratartalom"],
                    "unit": "%RH",
                    "timestamp": adat["timestamp"],
                }),
                qos=1,
            )

            # Anomália jelzés
            if adat["anomalia"]:
                client.publish(
                    f"{TOPIC_BASE}/anomalia",
                    json.dumps({
                        "aktiv": True,
                        "timestamp": adat["timestamp"],
                    }),
                    qos=1,
                )
                print(f"[PUBLISHER] ANOMÁLIA: {adat}")
            else:
                print(f"[PUBLISHER] Küldve: T={adat['homerseklet']}°C, RH={adat['paratartalom']}%")

            time.sleep(PUBLISH_INTERVAL)

    except KeyboardInterrupt:
        print("\n[PUBLISHER] Leállítás...")
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
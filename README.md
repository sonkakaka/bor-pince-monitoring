# Bor Pince Monitoring Rendszer

Vörösbor-érlelő pince hőmérséklet- és páratartalom-monitoring rendszere MQTT-alapú publish/subscribe adatút segítségével.

## Követelmények

- Vörösbor érlelés: **14–16 °C**, **70–80% RH**
- Valós idejű monitoring
- Riasztás küszöbérték túllépés esetén
- Adatok tárolása és megjelenítése

## Architektúra
```
[Szenzor szimulátor] → [MQTT Publisher] → [Mosquitto Broker]
                                                    ↓
                                            [Subscriber] → [SQLite]
                                                    ↓
                                              [Grafana Dashboard]
```

## Technológiák

| Komponens | Eszköz |
|-----------|--------|
| Nyelv | Python 3.11 |
| MQTT kliens | paho-mqtt |
| Broker | Eclipse Mosquitto 2.0 |
| Adatbázis | SQLite |
| Dashboard | Grafana |
| Konténerizáció | Docker + docker-compose |

## Telepítés és futtatás

### Előfeltételek

- Docker Desktop
- Docker Compose
- Python 3.11+ (fejlesztéshez)

### Indítás

```bash
# Az összes szolgáltatás indítása
docker-compose up -d

# Naplók megtekintése
docker-compose logs -f

# Leállítás
docker-compose down
```

### Elérés

- **Grafana dashboard:** http://localhost:3000 (admin / admin)
- **MQTT broker:** localhost:1883
- **MQTT WebSocket:** localhost:9001

## Projekt struktúra

```
bor-pince-monitoring/
├── docker-compose.yml
├── mosquitto/
├── simulator/
├── publisher/
├── subscriber/
├── database/
├── dashboard/
└── docs/
```

## Szerző

Kiss Patrik (J1OM3G)
Mérnökinformatikus, Széchenyi István Egyetem
Ipar 4.0 tárgy, 2026/27-1
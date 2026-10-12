"""
Bor pince szimulátor
Vörösbor érlelés: 14-16°C, 70-80% RH
Valósághű adatokat generál: napi ciklus, zaj, drift, ritka anomáliák
"""

import random
import math
from datetime import datetime


class PinceSzimulator:
    def __init__(self):
        # Alapértékek (ideális vörösbor pince)
        self.alap_homerseklet = 15.0      # °C
        self.alap_paratartalom = 75.0     # % RH

        # Napi ciklus amplitúdó
        self.napi_amplitude_h = 0.3       # °C
        self.napi_amplitude_rh = 1.5      # %

        # Zaj (szenzor mérési bizonytalanság)
        self.zaj_h = 0.1                  # ±0.1°C
        self.zaj_rh = 0.5                 # ±0.5%

        # Drift (lassú változás)
        self.drift_h = 0.0
        self.drift_rh = 0.0
        self.drift_sebesseg_h = 0.001
        self.drift_sebesseg_rh = 0.005

        # Anomália
        self.anomalia_esely = 0.01
        self.anomalia_aktiv = False
        self.anomalia_hatralevo = 0

    def _napi_ciklus(self):
        """Napi hőmérséklet-ingadozás (hajnalban hidegebb)."""
        ora = datetime.now().hour
        fazis = (ora - 4) / 24 * 2 * math.pi
        return math.sin(fazis)

    def _general_anomaliat(self):
        """Ritka anomália (pl. ajtó nyitva, hűtés hiba)."""
        if not self.anomalia_aktiv and random.random() < self.anomalia_esely:
            self.anomalia_aktiv = True
            self.anomalia_hatralevo = random.randint(3, 10)
            print(f"[ANOMÁLIA] Kezdődik! Hátralévő mérések: {self.anomalia_hatralevo}")
        elif self.anomalia_aktiv:
            self.anomalia_hatralevo -= 1
            if self.anomalia_hatralevo <= 0:
                self.anomalia_aktiv = False

    def meres(self):
        """Egy mérési pont generálása."""
        self.drift_h += random.uniform(-self.drift_sebesseg_h, self.drift_sebesseg_h)
        self.drift_rh += random.uniform(-self.drift_sebesseg_rh, self.drift_sebesseg_rh)

        self.drift_h = max(-1.0, min(1.0, self.drift_h))
        self.drift_rh = max(-3.0, min(3.0, self.drift_rh))

        ciklus = self._napi_ciklus()
        self._general_anomaliat()

        anomalia_hatas_h = 0
        anomalia_hatas_rh = 0
        if self.anomalia_aktiv:
            anomalia_hatas_h = random.uniform(1.0, 3.0)
            anomalia_hatas_rh = random.uniform(-5.0, -2.0)

        homerseklet = (
            self.alap_homerseklet
            + ciklus * self.napi_amplitude_h
            + self.drift_h
            + random.gauss(0, self.zaj_h)
            + anomalia_hatas_h
        )

        paratartalom = (
            self.alap_paratartalom
            + ciklus * self.napi_amplitude_rh
            + self.drift_rh
            + random.gauss(0, self.zaj_rh)
            + anomalia_hatas_rh
        )

        return {
            "homerseklet": round(homerseklet, 2),
            "paratartalom": round(paratartalom, 2),
            "timestamp": datetime.now().isoformat(),
            "anomalia": self.anomalia_aktiv,
        }


if __name__ == "__main__":
    szim = PinceSzimulator()
    for i in range(10):
        print(szim.meres())
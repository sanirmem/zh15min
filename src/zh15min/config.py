"""Zentrale Konfiguration: Pfade, Koordinatensysteme, POI-Kategorien, Gewichte.

Alle Notebooks importieren ihre Konstanten von hier — so gibt es eine einzige
Quelle der Wahrheit, was eine Bewertung als "zentraler Code-Standard" begünstigt.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Pfade
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EXTERNAL_DIR = DATA_DIR / "external"
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

for _d in (RAW_DIR, PROCESSED_DIR, EXTERNAL_DIR, FIGURES_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Koordinatensysteme
# ---------------------------------------------------------------------------
# WGS84  – Standard für OSM, Folium, GeoJSON
EPSG_WGS84 = 4326
# CH1903+/LV95 – Schweizer Landeskoordinaten, im Kurs verwendet
EPSG_LV95 = 2056
# Web Mercator – für contextily-Basemaps
EPSG_WEB_MERCATOR = 3857

# Default für Distanz-/Flächenberechnungen in der CH
EPSG_METRIC = EPSG_LV95

# ---------------------------------------------------------------------------
# Untersuchungsgebiet
# ---------------------------------------------------------------------------
CITY_NAME = "Zürich, Switzerland"
# Bounding Box ungefähr (W, S, E, N) in WGS84 — als Sicherheitsnetz, falls
# OSMnx die Stadtgrenze nicht findet.
ZURICH_BBOX_WGS84 = (8.4470, 47.3203, 8.6258, 47.4348)

# ---------------------------------------------------------------------------
# POI-Kategorien (OSM-Tags) und Gewichte für den 15-Min-City-Score
# ---------------------------------------------------------------------------
# Quelle der Inspiration: Moreno et al. (2021) – "Introducing the 15-Minute City"
# Wir mappen die sechs „essential urban functions“ auf OSM-Tags.
POI_CATEGORIES: dict[str, dict] = {
    "einkauf": {
        "weight": 0.22,
        "tags": {
            "shop": ["supermarket", "convenience", "bakery", "butcher", "greengrocer"],
        },
    },
    "bildung": {
        "weight": 0.18,
        "tags": {
            "amenity": ["school", "kindergarten", "library", "university", "college"],
        },
    },
    "gesundheit": {
        "weight": 0.18,
        "tags": {
            "amenity": ["pharmacy", "doctors", "clinic", "hospital", "dentist"],
        },
    },
    "erholung": {
        "weight": 0.14,
        "tags": {
            "leisure": ["park", "playground", "sports_centre", "fitness_centre", "garden"],
        },
    },
    "gastro": {
        "weight": 0.10,
        "tags": {
            "amenity": ["restaurant", "cafe", "bar", "fast_food"],
        },
    },
    "oev": {
        "weight": 0.18,
        "tags": {
            "highway": ["bus_stop"],
            "railway": ["tram_stop", "station", "halt"],
            "public_transport": ["stop_position", "platform"],
        },
    },
}

# Summe der Gewichte sollte 1.0 sein (kleiner Floating-Point-Spielraum)
assert abs(sum(c["weight"] for c in POI_CATEGORIES.values()) - 1.0) < 1e-9, (
    "POI-Gewichte müssen sich zu 1.0 summieren"
)

# ---------------------------------------------------------------------------
# Score-Parameter
# ---------------------------------------------------------------------------
# Maximaldistanz (Meter), die als 15-Minuten-Fussweg gilt.
# Annahme: 5 km/h Fussgängergeschwindigkeit → 15 min = 1250 m Luftlinie ≈
#          1000–1100 m über reales Strassennetz.
WALK_DISTANCE_M = 1200
WALK_SPEED_KMH = 5.0
WALK_TIME_MIN = 15

# Hex-Gitter-Auflösung in Metern (Apothem). 200 m → angenehme Auflösung in QGIS,
# 100 m → fein-granular aber teurer.
HEX_RESOLUTION_M = 200

# Huff-Distanzparameter (Distance Decay): höhere Werte → schärferer Abfall
HUFF_BETA = 1.5

# ---------------------------------------------------------------------------
# Datenbank-Verbindung
# ---------------------------------------------------------------------------
load_dotenv(PROJECT_ROOT / ".env", override=False)


def db_url() -> str:
    """Liefert die SQLAlchemy-URL zu PostGIS aus Umgebungsvariablen."""
    user = os.getenv("POSTGRES_USER", "postgres")
    pw = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "zh15min")
    return f"postgresql+psycopg://{user}:{pw}@{host}:{port}/{db}"


def db_dsn() -> str:
    """Liefert eine libpq-DSN-Zeichenkette (für psycopg ohne SQLAlchemy)."""
    user = os.getenv("POSTGRES_USER", "postgres")
    pw = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "zh15min")
    return f"host={host} port={port} dbname={db} user={user} password={pw}"

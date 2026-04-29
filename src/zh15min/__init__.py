"""zh15min — Geo-Algorithmus zur Bewertung der 15-Minuten-Erreichbarkeit in Zürich.

Modul-Aufbau:
    config   – Pfade, EPSG-Codes, POI-Kategorien, Score-Gewichte.
    db       – PostGIS-Verbindung (psycopg + SQLAlchemy/GeoAlchemy2).
    osm      – OSM-Download und POI-Extraktion (OSMnx).
    grid     – Hex-/Quadratgitter über die Stadtgrenze.
    isochron – Walking-Isochronen via OSMnx-Strassengraph.
    score    – Distanzgewichteter 15-Min-City-Score (Huff-Ansatz).
    viz      – Matplotlib- und Folium-Helfer.
"""

__version__ = "0.1.0"

# The 15-Minute City Intelligence — Zürich

> Ein Geo-Algorithmus zur Bewertung der „15-Minuten-Erreichbarkeit“ und zur Identifikation von Versorgungslücken in der Stadt Zürich.

**Modul:** Einsatz von Geodaten in Marketing (FS 2026, Dr. Mario Gellrich, ZHAW)
**Gruppe:** 3 Personen
**Abgabe:** 27.05.2026

---

## 1. Projekt-Idee in einem Satz

Wir berechnen für **744 hexagonale Analyse-Zellen (200 m Apothem)** über der Stadt Zürich einen **15-Minute-City-Score (0 – 100)**, der ausdrückt, wie viele Einrichtungen des täglichen Bedarfs (Einkauf, Bildung, Gesundheit, Erholung, Gastro, ÖV) innerhalb eines 15-minütigen Fussweges erreichbar sind — und aggregieren ihn auf die **34 offiziellen Stadt-Zürich-Quartiere**, um **Versorgungslücken** und **Investitionschancen** im Vergleich zu Bevölkerungsdichte (BFS STATPOP, Hektarraster) und Median-Mietpreis sichtbar zu machen.

## 2. Forschungsfrage & Hypothesen

**Forschungsfrage:** *In welchen Quartieren Zürichs klaffen die grössten Lücken zwischen Wohnungsdichte und täglicher Infrastruktur?*

- **H1:** Der 15-Min-Score korreliert positiv mit dem Median-Mietpreis pro Quartier (Stadt Zürich Open Data).
- **H1a (Robustness):** Der 15-Min-Score korreliert negativ mit der Distanz zum Hauptbahnhof — methodisch sauberer Proxy ohne Marktdaten-Confounder.
- **H2 („Wüsteneffekt“):** Es existieren Quartiere mit hoher Bevölkerungsdichte aber unterdurchschnittlichem Score.

## 3. Toolchain (im Kurs verwendet)

| Layer | Tool | Verwendung |
|---|---|---|
| Datenquelle | OpenStreetMap via OSMnx (Overpass-API) | POIs (6 Kategorien), Stadtgrenze, Walking-Graph |
| Datenquelle | Geofabrik `switzerland-latest.osm.pbf` (optional) | Vollständiges OSM für `osm2pgsql`-PostGIS-Import |
| Datenquelle | BFS STATPOP 2023 | Bevölkerungsdichte (Hektar-Raster) |
| Datenquelle | Stadt Zürich Open Data | Statistische Quartiere, Immobilien-Index |
| Datenquelle | swisstopo / GeoAdmin | Stadtgrenze Zürich, Hintergrundkarten |
| Datenquelle | swisstopo SwissALTI3D | Digitales Höhenmodell (2 m) für topografische Score-Erweiterung |
| DB | PostgreSQL 16 + PostGIS 3.4 | Zentrale Speicherung, räumliche Joins, SQL-Analysen |
| Import | `osm2pgsql` | OSM-PBF → PostGIS-Schema (`planet_osm_point`, `planet_osm_polygon`, `planet_osm_line`) |
| Routing | OSMnx + NetworkX | Walking-Isochronen (5/10/15 Min), Dijkstra |
| Topografie | rasterio + pyproj + Tobler-Hiking-Funktion | Steigungs-abhängige Walking-Zeiten pro Edge |
| Analyse | Python (GeoPandas, Pandas, NumPy, Shapely, scipy) | Score-Berechnung (Huff-Ansatz, KDTree, single_source_dijkstra) |
| Visualisierung | Folium, Matplotlib, contextily | Web- und Print-Karten |
| Visualisierung | QGIS 3.40 LTR | 3D-Map (Score als Höhe), Print Layout |
| Doku | Jupyter, Markdown | Reproduzierbare Notebooks |

## 4. Setup (Reproduzierbarkeit)

### 4.1 Python-Umgebung

```bash
# Klonen
git clone https://github.com/sanirmem/zh15min.git
cd zh15min

# Virtuelle Umgebung
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 4.2 PostGIS (Docker)

```bash
cp .env.example .env               # Passwörter ggf. anpassen
docker compose up -d
# pgAdmin öffnen:  http://localhost:5050
# Postgres-Port:   5432
```

### 4.3 OSM-Daten herunterladen

```bash
# wird auch in Notebook 01 automatisch gemacht
curl -L -o data/raw/switzerland-latest.osm.pbf \
  https://download.geofabrik.de/europe/switzerland-latest.osm.pbf
```

### 4.4 Notebooks ausführen

Reihenfolge:

1. `01_load_osm.ipynb` – OSM-POIs für Zürich extrahieren
2. `02_streetnet_statpop.ipynb` – Walking-Graph + Bevölkerungsraster
3. `02b_elevation.ipynb` – ⭐ Höhen-Anreicherung des Walking-Graphs (SwissALTI3D)
4. `03_postgis_import.ipynb` – Alles in PostGIS laden
5. `04_isochrones.ipynb` – 15-Min-Isochronen je Hex-Zelle
6. `05_score.ipynb` – Huff-gewichteter 15-Min-Score (flach, Luftlinie)
7. `06_gap_analysis.ipynb` – Versorgungslücken & Hypothesen-Test
8. `06b_delta.ipynb` – ⭐ Topografischer Score (Tobler) vs. flach — Δ-Visualisierung
9. `07_visualization.ipynb` – Folium-Map + statische Plots

### 4.5 Topografische Erweiterung (optional, für Notebooks 02b + 06b)

Der topografische Score nutzt das **digitale Höhenmodell SwissALTI3D von swisstopo**, um den Walking-Graph mit Steigungs-Information anzureichern und mit der **Tobler-Hiking-Funktion** auf realistische Walking-Zeiten an Hängen zu kommen. Vorteil gegenüber der flachen 5-km/h-Annahme: Hangzonen wie Zürichberg, Hönggerberg, Käferberg und Üetliberg werden korrekt als langsamer abgebildet.

**DEM beschaffen** (Login bei swisstopo erforderlich, kann nicht automatisiert werden):

1. <https://www.swisstopo.admin.ch/de/geodata/height/alti3d.html> → "swissALTI3D Daten beziehen"
2. Auswahl mit Gemeinde **Zürich (ZH)**, Format **GeoTIFF** (oder COG), Auflösung **2 m**, CRS **LV95**, Zeitstand "Aktuell"
3. "Suchen" → bei "Zu viele Ergebnisse" auf **„Alle Links exportieren"** klicken → URL-Liste in `data/external/swissalti3d_zh_links.csv` ablegen
4. Download und Merge automatisiert:

```bash
python scripts/download_dem_tiles.py data/external/swissalti3d_zh_links.csv
python scripts/merge_dem.py
# → erzeugt data/external/swissalti3d_zh.tif (~57 MB)
```

5. Notebooks `02b_elevation.ipynb` und `06b_delta.ipynb` ausführen.

**Performance-Check vor dem 06b-Lauf** (geschätzt 30–60 s auf Laptop):

```bash
python scripts/benchmark_topo_score.py
```

**Tests:**

```bash
pip install "pytest>=8.0"
pytest tests/test_tobler.py -v
```

## 5. Repository-Struktur

```
zh15min/
├── data/
│   ├── raw/            # Rohdaten (nicht versioniert, .gitignore)
│   ├── processed/      # GeoPackages, CSV-Outputs der Notebooks
│   └── external/       # Stadtgrenze, STATPOP, Open Data Zürich
├── notebooks/          # 01–07 + 02b/06b (Topo-Erweiterung) — 9 Notebooks
├── src/zh15min/        # Wiederverwendbarer Python-Code (Module)
├── sql/                # PostGIS-Schema, Views, Queries
├── qgis/               # QGIS-Projektdatei (.qgz) + Style-Dateien
├── reports/            # Slides, PDF-Export, Figuren
├── docs/               # Datenquellen, KI-Nutzung, Methoden-Details
├── docker-compose.yml  # PostGIS + pgAdmin
├── requirements.txt
├── .env.example
└── README.md
```

## 6. Bewertungs-Mapping

| Kriterium (Gewichtung) | Wo erfüllt |
|---|---|
| Technische Umsetzung & Standards (15 %) | `src/zh15min/`, Notebooks, gepinnte `requirements.txt` |
| Repo-Organisation (5 %) | klare Ordnerstruktur s. o. |
| Dokumentation (10 %) | dieses README + Markdown-Zellen in jedem Notebook + `docs/` |
| Reproduzierbarkeit (5 %) | Docker-Compose, `.env.example`, automatischer Daten-Download |
| Versionierung (5 %) | sinnvolle Commits, `.gitignore`, Branches pro Notebook |

## 7. KI-Einsatz

Die Nutzung von Claude / ChatGPT 5.x ist transparent in [`docs/ki_einsatz.md`](docs/ki_einsatz.md) dokumentiert (Code-Optimierung, Hypothesen-Generierung, Datenquellen-Recherche).

## 8. Lizenz & Datenquellen

- OSM-Daten: © OpenStreetMap-Mitwirkende, ODbL
- BFS STATPOP: © Bundesamt für Statistik
- Stadt Zürich Open Data: CC BY 4.0
- swisstopo SwissALTI3D: © swisstopo (frei mit Quellenangabe)

Code dieses Repositorys: MIT.

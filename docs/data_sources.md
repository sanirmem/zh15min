# Datenquellen — Wo kommen unsere Daten her?

Dieses Dokument erklärt, **welche Daten wir benutzen, wo sie herkommen, wie sie lizenziert sind und wie ihr sie ohne Vorwissen herunterladen könnt**. Es ist absichtlich ausführlich, damit ihr in der Präsentation jede Quelle benennen und verteidigen könnt.

---

## Übersicht

| # | Quelle | Was wir daraus nehmen | Format | CRS | Lizenz |
|---|---|---|---|---|---|
| 1 | OpenStreetMap via **OSMnx / Overpass-API** | POIs (Supermarkt, Schule, Apotheke, ÖV, Park …), Stadtgrenze | GeoJSON in-memory | WGS84 | ODbL |
| 2 | **Geofabrik** | Komplette OSM-Daten als PBF (für Import via `osm2pgsql` in PostGIS) | `.osm.pbf` | WGS84 | ODbL |
| 3 | OSMnx Walking-Graph | Strassennetz für Isochronen | NetworkX-Graph | WGS84 | ODbL |
| 4 | **BFS STATPOP 2023** | Bevölkerungsdichte, Hektar-Raster | CSV → Punkte | LV95 | „Open Data BFS“ — frei mit Quellenangabe |
| 5 | **Stadt Zürich Open Data** | Statistische Quartiere, Quartiergrenzen | GeoJSON | LV95 | CC BY 4.0 |
| 6 | **Stadt Zürich** Wohnungs-Index | Median-Mietpreis pro Quartier | CSV | – | CC BY 4.0 |
| 7 | **swisstopo / GeoAdmin** | Hintergrundkarten (TileMap) für Folium | XYZ-Tiles | Web Mercator | terms_of_use_swisstopo |
| 8 | **swisstopo SwissALTI3D** | Höhenmodell — Knoten-Höhen + Steigung im Walking-Graph | GeoTIFF | LV95 | swisstopo Open Government Data — frei mit Quellenangabe |

---

## 1. OpenStreetMap via OSMnx

OpenStreetMap ist eine kollaborative Weltkarte. Jedes Objekt (Supermarkt, Strasse, Park) hat **Tags** wie `shop=supermarket`, `amenity=pharmacy`. Wir fragen OSM nicht direkt an, sondern über die Python-Bibliothek **OSMnx**, die einen einfachen Wrapper um die Overpass-API bietet.

**Wichtige Aufrufe** (siehe `src/zh15min/osm.py`):

```python
import osmnx as ox
boundary = ox.geocode_to_gdf("Zürich, Switzerland")
pois = ox.features_from_polygon(boundary.unary_union,
                                 tags={"shop": ["supermarket"]})
```

**Vorteile**: keine Anmeldung, eine Zeile Code, immer aktuell.
**Nachteile**: Datenqualität schwankt; manchmal fehlen Filialen kleiner Ketten.

**Lizenz**: Open Database License (ODbL). Nennung „© OpenStreetMap contributors“ in jeder Karte. Siehe <https://www.openstreetmap.org/copyright>.

## 2. Geofabrik (OSM-PBF für PostGIS)

Wenn wir das **gesamte Strassennetz und alle POIs** für die Schweiz brauchen — z. B. für den Import via `osm2pgsql` (so wie es im Kursfolien S. 80–85 gezeigt wird) — laden wir uns das **PBF** der Schweiz von Geofabrik herunter:

- URL: <https://download.geofabrik.de/europe/switzerland-latest.osm.pbf>
- Grösse: ca. 470 MB
- Aktualität: täglich neu generiert

```bash
curl -L -o data/raw/switzerland-latest.osm.pbf \
     https://download.geofabrik.de/europe/switzerland-latest.osm.pbf
```

Import in PostGIS:
```bash
osm2pgsql --create --slim --hstore \
          --database zh15min --username postgres --host localhost \
          --style /usr/share/osm2pgsql/default.style \
          data/raw/switzerland-latest.osm.pbf
```

Resultat: Tabellen `planet_osm_point`, `planet_osm_line`, `planet_osm_polygon` — wie auf den Folien des Kurses.

## 3. OSMnx Walking-Graph

Für die Berechnung der **Walking-Isochronen** (5 / 10 / 15 min) brauchen wir den begehbaren Strassengraph. OSMnx liefert ihn direkt:

```python
G = ox.graph_from_polygon(boundary.unary_union, network_type="walk")
```

Jede Kante hat `length` (Meter). Wir ergänzen `time_min = length / 83.3` (5 km/h ≙ 83.3 m/min) und nutzen `networkx.ego_graph(G, source, radius=15, distance="time_min")`, um alle in 15 Minuten erreichbaren Knoten zu finden.

## 4. BFS STATPOP — Bevölkerungsdichte

Das Bundesamt für Statistik veröffentlicht **STATPOP**, einen Datensatz mit Einwohnerzahlen je 100 m × 100 m-Zelle.

- Landingpage: <https://www.bfs.admin.ch/asset/de/32686751>
- Download (Stand FS 2026): `STATPOP2023_NOLOC_GMDFLAG.csv`
- Format: CSV mit Spalten `E_KOORD`, `N_KOORD` (LV95), `B23BTOT` (Total Einwohner pro Hektar)

**Achtung Datenschutz**: Werte ≤ 3 sind aus Anonymitätsgründen auf 3 fixiert. Für unseren Score reicht das, weil wir nur Bevölkerungsdichten je Quartier aggregieren.

Wir laden die CSV-Datei selbst herunter (kann nicht per API automatisiert werden), legen sie in `data/external/STATPOP_2023.csv` ab.

## 5. Stadt Zürich Open Data — Statistische Quartiere

Open Data Portal: <https://data.stadt-zuerich.ch/>

**Datensatz**: „Statistische Quartiere"
- Direkt-Link API: <https://www.ogd.stadt-zuerich.ch/wfs/geoportal/Statistische_Quartiere>
- Format: WFS / GeoJSON / Shapefile
- Anzahl Polygone: 34 statistische Quartiere
- CRS: LV95 (EPSG:2056)

Download als GeoJSON:
```bash
curl -L -o data/external/quartiere.geojson \
  "https://www.ogd.stadt-zuerich.ch/wfs/geoportal/Statistische_Quartiere?service=WFS&version=1.1.0&request=GetFeature&typename=ms:adm_statistische_quartiere_v&outputFormat=geojson"
```

## 6. Wohnungs-/Mietpreis-Index

Stadt Zürich Open Data, Datensatz: **Mietpreise nach Stadtquartier**
- Pfad: <https://data.stadt-zuerich.ch/dataset/bau_best_bauinv_p_jahr_quartier_od5161>
- Format: CSV mit Spalten `Jahr`, `Quartier`, `Mietpreis_Median`, `Mietpreis_Median_pro_qm` u. ä.

Wir nehmen den jüngsten verfügbaren Jahrgang (typischerweise 2-3 Jahre Versatz) und joinen ihn auf die Quartier-Polygone.

## 7. swisstopo Hintergrundkarten

Für hübsche Karten in der Präsentation nutzen wir swisstopo-Tiles:

- Pixelkarte farbig: <https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.png>
- Luftbilder SWISSIMAGE: <https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg>

Lizenz: Nutzungsbedingungen swisstopo — kostenlos für nicht-kommerziellen Gebrauch mit Quellenangabe.

## 8. SwissALTI3D — Höhenmodell (für topografischen Score)

Das **digitale Höhenmodell von swisstopo** mit 0.5 m bzw. 2 m Raster-Auflösung. Wir nutzen es, um den Walking-Graph-Knoten Höhen-Werte zuzuweisen und daraus pro Kante eine Steigung zu berechnen — die Grundlage des **topografischen Scores** (Tobler-basierte Walking-Geschwindigkeit statt konstanter 5 km/h).

**Bezugsweg** (Login bei swisstopo erforderlich, kann **nicht** automatisiert werden):

1. Browser → <https://www.swisstopo.admin.ch/de/geodata/height/alti3d.html>
2. **„swissALTI3D Daten beziehen"** → swisstopo-Login (kostenlos)
3. **Ausschnitt Zürich** auf der Karte aufziehen (BBox ungefähr 8.45° N, 47.32° E → 8.63° N, 47.44° E)
4. **Format**: GeoTIFF, **Auflösung**: 2 m, **CRS**: LV95 (EPSG:2056)
5. Download starten — kommt per E-Mail-Link, kann ein paar Minuten dauern
6. ZIP entpacken, GeoTIFF nach `data/external/swissalti3d_zh.tif` legen

**Filename-Konvention**: Genau dieser Dateiname (`swissalti3d_zh.tif`) wird in `src/zh15min/elevation.py:DEFAULT_DEM_PATH` erwartet. Falls anders benannt, in `notebooks/02b_elevation.ipynb` den Pfad explizit übergeben.

**Code-Verwendung**:
```python
from zh15min.elevation import enrich_graph_with_elevation, compute_edge_slopes
graph = enrich_graph_with_elevation(graph)   # setzt z pro Knoten
graph = compute_edge_slopes(graph)            # setzt slope pro Kante
```

**Lizenz**: swisstopo Open Government Data — kostenlos mit Quellenangabe „© swisstopo".

**Warum nötig?** Zürich ist topografisch heterogen — Zürichberg (~870 m), Hönggerberg, Käferberg, Üetliberg liegen 200–400 m über dem Stadtkern. Eine flache 15-Min-Stadt-Berechnung unterschätzt die reale Gehzeit erheblich. Mit Höhen + Tobler-Funktion wird der Score realistisch.

---

## Zusammenfassung: Wo wird was benutzt?

| Notebook | Quellen |
|---|---|
| `01_load_osm.ipynb` | 1 (OSMnx-POIs, Stadtgrenze), 7 (Hintergrund) |
| `02_streetnet_statpop.ipynb` | 3 (Walking-Graph), 4 (STATPOP), 5 (Quartiere) |
| **`02b_elevation.ipynb`** ⭐ | **3 (Walking-Graph aus 02), 8 (SwissALTI3D)** |
| `03_postgis_import.ipynb` | 2 (Geofabrik PBF → osm2pgsql), Outputs aus 01/02 |
| `04_isochrones.ipynb` | 3 |
| `05_score.ipynb` | Outputs aus 01/04 |
| **`05b_topo_score.ipynb`** | Outputs aus 02b/04 (geplant) |
| `06_gap_analysis.ipynb` | 4, 5, 6, eigener Score |
| **`06b_delta.ipynb`** | Vergleich flat vs. topografisch (geplant) |
| `07_visualization.ipynb` | 7 + alles aus 05/06 |

Bei allen Karten zwingend **Copyright-Hinweise**:
> © OpenStreetMap-Mitwirkende · © swisstopo · © swisstopo SwissALTI3D · BFS STATPOP 2023/2024 · Stadt Zürich Open Data

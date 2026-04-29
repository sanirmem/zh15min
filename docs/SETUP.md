# SETUP — Schritt-für-Schritt für die Gruppe

> Diese Anleitung führt euch in **45 Minuten** vom leeren Repo zum laufenden Score. Sie geht davon aus, dass keiner von euch Vorerfahrung mit PostGIS oder OSMnx hat.

## Voraussetzungen

| Software | Version | Wer braucht's? |
|---|---|---|
| Python | 3.11 oder 3.12 | alle |
| Docker Desktop | aktuell | alle (für PostGIS) |
| QGIS | 3.40 LTR | für Visualisierung |
| Git | aktuell | alle |

Mac-User: alles per Homebrew (`brew install python git`, Docker Desktop von docker.com, QGIS von qgis.org).
Windows: Python von python.org, Docker Desktop, QGIS-OSGeo4W-Installer.

---

## Schritt 1 — Repository einrichten (5 min)

```bash
# Eine/r legt das Repo auf GitHub an: zh15min
git clone git@github.com:<eure-org>/zh15min.git
cd zh15min

# Dieses Projekt-Skelett (alles, was Claude erstellt hat) hinein kopieren / commiten
git add .
git commit -m "Initial: Projektstruktur, Notebooks, src-Paket, Slides"
git push
```

## Schritt 2 — Python-Umgebung (10 min)

```bash
python3 -m venv .venv
source .venv/bin/activate          # Mac/Linux
# .venv\Scripts\activate           # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

Test:
```bash
python -c "import geopandas, osmnx, sqlalchemy; print('OK')"
```

## Schritt 3 — PostGIS via Docker (5 min)

```bash
cp .env.example .env               # Defaults reichen für lokale Arbeit
docker compose up -d
docker compose ps                  # zh15min_postgis sollte 'healthy' zeigen
```

Browser → `http://localhost:5050` → pgAdmin (Login `admin@local.test` / `admin` aus `.env`).
Server registrieren: Host `postgis`, Port `5432`, DB `zh15min`, User `postgres`, PW `postgres`.

## Schritt 4 — Daten und Notebooks ausführen (20 min)

```bash
jupyter lab notebooks/
```

In Jupyter Lab in **dieser** Reihenfolge öffnen und „Run All" drücken:

1. `01_load_osm.ipynb` — lädt Stadtgrenze + POIs (~3 min)
2. `02_streetnet_statpop.ipynb` — Walking-Graph + Quartiere (~5 min)
   - **Manueller Schritt vorher:** STATPOP CSV von <https://www.bfs.admin.ch/asset/de/32686751> in `data/external/STATPOP_2023.csv` legen.
3. `03_postgis_import.ipynb` — Daten in PostGIS schreiben (~1 min)
4. `04_isochrones.ipynb` — Demo-Isochronen + Hex-Gitter (~2 min)
5. `05_score.ipynb` — Score-Berechnung (~30 s dank KDTree)
6. `06_gap_analysis.ipynb` — Hypothesen-Test (~1 min)
7. `07_visualization.ipynb` — Karten erstellen (~30 s)

## Schritt 5 — QGIS-Projekt (5 min)

Folgt `qgis/QGIS_SETUP.md` — verbindet euch mit der lokalen PostGIS-DB und stellt die Score-Symbologie ein.

## Schritt 6 — Optional: Vollständiges OSM-PBF importieren

Nur wenn ihr in der Live-Demo SQL-Queries auf `planet_osm_*` zeigen wollt (wie in den Kursfolien):

```bash
# Geofabrik-PBF Schweiz herunterladen (~470 MB)
curl -L -o data/raw/switzerland-latest.osm.pbf \
  https://download.geofabrik.de/europe/switzerland-latest.osm.pbf

# osm2pgsql (Mac)
brew install osm2pgsql

# Importieren — dauert 5–15 min
osm2pgsql --create --slim --hstore \
  --database zh15min --username postgres --host localhost --port 5432 \
  data/raw/switzerland-latest.osm.pbf
```

---

## Aufgabenteilung (Vorschlag, 3 Personen)

| Person | Verantwortung | Slides | Repo-Bereich |
|---|---|---|---|
| A | Daten & Datenbank | 1–7 (Einleitung, Daten) | `notebooks/01–03`, `docs/data_sources.md` |
| B | Methode & Score | 8–10, 12 (Methodik, H-Tests) | `src/zh15min/`, `notebooks/04–06` |
| C | Visualisierung & QGIS | 11, 13–16 (Ergebnisse, Schluss) | `notebooks/07`, `qgis/`, Slides-Polishing |

Jede/r macht ihren/seinen Slot in der Videopräsentation (~3 Min pro Person).

---

## Häufige Fehler

| Symptom | Ursache | Fix |
|---|---|---|
| `psycopg.OperationalError: connection refused` | Docker nicht hochgefahren | `docker compose up -d` |
| `OSMnx GeocoderError: Z`#xFC;`rich not found` | Overpass-Server timed out | Notebook erneut ausführen, OSMnx nutzt Cache |
| `KeyError: 'B23BTOT'` | STATPOP-Spalte heisst anders | In Notebook 02 die echte Total-Spalte (`B<Jahr>BTOT`) prüfen |
| `RuntimeError: cannot find proj.db` | Pyproj-Daten fehlen | `pip install --force-reinstall pyproj` |
| pgAdmin meldet „server already registered" | Konfigurationsstand alt | Bestehenden Server löschen, neu anlegen |

---

## Helpful Commands

```bash
# DB stoppen / komplett zurücksetzen
docker compose down -v       # -v löscht das Volume (alle Daten weg!)
docker compose up -d

# Score erneut berechnen, ohne 01/02 nochmal zu fahren
jupyter execute notebooks/05_score.ipynb

# Slides regenerieren (falls Inhalte angepasst werden)
node scripts/build_slides.js
```

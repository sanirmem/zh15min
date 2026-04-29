"""Erzeugt notebooks/03_postgis_import.ipynb."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from make_notebook import md, code, nb, save

OUT = Path("/sessions/intelligent-practical-clarke/mnt/Einsatz von Geodaten in Marketing/notebooks/03_postgis_import.ipynb")

cells = [
    md(
        "# 03 — PostGIS-Setup & Datenimport",
        "",
        "**Ziel:** Alle vorbereiteten Layer in eine zentrale PostGIS-Datenbank laden, sodass Notebook 05/06 SQL-basiert auf eine konsistente Datenbasis zugreifen kann.",
        "",
        "**Voraussetzung:**",
        "1. `docker compose up -d` wurde im Projekt-Root ausgeführt → PostGIS läuft auf Port 5432, pgAdmin auf Port 5050.",
        "2. `.env` ist aus `.env.example` erstellt.",
        "",
        "**Inhalt:**",
        "1. Verbindungs-Test (`SELECT postgis_full_version()`).",
        "2. Layer aus den GeoPackages der vorigen Notebooks in das Schema `zh15min` schreiben.",
        "3. (Optional) Volles OSM-PBF via `osm2pgsql` importieren — wie in den Kursfolien gezeigt.",
    ),
    md("## 1. Setup & PostGIS-Verbindung"),
    code(
        "import sys",
        "from pathlib import Path",
        "ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()",
        "sys.path.insert(0, str(ROOT / 'src'))",
        "",
        "import geopandas as gpd",
        "from sqlalchemy import text",
        "",
        "from zh15min import config, db",
    ),
    code(
        "ok = db.ping()",
        "assert ok, 'PostGIS antwortet nicht — läuft der Docker-Container?'",
    ),
    md(
        "## 2. Stadtgrenze & POIs in PostGIS schreiben",
        "",
        "Wir reprojizieren auf LV95 (EPSG:2056), dem im Kurs verwendeten metrischen System.",
    ),
    code(
        "boundary = gpd.read_file(config.PROCESSED_DIR / 'zh_boundary.gpkg', layer='boundary').to_crs(config.EPSG_LV95)",
        "db.write_gdf(boundary[['geometry']].assign(name='Zürich'), 'boundary')",
        "print('boundary →', len(boundary), 'Zeilen')",
    ),
    code(
        "pois = gpd.read_file(config.PROCESSED_DIR / 'zh_pois.gpkg', layer='all').to_crs(config.EPSG_LV95)",
        "# nur Spalten halten, die wir brauchen",
        "keep = [c for c in ['osmid', 'name', 'category'] if c in pois.columns]",
        "pois = pois[keep + ['geometry']]",
        "db.write_gdf(pois, 'pois')",
        "print('pois →', len(pois), 'Zeilen')",
    ),
    code(
        "quart = gpd.read_file(config.EXTERNAL_DIR / 'quartiere.geojson').to_crs(config.EPSG_LV95)",
        "# Spalten unifizieren",
        "rename = {c: c.lower() for c in quart.columns}",
        "quart = quart.rename(columns=rename)",
        "db.write_gdf(quart, 'quartiere')",
        "print('quartiere →', len(quart), 'Zeilen')",
    ),
    md("## 3. Smoke-Tests — passt alles?"),
    code(
        "with db.conn() as c:",
        "    rows = c.execute(text(",
        "        'SELECT category, COUNT(*) FROM zh15min.pois GROUP BY category ORDER BY 2 DESC'",
        "    )).fetchall()",
        "for r in rows: print(r)",
    ),
    code(
        "with db.conn() as c:",
        "    n_in = c.execute(text(",
        "        'SELECT COUNT(*) FROM zh15min.pois p '",
        "        'JOIN zh15min.boundary b ON ST_Within(p.geometry, b.geometry)'",
        "    )).scalar()",
        "print('POIs innerhalb der Stadtgrenze:', n_in)",
    ),
    md(
        "## 4. (Optional) Volles OSM-PBF via `osm2pgsql`",
        "",
        "Wie in den Kurs-Folien (S. 80–85) gezeigt, importiert `osm2pgsql` ein PBF in die Tabellen `planet_osm_point`, `planet_osm_line`, `planet_osm_polygon`. Das ist nicht zwingend für den Score — aber sehr stark für die Live-Demo (z.B. SQL-Query für \"Supermärkte mit Adresse\" aus den Kursfolien).",
        "",
        "**Schritte (im Terminal, nicht im Notebook):**",
        "",
        "```bash",
        "# 1. PBF herunterladen",
        "curl -L -o data/raw/switzerland-latest.osm.pbf \\",
        "  https://download.geofabrik.de/europe/switzerland-latest.osm.pbf",
        "",
        "# 2. osm2pgsql installieren (macOS)",
        "brew install osm2pgsql",
        "",
        "# 3. Importieren — dauert 5–15 min",
        "osm2pgsql --create --slim --hstore \\",
        "  --database zh15min --username postgres --host localhost \\",
        "  --port 5432 \\",
        "  data/raw/switzerland-latest.osm.pbf",
        "```",
        "",
        "Anschliessend könnt ihr in pgAdmin direkt Queries wie",
        "",
        "```sql",
        "SELECT name, addr_street, addr_housenumber",
        "FROM   planet_osm_point",
        "WHERE  shop = 'supermarket' AND name IS NOT NULL",
        "LIMIT  20;",
        "```",
        "",
        "ausführen und in der Live-Demo zeigen.",
    ),
    md(
        "## 5. Zusammenfassung",
        "",
        "Ab jetzt sind in PostGIS verfügbar (Schema `zh15min`):",
        "",
        "- `boundary` — Stadtgrenze",
        "- `pois` — alle POI-Punkte",
        "- `quartiere` — 34 statistische Quartiere",
        "",
        "Optional zusätzlich (über `osm2pgsql`):",
        "- `planet_osm_point|line|polygon` — gesamtes Schweizer OSM",
    ),
]

save(OUT, nb(cells))
print('Notebook 03 geschrieben:', OUT)

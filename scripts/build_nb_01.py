"""Erzeugt notebooks/01_load_osm.ipynb."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from make_notebook import md, code, nb, save

OUT = Path("/sessions/intelligent-practical-clarke/mnt/Einsatz von Geodaten in Marketing/notebooks/01_load_osm.ipynb")

cells = [
    md(
        "# 01 — OSM-Daten für Zürich laden",
        "",
        "**Ziel:** Stadtgrenze und alle relevanten Points of Interest (POIs) per OSMnx aus OpenStreetMap holen, in einem GeoPackage ablegen und einen ersten Sichtcheck machen.",
        "",
        "**Quellen:**",
        "- OpenStreetMap via OSMnx → `ox.geocode_to_gdf`, `ox.features_from_polygon`",
        "- siehe auch `docs/data_sources.md`",
        "",
        "**Output:**",
        "- `data/processed/zh_boundary.gpkg`",
        "- `data/processed/zh_pois.gpkg` (alle Kategorien zusammengelegt)",
    ),
    md(
        "## 1. Setup",
        "",
        "Wir hängen das Projekt-`src`-Verzeichnis an den Pythonpfad, sodass wir das Paket `zh15min` importieren können.",
    ),
    code(
        "import sys",
        "from pathlib import Path",
        "",
        "ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()",
        "sys.path.insert(0, str(ROOT / 'src'))",
        "",
        "import logging",
        "logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')",
        "",
        "from zh15min import config, osm",
        "print('Projekt-Root:', ROOT)",
        "print('Datenverzeichnis:', config.DATA_DIR)",
    ),
    md("## 2. Stadtgrenze Zürich laden"),
    code(
        "boundary = osm.city_boundary('Zürich, Switzerland')",
        "boundary.to_file(config.PROCESSED_DIR / 'zh_boundary.gpkg', layer='boundary', driver='GPKG')",
        "print(f'Stadtgrenze geladen: {len(boundary)} Polygon(e)')",
        "boundary.head(2)",
    ),
    code(
        "ax = boundary.plot(figsize=(7, 7), facecolor='none', edgecolor='black', linewidth=1.4)",
        "ax.set_title('Stadtgrenze Zürich (OSM)', fontsize=12)",
        "ax.set_axis_off();",
    ),
    md(
        "## 3. POIs aller Kategorien laden",
        "",
        "Die in `config.POI_CATEGORIES` definierten OSM-Tags werden Kategorie für Kategorie abgefragt. Polygon-POIs (z.B. Spitäler) werden auf ihren Schwerpunkt reduziert, damit wir später einheitlich mit Punkten rechnen können.",
    ),
    code(
        "pois = osm.all_pois(boundary)",
        "print(f'Insgesamt {len(pois):,} POIs')",
        "pois.groupby('category').size().sort_values(ascending=False)",
    ),
    code(
        "# In ein GeoPackage schreiben — eine Layer pro Kategorie + 'all'",
        "out_path = config.PROCESSED_DIR / 'zh_pois.gpkg'",
        "if out_path.exists():",
        "    out_path.unlink()",
        "",
        "for cat, grp in pois.groupby('category'):",
        "    grp.to_file(out_path, layer=cat, driver='GPKG')",
        "pois.to_file(out_path, layer='all', driver='GPKG')",
        "print('Gespeichert nach', out_path)",
    ),
    md(
        "## 4. Sichtcheck — POIs auf der Karte",
        "",
        "Eine kleine, schnelle matplotlib-Karte zur Plausibilitätsprüfung. Die richtige Visualisierung folgt in Notebook 07.",
    ),
    code(
        "import matplotlib.pyplot as plt",
        "",
        "fig, ax = plt.subplots(figsize=(9, 9))",
        "boundary.plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1)",
        "for cat, grp in pois.groupby('category'):",
        "    grp.plot(ax=ax, markersize=4, alpha=0.6, label=cat)",
        "ax.legend(loc='upper right', fontsize=8)",
        "ax.set_title(f'POIs nach Kategorie ({len(pois):,} Punkte)', fontsize=12)",
        "ax.set_axis_off();",
    ),
    md(
        "## 5. Zusammenfassung",
        "",
        "- ✅ Stadtgrenze in `data/processed/zh_boundary.gpkg`",
        "- ✅ POIs in `data/processed/zh_pois.gpkg` (Layer pro Kategorie + Layer `all`)",
        "",
        "Weiter mit `02_streetnet_statpop.ipynb`.",
    ),
]

save(OUT, nb(cells))
print('Notebook 01 geschrieben:', OUT)

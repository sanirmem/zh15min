"""Erzeugt notebooks/02_streetnet_statpop.ipynb."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from make_notebook import md, code, nb, save

OUT = Path("/sessions/intelligent-practical-clarke/mnt/Einsatz von Geodaten in Marketing/notebooks/02_streetnet_statpop.ipynb")

cells = [
    md(
        "# 02 — Walking-Strassennetz, Bevölkerungsraster & Stadtquartiere",
        "",
        "**Ziel:** Drei zusätzliche Datenquellen vorbereiten:",
        "1. **OSMnx Walking-Graph** — die Basis für die Isochronen-Berechnung in Notebook 04.",
        "2. **BFS STATPOP 2023** — Bevölkerungsdichte-Hektarraster, später für die Versorgungslücken-Analyse.",
        "3. **Stadt Zürich Open Data** — die 34 statistischen Quartiere.",
        "",
        "**Outputs:**",
        "- `data/processed/zh_walk_graph.graphml`",
        "- `data/external/quartiere.geojson`",
        "- `data/external/STATPOP_2023.csv` (manuell herunterzuladen — wir prüfen Existenz)",
    ),
    md("## 1. Setup"),
    code(
        "import sys",
        "from pathlib import Path",
        "ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()",
        "sys.path.insert(0, str(ROOT / 'src'))",
        "",
        "import geopandas as gpd",
        "import pandas as pd",
        "import requests",
        "import osmnx as ox",
        "",
        "from zh15min import config, osm",
    ),
    md(
        "## 2. Walking-Strassennetz",
        "",
        "OSMnx bietet `graph_from_polygon` mit `network_type='walk'`. Der Graph wird simplifiziert (Knoten werden zusammengelegt, wo es nur Durchgangs-Knoten gibt) und als GraphML gespeichert.",
    ),
    code(
        "boundary = gpd.read_file(config.PROCESSED_DIR / 'zh_boundary.gpkg', layer='boundary')",
        "G = osm.walk_graph(boundary)",
        "print(f'Walking-Graph: {len(G.nodes):,} Knoten, {len(G.edges):,} Kanten')",
    ),
    code(
        "graph_path = config.PROCESSED_DIR / 'zh_walk_graph.graphml'",
        "ox.save_graphml(G, graph_path)",
        "print('Graph gespeichert:', graph_path)",
    ),
    md(
        "## 3. Statistische Quartiere (Stadt Zürich Open Data)",
        "",
        "WFS-Endpoint des Geoportals Zürich. Falls der Download fehlschlägt (Firewall, Versionswechsel), liefern wir einen Fallback über das ARE-Datensatzportal.",
    ),
    code(
        "QUART_URL = (",
        "    'https://www.ogd.stadt-zuerich.ch/wfs/geoportal/Statistische_Quartiere'",
        "    '?service=WFS&version=1.1.0&request=GetFeature'",
        "    '&typename=ms:adm_statistische_quartiere_v&outputFormat=geojson'",
        ")",
        "quart_path = config.EXTERNAL_DIR / 'quartiere.geojson'",
        "",
        "if not quart_path.exists():",
        "    print('Lade Quartiere…')",
        "    r = requests.get(QUART_URL, timeout=120)",
        "    r.raise_for_status()",
        "    quart_path.write_bytes(r.content)",
        "    print('Gespeichert:', quart_path)",
        "else:",
        "    print('Quartiere bereits vorhanden:', quart_path)",
        "",
        "quart = gpd.read_file(quart_path).to_crs(config.EPSG_LV95)",
        "print(f'{len(quart)} Quartier-Polygone')",
        "quart.head(3)",
    ),
    code(
        "ax = quart.plot(figsize=(7, 7), facecolor='lightgrey', edgecolor='white', linewidth=0.7)",
        "ax.set_title('Statistische Quartiere Zürich', fontsize=12)",
        "ax.set_axis_off();",
    ),
    md(
        "## 4. STATPOP 2023 (BFS) — Bevölkerung pro Hektar",
        "",
        "Die CSV ist nicht per offene API erreichbar (Asset-ID-basierter Download mit Captcha). Bitte einmalig manuell herunterladen:",
        "",
        "👉 https://www.bfs.admin.ch/asset/de/32686751",
        "",
        "Dann nach `data/external/STATPOP_2023.csv` legen. Die Spalten heissen typischerweise `E_KOORD`, `N_KOORD`, `B23BTOT` (Total Einwohner).",
    ),
    code(
        "statpop_path = config.EXTERNAL_DIR / 'STATPOP_2023.csv'",
        "",
        "if not statpop_path.exists():",
        "    print('⚠️  STATPOP fehlt — bitte manuell von https://www.bfs.admin.ch/asset/de/32686751 laden.')",
        "    print('    Notebook 06 funktioniert auch ohne, dann fehlt nur die Dichte-Validierung.')",
        "else:",
        "    statpop = pd.read_csv(statpop_path, sep=';', low_memory=False)",
        "    print(f'STATPOP: {len(statpop):,} Hektarzellen Schweiz')",
        "    # Auf Zürich clippen über Quartier-BBOX in LV95",
        "    minx, miny, maxx, maxy = quart.total_bounds",
        "    pad = 500",
        "    mask = (",
        "        statpop['E_KOORD'].between(minx - pad, maxx + pad)",
        "        & statpop['N_KOORD'].between(miny - pad, maxy + pad)",
        "    )",
        "    pop_zh = statpop.loc[mask].copy()",
        "    pop_zh = gpd.GeoDataFrame(",
        "        pop_zh,",
        "        geometry=gpd.points_from_xy(pop_zh['E_KOORD'], pop_zh['N_KOORD']),",
        "        crs=config.EPSG_LV95,",
        "    )",
        "    pop_zh.to_file(config.PROCESSED_DIR / 'zh_statpop.gpkg', layer='pop_ha', driver='GPKG')",
        "    print(f'Zürich: {len(pop_zh):,} Hektarzellen — gespeichert.')",
    ),
    md(
        "## 5. Zusammenfassung",
        "",
        "- ✅ Walking-Graph in `data/processed/zh_walk_graph.graphml`",
        "- ✅ Quartiere in `data/external/quartiere.geojson`",
        "- ⚠️/✅ STATPOP — falls vorhanden in `data/processed/zh_statpop.gpkg`",
        "",
        "Weiter mit `03_postgis_import.ipynb`.",
    ),
]

save(OUT, nb(cells))
print('Notebook 02 geschrieben:', OUT)

"""Erzeugt notebooks/04_isochrones.ipynb."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from make_notebook import md, code, nb, save

OUT = Path("/sessions/intelligent-practical-clarke/mnt/Einsatz von Geodaten in Marketing/notebooks/04_isochrones.ipynb")

cells = [
    md(
        "# 04 — Walking-Isochronen (5 / 10 / 15 Min)",
        "",
        "**Ziel:** Für ausgewählte Beispielpunkte Walking-Isochronen berechnen, um die Methodik zu illustrieren — und das **Hex-Analyse-Gitter** über Zürich anlegen, in dem wir später den Score schreiben.",
        "",
        "**Methode:** OSMnx-Walking-Graph → Kanten mit Gehzeit gewichten → `networkx.ego_graph` für jeden Mittelpunkt.",
        "",
        "**Outputs:**",
        "- `data/processed/zh_hex_grid.gpkg` — Analyse-Gitter (200 m Apothem)",
        "- `reports/figures/isochrone_demo.png` — Isochronen-Karte für die Slides",
    ),
    md("## 1. Setup"),
    code(
        "import sys",
        "from pathlib import Path",
        "ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()",
        "sys.path.insert(0, str(ROOT / 'src'))",
        "",
        "import geopandas as gpd",
        "import matplotlib.pyplot as plt",
        "import osmnx as ox",
        "from shapely.geometry import Point",
        "",
        "from zh15min import config, grid, isochron",
    ),
    md("## 2. Hex-Analyse-Gitter über die Stadt legen"),
    code(
        "boundary = gpd.read_file(config.PROCESSED_DIR / 'zh_boundary.gpkg', layer='boundary')",
        "hex_grid = grid.hex_grid(boundary, apothem_m=config.HEX_RESOLUTION_M)",
        "print(f'Hex-Gitter: {len(hex_grid):,} Zellen ({config.HEX_RESOLUTION_M} m Apothem)')",
        "hex_grid.head(3)",
    ),
    code(
        "hex_grid.to_file(config.PROCESSED_DIR / 'zh_hex_grid.gpkg', layer='grid', driver='GPKG')",
    ),
    md("## 3. Walking-Graph laden & mit Gehzeit gewichten"),
    code(
        "graph_path = config.PROCESSED_DIR / 'zh_walk_graph.graphml'",
        "G = ox.load_graphml(graph_path)",
        "G = isochron.add_walk_time(G, speed_kmh=config.WALK_SPEED_KMH)",
        "print(f'Graph: {len(G.nodes):,} Knoten, {len(G.edges):,} Kanten')",
    ),
    md(
        "## 4. Demo: Isochronen für drei prominente Standorte",
        "",
        "Gewählt sind drei Punkte mit unterschiedlichem Charakter — Innenstadt (HB), Wohnquartier (Wiedikon) und Entwicklungsgebiet (Leutschenbach).",
    ),
    code(
        "demo_points_lv95 = {",
        "    'Hauptbahnhof':   (2683160, 1248230),",
        "    'Wiedikon':       (2681900, 1246150),",
        "    'Leutschenbach':  (2685300, 1252700),",
        "}",
        "",
        "iso_records = []",
        "for label, (x, y) in demo_points_lv95.items():",
        "    for minutes in (5, 10, 15):",
        "        poly = isochron.isochrone_polygon(G, (x, y), minutes=minutes)",
        "        if poly is not None:",
        "            iso_records.append({'point': label, 'minutes': minutes, 'geometry': poly})",
        "",
        "iso_gdf = gpd.GeoDataFrame(iso_records, geometry='geometry', crs=config.EPSG_LV95)",
        "iso_gdf.head(6)",
    ),
    code(
        "fig, ax = plt.subplots(figsize=(10, 10))",
        "boundary.to_crs(config.EPSG_LV95).plot(ax=ax, facecolor='none', edgecolor='black', linewidth=1)",
        "",
        "colors = {5: '#1a9850', 10: '#fdae61', 15: '#d73027'}",
        "for minutes, sub in iso_gdf.groupby('minutes'):",
        "    sub.plot(ax=ax, alpha=0.25, color=colors[minutes], edgecolor=colors[minutes], linewidth=1.4, label=f'{minutes} min')",
        "",
        "for label, (x, y) in demo_points_lv95.items():",
        "    ax.plot(x, y, 'ko', markersize=6)",
        "    ax.annotate(label, (x, y), xytext=(5, 5), textcoords='offset points', fontsize=9)",
        "",
        "ax.legend(title='Walking-Isochrone', loc='lower left')",
        "ax.set_title('Fussweg-Erreichbarkeit (5 / 10 / 15 min) — Demo', fontsize=12)",
        "ax.set_axis_off()",
        "out = config.FIGURES_DIR / 'isochrone_demo.png'",
        "fig.savefig(out, dpi=180, bbox_inches='tight')",
        "print('Figur gespeichert:', out)",
    ),
    md(
        "## 5. Zusammenfassung",
        "",
        "- ✅ Hex-Gitter (200 m) über die ganze Stadt — Basis aller Score-Zellen.",
        "- ✅ Demo-Isochronen für drei Standorte — illustriert die Methode in den Slides.",
        "- ⚙️ Den Score selbst berechnen wir in Notebook 05 nicht über `ego_graph` für jede einzelne Zelle (zu langsam), sondern mit einer **Luftlinien-Approximation auf KDTree**, die für 12 000+ Zellen × 4 500 POIs in Sekunden läuft. Die Isochronen dienen als Validierung und Visualisierung der Methode.",
    ),
]

save(OUT, nb(cells))
print('Notebook 04 geschrieben:', OUT)

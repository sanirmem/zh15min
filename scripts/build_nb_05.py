"""Erzeugt notebooks/05_score.ipynb."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from make_notebook import md, code, nb, save

OUT = Path("/sessions/intelligent-practical-clarke/mnt/Einsatz von Geodaten in Marketing/notebooks/05_score.ipynb")

cells = [
    md(
        "# 05 — 15-Minute-City-Score",
        "",
        "**Ziel:** Pro Hex-Zelle einen Score in [0, 100] berechnen, der die Erreichbarkeit täglicher Funktionen (Einkauf, Bildung, Gesundheit, Erholung, Gastro, ÖV) innerhalb einer 15-Minuten-Fussdistanz quantifiziert.",
        "",
        "**Methodik (kurz):**",
        "Pro Kategorie c und Zelle z:",
        "$$A_c(z) = \\sum_{p \\in P_c,\\, d(z,p) \\le d_{\\max}} \\exp\\!\\left(-\\beta \\cdot \\frac{d(z,p)}{d_{\\max}}\\right)$$",
        "",
        "Anschliessend Normalisierung pro Kategorie auf [0,1] (95.-Perzentil-Cap), gewichtete Summe über die Kategorien (Gewichte aus `config.POI_CATEGORIES`), Skalierung × 100.",
        "",
        "**Output:**",
        "- `data/processed/zh_score.gpkg` — Hex-Gitter mit allen Score-Spalten",
        "- Score wird zusätzlich in PostGIS (`zh15min.score`) geschrieben",
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
        "",
        "from zh15min import config, db, score",
    ),
    md("## 2. Daten laden"),
    code(
        "hex_grid = gpd.read_file(config.PROCESSED_DIR / 'zh_hex_grid.gpkg', layer='grid')",
        "pois     = gpd.read_file(config.PROCESSED_DIR / 'zh_pois.gpkg',     layer='all').to_crs(config.EPSG_LV95)",
        "print(f'Gitter: {len(hex_grid):,} Zellen | POIs: {len(pois):,}')",
    ),
    md("## 3. Erreichbarkeit pro Kategorie"),
    code(
        "acc = score.category_accessibility(",
        "    hex_grid, pois,",
        "    d_max=config.WALK_DISTANCE_M,",
        "    beta=config.HUFF_BETA,",
        ")",
        "acc.head(3)",
    ),
    md("## 4. Gesamtscore (gewichtete Summe)"),
    code(
        "scored = score.total_score(acc)",
        "scored.describe()[['acc_einkauf', 'acc_bildung', 'acc_gesundheit', 'acc_erholung', 'acc_gastro', 'acc_oev', 'score']]",
    ),
    code(
        "# zurück an das Hex-Gitter joinen",
        "hex_score = hex_grid.merge(scored, on='hex_id', how='left')",
        "hex_score.to_file(config.PROCESSED_DIR / 'zh_score.gpkg', layer='hex_score', driver='GPKG')",
        "print('Gespeichert:', config.PROCESSED_DIR / 'zh_score.gpkg')",
    ),
    md("## 5. Score in PostGIS schreiben"),
    code(
        "db.write_gdf(hex_score, 'score')",
        "from sqlalchemy import text",
        "with db.conn() as c:",
        "    avg = c.execute(text('SELECT AVG(score) FROM zh15min.score')).scalar()",
        "print(f'Mittlerer Score (Stadt Zürich): {avg:.1f}')",
    ),
    md(
        "## 6. Schnelle Sichtprüfung",
        "",
        "Die richtige Kartendarstellung folgt in Notebook 07 (Folium + statisch).",
    ),
    code(
        "import matplotlib.pyplot as plt",
        "fig, ax = plt.subplots(figsize=(9, 9))",
        "hex_score.plot(column='score', cmap='RdYlGn', scheme='quantiles', k=7, legend=True, ax=ax, edgecolor='none')",
        "ax.set_axis_off()",
        "ax.set_title('15-Minute-City-Score Zürich (Quantile)', fontsize=12);",
    ),
    md(
        "## 7. Zusammenfassung",
        "",
        "- ✅ Score je Hex-Zelle berechnet (sechs Komponenten + Total).",
        "- ✅ Persistiert als GeoPackage und in PostGIS-Tabelle `zh15min.score`.",
        "",
        "Weiter mit `06_gap_analysis.ipynb` für Hypothesen-Test und Versorgungslücken.",
    ),
]

save(OUT, nb(cells))
print('Notebook 05 geschrieben:', OUT)

"""Re-generiert alle Slide-Figuren aus den aktuellen GeoPackages.

Dieses Skript ist äquivalent zu Notebook 07, aber als CLI-Tool. Praktisch,
wenn man die Figuren nach einem Notebook-06-Re-Run neu erzeugen will, ohne
Jupyter zu starten.

Aufruf (vom Projekt-Root, mit aktivem .venv):

    python scripts/regenerate_figures.py

Outputs in reports/figures/:
    - score_map.png             — Hex-Score-Karte mit OSM-Hintergrund
    - score_map.html            — interaktive Folium-Karte
    - topflop_quartiere.png     — Top/Flop-5-Bar-Charts
    - score_histogram.png       — Score-Verteilung
"""

from __future__ import annotations

import sys
from pathlib import Path

# Projekt-Root in den Python-Pfad
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

from zh15min import config, viz


def main() -> None:
    print(f"Projekt-Root: {ROOT}")
    print(f"Output: {config.FIGURES_DIR}\n")

    # --- Daten laden -------------------------------------------------------
    hex_score = gpd.read_file(
        config.PROCESSED_DIR / "zh_score.gpkg", layer="hex_score"
    ).to_crs(config.EPSG_LV95)
    quart_summary = gpd.read_file(
        config.PROCESSED_DIR / "zh_quartier_summary.gpkg", layer="quartiere"
    ).to_crs(config.EPSG_LV95)
    pois_path = config.PROCESSED_DIR / "zh_pois.gpkg"
    pois = gpd.read_file(pois_path, layer="all").to_crs(config.EPSG_LV95) if pois_path.exists() else None

    print(
        f"Daten geladen: {len(hex_score):,} Hex-Zellen, "
        f"{len(quart_summary)} Quartiere"
        + (f", {len(pois):,} POIs" if pois is not None else "")
    )

    # --- 1. Statische Score-Karte -----------------------------------------
    fig, _ = viz.style_score_static(hex_score, title="15-Minute-City-Score Zürich")
    out = config.FIGURES_DIR / "score_map.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")

    # --- 2. Folium interaktive Karte (Hex + Quartier-Overlay + POIs) ------
    m = viz.folium_score(hex_score, quart_summary=quart_summary, pois=pois)
    out = config.FIGURES_DIR / "score_map.html"
    m.save(str(out))
    print(f"  ✓ {out.name}")

    # --- 3. Top/Flop-Quartiere --------------------------------------------
    name_col = next(
        (c for c in quart_summary.columns if "name" in c.lower()), None
    )
    if name_col is None:
        raise RuntimeError("Quartier-Namensspalte nicht gefunden")

    ranking = (
        quart_summary[[name_col, "score_mean"]].dropna().sort_values(
            "score_mean", ascending=False
        )
    )
    top = ranking.head(5).iloc[::-1]
    flop = ranking.tail(5)

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))
    axes[0].barh(top[name_col], top["score_mean"], color="#1a9850")
    axes[0].set_title("Top 5 Quartiere")
    axes[0].set_xlabel("Score (Mittelwert)")
    for ax in axes[0:1]:
        for i, v in enumerate(top["score_mean"]):
            ax.text(v + 1, i, f"{v:.1f}", va="center", fontsize=10)

    axes[1].barh(flop[name_col], flop["score_mean"], color="#d73027")
    axes[1].set_title("Flop 5 Quartiere")
    axes[1].set_xlabel("Score (Mittelwert)")
    for i, v in enumerate(flop["score_mean"]):
        axes[1].text(v + 1, i, f"{v:.1f}", va="center", fontsize=10)
    for ax in axes:
        ax.invert_yaxis()
        ax.set_xlim(0, 100)
    fig.suptitle(f"Top- und Flop-Quartiere (n = {len(ranking)})", fontsize=14)
    fig.tight_layout()
    out = config.FIGURES_DIR / "topflop_quartiere.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")

    # --- 4. Score-Histogramm ----------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(hex_score["score"].dropna(), bins=30, color="#4575b4", edgecolor="white")
    median = float(hex_score["score"].median())
    ax.axvline(median, color="black", linestyle="--", label=f"Median = {median:.1f}")
    ax.set_xlabel("15-Minute-City-Score")
    ax.set_ylabel("Anzahl Hex-Zellen")
    ax.set_title("Verteilung des Scores über Zürich")
    ax.legend()
    fig.tight_layout()
    out = config.FIGURES_DIR / "score_histogram.png"
    fig.savefig(out, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {out.name}")

    print("\nAlle Figuren regeneriert.")


if __name__ == "__main__":
    main()

"""15-Minute-City-Score je Hex-Zelle.

Methodik
--------
Pro Zelle und Kategorie c berechnen wir die Distanz d(z, p) zu jedem POI p der
Kategorie c (auf dem Strassengraph, sonst als Luftlinien-Fallback). Die
Erreichbarkeit A_c einer Zelle z ist eine Huff-artige Summe gewichtet mit dem
Distance-Decay :math:`exp(-\\beta \\cdot d / d_{max})` für d ≤ d_max:

.. math::
    A_c(z) = \\sum_{p \\in P_c, d(z,p) \\le d_{max}} \\exp(-\\beta \\cdot d(z,p)/d_{max})

A_c wird je Kategorie auf [0,1] normalisiert (95.-Perzentil-Capping gegen
Ausreisser) und über die Kategorien mit den Gewichten aus
:data:`config.POI_CATEGORIES` aggregiert. Resultat ist ein Score in [0, 100].
"""

from __future__ import annotations

import logging

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from . import config

log = logging.getLogger(__name__)


def _kdtree_distances(
    cell_xy: np.ndarray,
    poi_xy: np.ndarray,
    d_max: float,
) -> list[np.ndarray]:
    """Liefert pro Zelle ein Array der Luftlinien-Distanzen ≤ d_max."""
    if len(poi_xy) == 0:
        return [np.array([]) for _ in range(len(cell_xy))]
    tree = cKDTree(poi_xy)
    # query_ball_point ist effizienter als pairwise
    idx_lists = tree.query_ball_point(cell_xy, r=d_max)
    out: list[np.ndarray] = []
    for i, idx in enumerate(idx_lists):
        if not idx:
            out.append(np.array([]))
            continue
        d = np.linalg.norm(poi_xy[idx] - cell_xy[i], axis=1)
        out.append(d)
    return out


def category_accessibility(
    grid: gpd.GeoDataFrame,
    pois: gpd.GeoDataFrame,
    *,
    d_max: float = config.WALK_DISTANCE_M,
    beta: float = config.HUFF_BETA,
) -> pd.DataFrame:
    """Berechnet pro Hex-Zelle die Erreichbarkeit je POI-Kategorie."""
    if grid.crs is None or pois.crs is None:
        raise ValueError("Grid und POIs müssen ein CRS haben")
    if grid.crs.to_epsg() != config.EPSG_LV95:
        grid = grid.to_crs(config.EPSG_LV95)
    if pois.crs.to_epsg() != config.EPSG_LV95:
        pois = pois.to_crs(config.EPSG_LV95)

    cell_xy = np.column_stack(
        [grid.geometry.centroid.x.values, grid.geometry.centroid.y.values]
    )

    out = pd.DataFrame({"hex_id": grid["hex_id"].values})

    for cat in config.POI_CATEGORIES:
        sub = pois[pois["category"] == cat]
        log.info("Score-Komponente %s: %d POIs", cat, len(sub))
        poi_xy = np.column_stack(
            [sub.geometry.x.values, sub.geometry.y.values]
        ) if len(sub) else np.empty((0, 2))
        dists = _kdtree_distances(cell_xy, poi_xy, d_max=d_max)
        access = np.array([
            float(np.exp(-beta * (d / d_max)).sum()) if d.size else 0.0
            for d in dists
        ])
        # Normalisierung: 95.-Perzentil-Cap, dann auf [0, 1]
        cap = np.percentile(access, 95) if access.any() else 1.0
        cap = max(cap, 1e-9)
        out[f"acc_{cat}"] = np.minimum(access / cap, 1.0)

    return out


def total_score(access: pd.DataFrame) -> pd.DataFrame:
    """Aggregiert die Kategorien-Accessibilities zu einem Gesamtscore (0–100)."""
    df = access.copy()
    df["score"] = 0.0
    for cat, meta in config.POI_CATEGORIES.items():
        df["score"] += meta["weight"] * df[f"acc_{cat}"]
    df["score"] = (df["score"] * 100).clip(0, 100).round(2)
    return df


def score_with_weights(
    access: pd.DataFrame,
    weights: dict[str, float],
) -> pd.Series:
    """Score (0–100) mit benutzerdefinierten Kategorie-Gewichten.

    Praktisch für Sensitivitäts-Analysen: man füttert den gleichen
    ``access``-DataFrame mit verschiedenen Gewichts-Szenarien und kann so
    prüfen, wie robust das Ranking gegen Gewichts-Wahl ist.
    """
    if abs(sum(weights.values()) - 1.0) > 1e-6:
        raise ValueError(
            f"Gewichte müssen sich zu 1.0 summieren (aktuell {sum(weights.values()):.4f})"
        )
    s = pd.Series(0.0, index=access.index)
    for cat, w in weights.items():
        col = f"acc_{cat}"
        if col not in access.columns:
            raise KeyError(f"Spalte {col!r} fehlt in access — wurde sie berechnet?")
        s += w * access[col]
    return (s * 100).clip(0, 100).round(2)

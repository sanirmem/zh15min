"""Netzwerkbasierter (topografischer) 15-Minute-City-Score.

Im flachen Pfad (siehe :mod:`zh15min.score`) wird die Erreichbarkeit pro
Hex-Zelle aus **Luftlinien-Distanzen** zu den POIs berechnet — das ignoriert
sowohl das Strassennetz als auch die Topografie. Dieses Modul löst beides:

1. Walking-Zeiten werden aus dem **Strassengraph** abgelesen (statt
   Luftlinie). Voraussetzung: der Graph wurde mit
   :func:`zh15min.isochron.add_walk_time_tobler` gewichtet (so dass
   ``time_min`` pro Kante die Tobler-Walking-Zeit enthält).
2. Statt pro Zelle eine Distanz-Suche durchzuführen (~12k Zellen ×
   ~1k POIs) drehen wir die Berechnung um: **pro POI** ein einziges
   ``single_source_dijkstra_path_length`` mit ``cutoff = t_max_min``,
   das alle in 15 Minuten erreichbaren Knoten liefert. Anschliessend
   wird über die Knoten auf die Hex-Zellen aggregiert.

Datenmenge in unserem Setup
---------------------------
* 1 POI-Dijkstra besucht ~3–8k Knoten (statt aller 62k).
* Insgesamt ~1000 POI-Dijkstras → ~30–120 s auf einem Laptop.
* Aggregation auf ~1000 Hex-Zellen ist vektorisiert (NumPy) und kostet
  einen Bruchteil davon.

API
---
* :func:`topographic_accessibility` — Hauptfunktion, liefert pro Hex-Zelle
  eine Accessibilität pro POI-Kategorie (gleiches Format wie
  :func:`zh15min.score.category_accessibility`, nur mit Tobler-Zeiten
  statt Luftlinien-Distanzen).
* :func:`benchmark_dijkstra_per_poi` — misst eine Stichprobe an
  POI-Dijkstras und extrapoliert die Gesamt-Laufzeit. Soll **vor** dem
  vollen Lauf aufgerufen werden, damit man weiss, womit man rechnet.
"""

from __future__ import annotations

import logging
import time
from typing import Iterable

import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd

from . import config

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Hilfs-Routinen
# ---------------------------------------------------------------------------


def _ensure_lv95(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        raise ValueError("GeoDataFrame muss ein CRS haben.")
    if gdf.crs.to_epsg() != config.EPSG_LV95:
        return gdf.to_crs(config.EPSG_LV95)
    return gdf


def _nearest_nodes_for_points(
    graph: nx.MultiDiGraph,
    points_lv95: np.ndarray,
) -> np.ndarray:
    """Liefert für N (x,y)-Punkte (LV95) den jeweils nächsten Graph-Knoten.

    Der OSMnx-Graph hat seine Knoten in WGS84 (Attribute ``x``, ``y`` =
    lon/lat). Wir reprojizieren die Punkte vor der Suche.

    Returns
    -------
    np.ndarray
        Array der Knoten-IDs (gleiche Reihenfolge wie ``points_lv95``).
    """
    if len(points_lv95) == 0:
        return np.array([], dtype=object)
    pts_wgs = (
        gpd.GeoSeries(gpd.points_from_xy(points_lv95[:, 0], points_lv95[:, 1]),
                      crs=config.EPSG_LV95)
        .to_crs(config.EPSG_WGS84)
    )
    xs = pts_wgs.x.to_numpy()
    ys = pts_wgs.y.to_numpy()
    # OSMnx bietet eine vektorisierte Variante:
    return np.asarray(ox.distance.nearest_nodes(graph, xs, ys))


def _dijkstra_times(
    graph: nx.MultiDiGraph,
    source_node,
    cutoff_min: float,
) -> dict:
    """Wrapper um single_source_dijkstra_path_length mit time_min-Gewicht."""
    return nx.single_source_dijkstra_path_length(
        graph, source_node, cutoff=cutoff_min, weight="time_min"
    )


# ---------------------------------------------------------------------------
# Benchmark — soll VOR dem vollen Lauf aufgerufen werden
# ---------------------------------------------------------------------------


def benchmark_dijkstra_per_poi(
    graph: nx.MultiDiGraph,
    pois: gpd.GeoDataFrame,
    *,
    sample_size: int = 10,
    t_max_min: float = config.WALK_TIME_MIN,
) -> dict:
    """Misst die Dijkstra-Laufzeit an einer POI-Stichprobe und extrapoliert.

    Praxisnah: ein voller Lauf über alle POIs kann auf grossen Graphen
    Minuten dauern. Vor dem vollen Run sollte man wissen, ob es 30 s oder
    10 min werden — diese Funktion liefert genau diese Schätzung.

    Returns
    -------
    dict
        Keys: ``sample_size``, ``mean_time_per_poi_s``, ``n_pois_total``,
        ``estimated_total_s``, ``mean_reached_nodes``.
    """
    pois = _ensure_lv95(pois).reset_index(drop=True)
    if len(pois) == 0:
        raise ValueError("POI-DataFrame ist leer.")

    sample = pois.sample(n=min(sample_size, len(pois)), random_state=42)
    sample_xy = np.column_stack([sample.geometry.x.to_numpy(),
                                 sample.geometry.y.to_numpy()])
    sample_nodes = _nearest_nodes_for_points(graph, sample_xy)

    durations = []
    reached = []
    for src in sample_nodes:
        t0 = time.perf_counter()
        times = _dijkstra_times(graph, int(src), cutoff_min=t_max_min)
        durations.append(time.perf_counter() - t0)
        reached.append(len(times))

    mean_per = float(np.mean(durations))
    return {
        "sample_size": len(sample),
        "mean_time_per_poi_s": mean_per,
        "median_time_per_poi_s": float(np.median(durations)),
        "mean_reached_nodes": float(np.mean(reached)),
        "n_pois_total": int(len(pois)),
        "estimated_total_s": mean_per * len(pois),
    }


# ---------------------------------------------------------------------------
# Voller Lauf
# ---------------------------------------------------------------------------


def topographic_accessibility(
    grid: gpd.GeoDataFrame,
    pois: gpd.GeoDataFrame,
    graph: nx.MultiDiGraph,
    *,
    t_max_min: float = config.WALK_TIME_MIN,
    beta: float = config.HUFF_BETA,
    categories: Iterable[str] | None = None,
    progress: bool = True,
) -> pd.DataFrame:
    """Liefert pro Hex-Zelle die Erreichbarkeit je POI-Kategorie (Tobler).

    Methodik (POI-zentriert)
    ------------------------
    Für jede POI :math:`p` der Kategorie c führen wir genau ein
    ``single_source_dijkstra_path_length`` auf dem Tobler-gewichteten
    Graph mit ``cutoff = t_max_min`` durch. Das liefert
    :math:`\\{n \\to t(n,p)\\}` für alle Knoten n innerhalb der Zeitgrenze.

    Pro Hex-Zelle z (mit nächstem Graph-Knoten :math:`n_z`) addieren wir
    den Decay-Beitrag dieses POI:

    .. math::
        A_c(z) \\mathrel{+}= \\exp(-\\beta \\cdot t(n_z, p) / t_{\\max})

    falls :math:`n_z` im 15-Minuten-Radius lag, sonst 0. Anschliessend
    Normalisierung per 95.-Perzentil-Cap (analog zum flachen Pfad).

    Parameter
    ---------
    grid : geopandas.GeoDataFrame
        Hex-Zellen mit Spalte ``hex_id``.
    pois : geopandas.GeoDataFrame
        POIs mit Spalte ``category`` (Werte aus :data:`config.POI_CATEGORIES`).
    graph : networkx.MultiDiGraph
        Walking-Graph mit ``time_min``-Kantengewicht (i. d. R. via
        :func:`zh15min.isochron.add_walk_time_tobler` gesetzt).
    t_max_min : float, default 15
        Zeit-Cutoff der 15-Minuten-Stadt.
    beta : float, default 1.5
        Distance-Decay-Parameter (Huff-Modell).
    categories : iterable of str, optional
        Wenn gesetzt, nur diese Kategorien berechnen. Sonst alle aus
        :data:`config.POI_CATEGORIES`.
    progress : bool, default True
        Ob Fortschritts-Logs ausgegeben werden sollen.
    """
    grid = _ensure_lv95(grid)
    pois = _ensure_lv95(pois).reset_index(drop=True)
    cats = list(categories) if categories else list(config.POI_CATEGORIES.keys())

    # Hex-Zellen: Zentroide → nächster Knoten (einmalig)
    cell_xy = np.column_stack(
        [grid.geometry.centroid.x.to_numpy(),
         grid.geometry.centroid.y.to_numpy()]
    )
    cell_nodes = _nearest_nodes_for_points(graph, cell_xy)
    log.info("Cell→Node-Mapping berechnet für %d Hex-Zellen.", len(grid))

    out = pd.DataFrame({"hex_id": grid["hex_id"].to_numpy()})
    n_cells = len(grid)

    for cat in cats:
        sub = pois[pois["category"] == cat]
        n_pois = len(sub)
        if progress:
            log.info("Kategorie %s: %d POIs → %d Dijkstras", cat, n_pois, n_pois)

        access = np.zeros(n_cells, dtype=np.float64)
        if n_pois == 0:
            out[f"acc_{cat}"] = access
            continue

        poi_xy = np.column_stack([sub.geometry.x.to_numpy(),
                                  sub.geometry.y.to_numpy()])
        poi_nodes = _nearest_nodes_for_points(graph, poi_xy)

        # eindeutige Source-Knoten — wenn mehrere POIs auf den gleichen Knoten
        # mappen, sparen wir Dijkstras
        unique_sources, src_inverse = np.unique(poi_nodes, return_inverse=True)
        if progress and len(unique_sources) < n_pois:
            log.info("  → %d eindeutige Source-Knoten (von %d POIs)",
                     len(unique_sources), n_pois)

        # Per Source-Knoten ein Dijkstra; Beitrag wird n_pois_at_src-fach gezählt
        # (beim Aggregieren).
        t0 = time.perf_counter()
        for k, src in enumerate(unique_sources):
            n_pois_here = int((src_inverse == k).sum())
            times = _dijkstra_times(graph, int(src), cutoff_min=t_max_min)
            if not times:
                continue
            # Vektorisierte Aggregation: pd.Series indexiert von Knoten-ID,
            # reindex auf die cell_nodes-Reihenfolge, NaN für unerreichbare.
            times_s = pd.Series(times, dtype=np.float64)
            cell_t = times_s.reindex(cell_nodes).to_numpy()
            mask = (~np.isnan(cell_t)) & (cell_t <= t_max_min)
            if mask.any():
                access[mask] += n_pois_here * np.exp(-beta * cell_t[mask] / t_max_min)
            if progress and (k + 1) % 100 == 0:
                log.info("  ... %d/%d Sources verarbeitet (%.1fs)",
                         k + 1, len(unique_sources), time.perf_counter() - t0)

        # Normalisierung wie im flachen Pfad
        cap = float(np.percentile(access, 95)) if access.any() else 1.0
        cap = max(cap, 1e-9)
        out[f"acc_{cat}"] = np.minimum(access / cap, 1.0)

    return out

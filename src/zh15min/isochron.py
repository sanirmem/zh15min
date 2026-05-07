"""Isochronen-Berechnung auf einem OSMnx-Walking-Graph.

Wir konvertieren den Graph in metrisches CRS (LV95), gewichten Kanten mit der
Gehzeit (Länge / Geschwindigkeit) und nutzen ``ego_graph`` von NetworkX, um
alle Knoten zu finden, die innerhalb einer Zeitgrenze erreichbar sind. Die
konvexe Hülle dieser Knoten ergibt das Isochron-Polygon.

Zwei Gewichtungs-Varianten stehen bereit:

* :func:`add_walk_time` — flache Annahme, konstant 5 km/h (Default).
* :func:`add_walk_time_tobler` — Tobler-Hiking-Funktion, berücksichtigt
  Steigung pro Kante (Voraussetzung: Graph wurde mit
  :func:`zh15min.elevation.compute_edge_slopes` angereichert).

Beide Funktionen schreiben das Attribut ``time_min`` und sind alternativ
einsetzbar — die topografische Variante überschreibt die flache, wenn sie
nach ihr aufgerufen wird, und umgekehrt.
"""

from __future__ import annotations

import logging
import math

import geopandas as gpd
import networkx as nx
import osmnx as ox
from shapely.geometry import MultiPoint, Point

from . import config

log = logging.getLogger(__name__)


def add_walk_time(graph, speed_kmh: float = config.WALK_SPEED_KMH):
    """Erweitert jede Kante des Graphen um Attribut ``time_min``."""
    speed_m_per_min = speed_kmh * 1000 / 60
    for _u, _v, data in graph.edges(data=True):
        length = data.get("length", 0.0)
        data["time_min"] = float(length) / speed_m_per_min
    return graph


def tobler_speed_kmh(slope: float, max_slope: float = 0.5) -> float:
    """Tobler-Hiking-Funktion: Walking-Geschwindigkeit in km/h.

    Formel: ``W(s) = 6 · exp(-3.5 · |s + 0.05|)``.

    Eigenschaften
    -------------
    * Maximum bei ``s = -0.05`` (5 % bergab) → 6 km/h.
    * Bei ``s = 0`` (flach) → ≈ 5.04 km/h, also nahe an der "5-km/h-Annahme".
    * Bergauf (``s > 0``) langsamer als bergab gleicher Steilheit.
    * ``|s| > max_slope`` wird auf ``±max_slope`` gedeckelt — das fängt
      OSM-Artefakte ab (z. B. Treppen-Edges mit unrealistisch grosser
      Steigung) und verhindert numerisch unsinnig kleine Geschwindigkeiten.

    Parameter
    ---------
    slope : float
        Steigung als Bruch (rise/run); positiv = bergauf, negativ = bergab.
    max_slope : float, default 0.5
        Hard-Clip auf ``±max_slope`` (50 % entspricht ~27°). Werte darüber
        sind in der Praxis Treppen oder Datenfehler.

    Returns
    -------
    float
        Geschwindigkeit in km/h. Liefert für ``slope = None`` (kein DEM-Wert)
        ``config.WALK_SPEED_KMH`` als sinnvollen Fallback.
    """
    if slope is None:
        return float(config.WALK_SPEED_KMH)
    s = max(-max_slope, min(max_slope, float(slope)))
    return 6.0 * math.exp(-3.5 * abs(s + 0.05))


def add_walk_time_tobler(
    graph,
    max_slope: float = 0.5,
    fallback_speed_kmh: float = config.WALK_SPEED_KMH,
):
    """Setzt ``time_min`` pro Kante via Tobler-Hiking-Funktion.

    Voraussetzung: Kanten haben ein Attribut ``slope`` (siehe
    :func:`zh15min.elevation.compute_edge_slopes`). Kanten ohne ``slope``
    (z. B. weil ein Endpunkt ausserhalb des DEM lag) bekommen die
    Walking-Zeit aus ``fallback_speed_kmh`` — so bleibt die Funktion
    robust auch bei lückenhafter DEM-Abdeckung.

    Da OSMnx-Walking-Graphen ``MultiDiGraph`` sind, ist die Steigung pro
    gerichteter Kante verschieden — bergauf und bergab erhalten daher
    **verschiedene** Walking-Zeiten. Das ist genau der Punkt, an dem sich
    der topografische Score vom flachen unterscheidet.

    Parameter
    ---------
    graph : networkx.MultiDiGraph
        Walking-Graph mit ``length`` (m) pro Kante und idealerweise mit
        ``slope`` pro Kante.
    max_slope : float, default 0.5
        An :func:`tobler_speed_kmh` durchgereicht.
    fallback_speed_kmh : float, default config.WALK_SPEED_KMH
        Geschwindigkeit für Kanten ohne valide Steigung.
    """
    n_total = 0
    n_fallback = 0
    for _u, _v, data in graph.edges(data=True):
        length = float(data.get("length", 0.0))
        slope = data.get("slope")
        if slope is None:
            n_fallback += 1
            speed_kmh = fallback_speed_kmh
        else:
            speed_kmh = tobler_speed_kmh(slope, max_slope=max_slope)
        speed_m_per_min = speed_kmh * 1000.0 / 60.0
        data["time_min"] = length / speed_m_per_min if speed_m_per_min > 0 else 0.0
        n_total += 1

    log.info(
        "Tobler-Walking-Zeit gesetzt für %d Kanten (%d via Fallback %.1f km/h, "
        "max_slope=%.0f %%)",
        n_total, n_fallback, fallback_speed_kmh, max_slope * 100,
    )
    return graph


def isochrone_polygon(
    graph,
    point_xy_lv95: tuple[float, float],
    minutes: float = config.WALK_TIME_MIN,
):
    """Liefert ein Polygon (LV95) der Knoten, die in ``minutes`` erreichbar sind."""
    # Nähesten Knoten zum Punkt finden — graph ist in WGS84, Punkt aber in LV95.
    px, py = point_xy_lv95
    # Schnelle Approximation: Ein-Punkt-Reproject reicht
    p_wgs = gpd.GeoSeries([Point(px, py)], crs=config.EPSG_LV95).to_crs(
        config.EPSG_WGS84
    ).iloc[0]
    nearest = ox.distance.nearest_nodes(graph, p_wgs.x, p_wgs.y)

    sub = nx.ego_graph(graph, nearest, radius=minutes, distance="time_min")
    if len(sub.nodes) < 3:
        return None

    pts = [Point(graph.nodes[n]["x"], graph.nodes[n]["y"]) for n in sub.nodes]
    hull = MultiPoint(pts).convex_hull
    return (
        gpd.GeoSeries([hull], crs=config.EPSG_WGS84)
        .to_crs(config.EPSG_LV95)
        .iloc[0]
    )

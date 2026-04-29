"""Isochronen-Berechnung auf einem OSMnx-Walking-Graph.

Wir konvertieren den Graph in metrisches CRS (LV95), gewichten Kanten mit der
Gehzeit (Länge / Geschwindigkeit) und nutzen ``ego_graph`` von NetworkX, um
alle Knoten zu finden, die innerhalb einer Zeitgrenze erreichbar sind. Die
konvexe Hülle dieser Knoten ergibt das Isochron-Polygon.
"""

from __future__ import annotations

import logging

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

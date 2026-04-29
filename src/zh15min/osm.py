"""OpenStreetMap-Helfer: Stadtgrenze laden, POIs nach Kategorie extrahieren.

Wir nutzen OSMnx (>=2.0). OSMnx fragt im Hintergrund die Overpass-API ab und
liefert direkt GeoDataFrames in EPSG:4326.
"""

from __future__ import annotations

import logging

import geopandas as gpd
import osmnx as ox
import pandas as pd

from . import config

log = logging.getLogger(__name__)

# OSMnx 2.x Defaults
ox.settings.use_cache = True
ox.settings.cache_folder = str(config.RAW_DIR / "osmnx_cache")
ox.settings.log_console = False
ox.settings.requests_timeout = 300


def city_boundary(name: str = config.CITY_NAME) -> gpd.GeoDataFrame:
    """Lädt die administrative Grenze der Stadt als GeoDataFrame in WGS84."""
    log.info("Lade Stadtgrenze für %s", name)
    gdf = ox.geocode_to_gdf(name)
    return gdf.to_crs(config.EPSG_WGS84)


def pois_by_category(
    boundary: gpd.GeoDataFrame,
    category: str,
) -> gpd.GeoDataFrame:
    """Holt alle POIs einer Kategorie aus OSM, geclippt auf die Stadtgrenze.

    Parameter
    ---------
    boundary : Polygon-GeoDataFrame in WGS84
    category : Schlüssel aus :data:`config.POI_CATEGORIES`
    """
    if category not in config.POI_CATEGORIES:
        raise KeyError(f"Unbekannte Kategorie: {category!r}")

    tags = config.POI_CATEGORIES[category]["tags"]
    polygon = boundary.unary_union  # Shapely-Polygon

    log.info("Lade POIs %s mit Tags %s", category, tags)
    gdf = ox.features_from_polygon(polygon, tags=tags)

    if gdf.empty:
        log.warning("Keine POIs für Kategorie %s gefunden", category)
        return gpd.GeoDataFrame(
            {"category": [], "name": [], "osmid": []},
            geometry=[],
            crs=config.EPSG_WGS84,
        )

    # Nur Punkte/Polygone behalten, Linien sind hier irrelevant.
    gdf = gdf[gdf.geometry.geom_type.isin(["Point", "Polygon", "MultiPolygon"])]
    # Polygon-POIs (z.B. Spitäler) auf Schwerpunkt reduzieren
    gdf = gdf.copy()
    gdf["geometry"] = gdf.geometry.apply(
        lambda g: g.centroid if g.geom_type in ("Polygon", "MultiPolygon") else g
    )

    # Aufgeräumtes Resultat
    gdf["category"] = category
    keep = ["category", "geometry"]
    if "name" in gdf.columns:
        keep.insert(1, "name")
    if gdf.index.name == "osmid":
        gdf = gdf.reset_index()
        keep.insert(1, "osmid")
    return gdf[[c for c in keep if c in gdf.columns]].reset_index(drop=True)


def all_pois(boundary: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Iteriert über alle Kategorien und konkateniert das Ergebnis."""
    parts: list[gpd.GeoDataFrame] = []
    for cat in config.POI_CATEGORIES:
        try:
            parts.append(pois_by_category(boundary, cat))
        except Exception as exc:  # noqa: BLE001
            log.error("Fehler bei Kategorie %s: %s", cat, exc)
    if not parts:
        raise RuntimeError("Es konnten keine POIs geladen werden")
    return gpd.GeoDataFrame(
        pd.concat(parts, ignore_index=True),
        geometry="geometry",
        crs=config.EPSG_WGS84,
    )


def walk_graph(boundary: gpd.GeoDataFrame):
    """Lädt den begehbaren Strassengraph für das Untersuchungsgebiet."""
    polygon = boundary.unary_union
    log.info("Lade Walking-Graph (kann einige Minuten dauern)…")
    return ox.graph_from_polygon(polygon, network_type="walk", simplify=True)

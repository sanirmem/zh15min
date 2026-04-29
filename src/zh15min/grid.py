"""Erzeugt ein hexagonales Analyse-Gitter über die Stadtgrenze.

Hex-Zellen sind kompakter und in der Nachbarschaftsanalyse fairer als Quadrate.
Wir arbeiten in LV95 (Meter), damit die Distanz-Parameter direkt funktionieren.
"""

from __future__ import annotations

import math

import geopandas as gpd
from shapely.geometry import Polygon

from . import config


def hex_grid(
    boundary: gpd.GeoDataFrame,
    apothem_m: float = config.HEX_RESOLUTION_M,
) -> gpd.GeoDataFrame:
    """Erzeugt ein Hex-Gitter, das die übergebene Grenze überdeckt.

    Parameter
    ---------
    boundary : GeoDataFrame mit beliebigem CRS – wird intern auf LV95 reprojiziert.
    apothem_m : Radius der inneren Kreisscheibe (Apothem) in Metern.

    Rückgabe
    --------
    GeoDataFrame in LV95 mit Spalte ``hex_id``.
    """
    if boundary.crs is None:
        raise ValueError("Grenze ohne CRS")

    boundary_lv95 = boundary.to_crs(config.EPSG_LV95)
    poly = boundary_lv95.unary_union
    minx, miny, maxx, maxy = poly.bounds

    # Geometrie eines flach-liegenden ("flat-top") Hexagons
    a = apothem_m
    side = a * 2 / math.sqrt(3)
    dx = 1.5 * side          # horizontaler Abstand zwischen Mittelpunkten
    dy = 2 * a               # vertikaler Abstand
    half_dy = a

    cells = []
    col = 0
    x = minx
    while x <= maxx + side:
        y_offset = half_dy if col % 2 == 1 else 0
        y = miny - dy
        while y <= maxy + dy:
            cy = y + y_offset
            hexagon = Polygon(
                [
                    (x + side * math.cos(math.radians(60 * i)),
                     cy + side * math.sin(math.radians(60 * i)))
                    for i in range(6)
                ]
            )
            cells.append(hexagon)
            y += dy
        x += dx
        col += 1

    grid = gpd.GeoDataFrame(geometry=cells, crs=config.EPSG_LV95)
    # Nur Zellen behalten, die die Stadt schneiden
    grid = grid[grid.intersects(poly)].copy()
    grid = grid.reset_index(drop=True)
    grid["hex_id"] = grid.index.astype(int)
    grid["centroid_x"] = grid.geometry.centroid.x
    grid["centroid_y"] = grid.geometry.centroid.y
    return grid[["hex_id", "centroid_x", "centroid_y", "geometry"]]

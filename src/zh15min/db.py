"""Hilfsfunktionen für die PostGIS-Verbindung.

Beispiele
---------
>>> from zh15min.db import engine, write_gdf
>>> write_gdf(gdf_pois, "pois", schema="zh15min")
"""

from __future__ import annotations

from contextlib import contextmanager

import geopandas as gpd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from . import config


def engine() -> Engine:
    """Liefert eine SQLAlchemy-Engine zu PostGIS."""
    return create_engine(config.db_url(), future=True, pool_pre_ping=True)


@contextmanager
def conn():
    """Context-Manager um eine Verbindung; commit am Ende, sonst rollback."""
    eng = engine()
    with eng.begin() as c:
        yield c


def ping() -> bool:
    """Test-Query — gibt True zurück, wenn PostGIS antwortet."""
    try:
        with conn() as c:
            v = c.execute(text("SELECT postgis_full_version()")).scalar()
            print(v)
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"PostGIS nicht erreichbar: {exc}")
        return False


def write_gdf(
    gdf: gpd.GeoDataFrame,
    table: str,
    *,
    schema: str = "zh15min",
    if_exists: str = "replace",
    index: bool = False,
) -> None:
    """Schreibt ein GeoDataFrame in PostGIS und legt einen GIST-Index an."""
    if gdf.crs is None:
        raise ValueError("GeoDataFrame muss ein CRS haben")
    gdf.to_postgis(table, engine(), schema=schema, if_exists=if_exists, index=index)
    with conn() as c:
        c.execute(
            text(
                f"CREATE INDEX IF NOT EXISTS {table}_geom_gix "
                f'ON "{schema}"."{table}" USING GIST (geometry);'
            )
        )


def read_gdf(query: str, geom_col: str = "geometry") -> gpd.GeoDataFrame:
    """Liest das Ergebnis einer SQL-Query als GeoDataFrame."""
    return gpd.read_postgis(query, engine(), geom_col=geom_col)

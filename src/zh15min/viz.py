"""Visualisierungs-Helfer: einheitliches Look & Feel für Slides und Notebook."""

from __future__ import annotations

import contextily as cx
import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import branca.colormap as cm

from . import config


def style_score_static(
    grid_score: gpd.GeoDataFrame,
    *,
    figsize: tuple[float, float] = (10, 11),
    title: str = "15-Minute-City-Score Zürich",
    cmap: str = "RdYlGn",
):
    """Statische Karte des Scores mit OSM-Hintergrund."""
    g = grid_score.to_crs(config.EPSG_WEB_MERCATOR)
    fig, ax = plt.subplots(figsize=figsize)
    g.plot(
        column="score",
        cmap=cmap,
        scheme="quantiles",
        k=7,
        legend=True,
        edgecolor="none",
        alpha=0.78,
        ax=ax,
    )
    cx.add_basemap(ax, source=cx.providers.CartoDB.Positron)
    ax.set_axis_off()
    ax.set_title(title, fontsize=14)
    fig.tight_layout()
    return fig, ax


def folium_score(grid_score: gpd.GeoDataFrame) -> folium.Map:
    """Interaktive Folium-Karte des Scores."""
    g = grid_score.to_crs(config.EPSG_WGS84)
    centroid = g.unary_union.centroid

    m = folium.Map(
        location=[centroid.y, centroid.x],
        zoom_start=12,
        tiles="CartoDB positron",
    )

    cmap = cm.linear.RdYlGn_09.scale(0, 100)
    cmap.caption = "15-Minute-City-Score"

    folium.GeoJson(
        g[["hex_id", "score", "geometry"]],
        name="Score",
        style_function=lambda f: {
            "fillColor": cmap(f["properties"]["score"]),
            "color": "#222",
            "weight": 0.2,
            "fillOpacity": 0.75,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["hex_id", "score"],
            aliases=["Hex-Zelle", "Score"],
        ),
    ).add_to(m)
    cmap.add_to(m)
    folium.LayerControl().add_to(m)
    return m

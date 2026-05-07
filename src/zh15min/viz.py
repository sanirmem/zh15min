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


# Kategorie-Farben für POI-Layer (konsistent mit Slide 9)
POI_COLORS: dict[str, str] = {
    "einkauf":    "#065A82",  # primary blue
    "bildung":    "#1C7293",  # teal
    "gesundheit": "#0EA5E9",  # sky
    "erholung":   "#10B981",  # emerald
    "gastro":     "#F59E0B",  # amber
    "oev":        "#8B5CF6",  # purple
}


def folium_score(
    grid_score: gpd.GeoDataFrame,
    quart_summary: gpd.GeoDataFrame | None = None,
    pois: gpd.GeoDataFrame | None = None,
) -> folium.Map:
    """Interaktive Folium-Karte des Scores.

    Parameter
    ---------
    grid_score : GeoDataFrame
        Hex-Gitter mit `hex_id` und `score` (Pflicht-Layer, immer aktiv).
    quart_summary : GeoDataFrame, optional
        Quartier-Polygone mit `name` und `score_mean`. Wenn angegeben, wird
        ein zweiter, umschaltbarer Layer mit den Quartier-Umrissen ergänzt
        — beim Klick zeigt der Tooltip Name + mittlerer Score.
    pois : GeoDataFrame, optional
        POI-Punkte mit ``category``-Spalte. Wenn angegeben, werden sechs
        umschaltbare Layer (einer pro Kategorie) als kleine farbige Kreise
        ergänzt, mit Tooltip „Kategorie: Name".
    """
    g = grid_score.to_crs(config.EPSG_WGS84)
    centroid = g.unary_union.centroid

    m = folium.Map(
        location=[centroid.y, centroid.x],
        zoom_start=12,
        tiles="CartoDB positron",
    )

    cmap = cm.linear.RdYlGn_09.scale(0, 100)
    cmap.caption = "15-Minute-City-Score"

    # Hex-Score (Standard sichtbar)
    folium.GeoJson(
        g[["hex_id", "score", "geometry"]],
        name="Hex-Score (200 m)",
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

    # Quartier-Overlay (optional, standardmässig ausgeblendet)
    if quart_summary is not None:
        q = quart_summary.to_crs(config.EPSG_WGS84).copy()
        # Nur Quartiere mit gültigem Score zeigen
        q = q.dropna(subset=["score_mean"])
        # Spalten für den Tooltip — defensiv, wegen unterschiedlicher Quellen
        keep = ["geometry"]
        for c in ("name", "kuerzel", "score_mean", "score_p25", "n_hex"):
            if c in q.columns:
                keep.append(c)
        q = q[keep].copy()

        if "score_mean" in q.columns:
            q["score_mean"] = q["score_mean"].round(1)
        if "score_p25" in q.columns:
            q["score_p25"] = q["score_p25"].round(1)

        folium.GeoJson(
            q,
            name="Quartiere (offiziell)",
            show=False,  # standardmässig ausgeblendet, per Layer-Control aktivierbar
            style_function=lambda f: {
                "fillColor": cmap(f["properties"].get("score_mean", 0) or 0),
                "color": "#1a1a1a",
                "weight": 1.4,
                "fillOpacity": 0.10,
            },
            highlight_function=lambda f: {
                "weight": 3.0,
                "color": "#000",
                "fillOpacity": 0.25,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=[c for c in ("name", "kuerzel", "score_mean", "n_hex") if c in q.columns],
                aliases=[
                    a for a, c in zip(
                        ["Quartier", "Kürzel", "⌀ Score", "n Hex"],
                        ["name", "kuerzel", "score_mean", "n_hex"],
                    ) if c in q.columns
                ],
                sticky=True,
            ),
        ).add_to(m)

    # POI-Layer (einer pro Kategorie, alle standardmässig ausgeblendet)
    # Per Kategorie auf max. POI_MAX_PER_CATEGORY subsamplen, damit der Browser
    # auch bei tausenden POIs nicht hängt.
    POI_MAX_PER_CATEGORY = 300
    if pois is not None and len(pois) > 0:
        p = pois.to_crs(config.EPSG_WGS84).copy()
        if "category" not in p.columns:
            raise ValueError("POIs müssen Spalte 'category' haben")

        for cat, color in POI_COLORS.items():
            sub = p[p["category"] == cat]
            total = len(sub)
            if total == 0:
                continue
            # Reproduzierbares Subsampling
            if total > POI_MAX_PER_CATEGORY:
                sub = sub.sample(POI_MAX_PER_CATEGORY, random_state=42)
                label = f"POI · {cat} ({POI_MAX_PER_CATEGORY} von {total})"
            else:
                label = f"POI · {cat} ({total})"

            fg = folium.FeatureGroup(name=label, show=False)
            for _, row in sub.iterrows():
                geom = row.geometry
                if geom is None or geom.is_empty:
                    continue
                # Polygon-POIs (z.B. Spitäler) auf Centroid reduzieren
                if geom.geom_type != "Point":
                    geom = geom.centroid
                name = str(row.get("name", "") or "")
                folium.CircleMarker(
                    location=[geom.y, geom.x],
                    radius=3,
                    color=color,
                    weight=0.5,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.75,
                    tooltip=f"{cat}: {name}" if name else cat,
                ).add_to(fg)
            fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m

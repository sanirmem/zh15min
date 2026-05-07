"""Höhen-Anreicherung des Walking-Graphs via SwissALTI3D.

SwissALTI3D ist das hochauflösende digitale Höhenmodell von swisstopo
(0.5 m / 2 m Raster). Wir nutzen einen GeoTIFF-Ausschnitt für Zürich, in
LV95 (EPSG:2056). Der Download erfordert ein swisstopo-Konto und kann
nicht automatisiert werden — Datei wird unter
``data/external/swissalti3d_zh.tif`` erwartet (Pfad in :data:`DEFAULT_DEM_PATH`).

Pipeline für den topografischen Score
-------------------------------------
1. :func:`load_dem` öffnet die GeoTIFF.
2. :func:`enrich_graph_with_elevation` setzt für jeden Knoten Attribut ``z``.
3. :func:`compute_edge_slopes` berechnet pro gerichteter Kante ``slope``.
4. Anschliessend kann :func:`zh15min.isochron.add_walk_time_tobler`
   die Tobler-Geschwindigkeit pro Kante ableiten.

Wichtig: Ein OSMnx-Walking-Graph ist ein ``MultiDiGraph``. Bergauf- und
Bergab-Kante zwischen zwei Knoten u, v existieren als zwei getrennte
Einträge — die Steigung wird daher pro gerichteter Kante einzeln gesetzt
und ist asymmetrisch.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import networkx as nx
import rasterio
from pyproj import Transformer

from . import config

log = logging.getLogger(__name__)

# Standard-Erwartungspfad für die GeoTIFF
DEFAULT_DEM_PATH = config.EXTERNAL_DIR / "swissalti3d_zh.tif"


def load_dem(path: str | Path = DEFAULT_DEM_PATH) -> rasterio.io.DatasetReader:
    """Öffnet die SwissALTI3D-GeoTIFF und liefert das rasterio-Dataset.

    Caller ist verantwortlich, das Dataset zu schliessen — idealerweise
    via ``with rasterio.open(path) as ds:`` oder mit ``ds.close()``.

    Parameter
    ---------
    path : str oder Path
        Pfad zur GeoTIFF. Default: ``data/external/swissalti3d_zh.tif``.

    Raises
    ------
    FileNotFoundError
        Wenn das DEM nicht existiert. Die Fehlermeldung enthält den
        Bezugsweg über swisstopo.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"DEM nicht gefunden: {path}\n"
            "    Manueller Download via swisstopo erforderlich:\n"
            "    https://www.swisstopo.admin.ch/de/geodata/height/alti3d.html\n"
            "    → Ausschnitt Zürich wählen → GeoTIFF (LV95, 2 m Auflösung) → "
            f"Datei nach {path} legen."
        )
    return rasterio.open(path)


def _transformer_to_dem_crs(dem_crs) -> Transformer:
    """pyproj-Transformer von WGS84 (OSMnx-Knoten) auf das DEM-CRS."""
    return Transformer.from_crs(
        f"EPSG:{config.EPSG_WGS84}", dem_crs, always_xy=True
    )


def enrich_graph_with_elevation(
    graph: nx.MultiDiGraph,
    dem_path: str | Path = DEFAULT_DEM_PATH,
) -> nx.MultiDiGraph:
    """Setzt für jeden Knoten ein Attribut ``z`` = Höhe in Metern.

    OSMnx-Knoten haben ``x`` (Längengrad) und ``y`` (Breitengrad) in WGS84.
    Wir reprojizieren on-the-fly auf das DEM-CRS (üblicherweise LV95) und
    sampeln die Höhen-Werte aus Band 1.

    Knoten ausserhalb der Raster-Bounds bekommen ``z = None``. Solche
    Kanten werden in :func:`compute_edge_slopes` ignoriert.

    Parameter
    ---------
    graph : networkx.MultiDiGraph
        OSMnx-Walking-Graph (Knoten haben ``x``, ``y`` in WGS84).
    dem_path : str oder Path
        Pfad zur GeoTIFF.
    """
    log.info("Lade DEM von %s", dem_path)
    with rasterio.open(dem_path) as ds:
        log.info(
            "DEM: CRS=%s, Bounds=%s, Auflösung=%s",
            ds.crs, tuple(round(b, 1) for b in ds.bounds), ds.res,
        )
        nodata = ds.nodata
        bounds = ds.bounds  # (left, bottom, right, top) im DEM-CRS

        transformer = _transformer_to_dem_crs(ds.crs)

        # Sammle alle Knoten + Koordinaten, projiziert auf DEM-CRS
        node_ids = list(graph.nodes)
        coords_dem: list[tuple[float, float]] = []
        for n in node_ids:
            lon = graph.nodes[n]["x"]
            lat = graph.nodes[n]["y"]
            x_dem, y_dem = transformer.transform(lon, lat)
            coords_dem.append((x_dem, y_dem))

        # Punkte ausserhalb der Bounds: z bleibt None.
        # Innerhalb: in einem Schwung samplen (effizient).
        in_bounds: list[bool] = [
            (bounds.left <= x <= bounds.right) and (bounds.bottom <= y <= bounds.top)
            for x, y in coords_dem
        ]
        sample_coords = [c for c, ok in zip(coords_dem, in_bounds) if ok]

        elevations: list[float | None] = []
        if sample_coords:
            samples_iter = ds.sample(sample_coords, indexes=1)
            sampled_values = [next(samples_iter) for _ in sample_coords]
        else:
            sampled_values = []

        # Wieder in die Reihenfolge der node_ids einsortieren
        sample_idx = 0
        for ok in in_bounds:
            if ok:
                val = float(sampled_values[sample_idx][0])
                if nodata is not None and val == nodata:
                    elevations.append(None)
                else:
                    elevations.append(val)
                sample_idx += 1
            else:
                elevations.append(None)

    for node_id, z in zip(node_ids, elevations):
        graph.nodes[node_id]["z"] = z

    n_with_z = sum(1 for n in graph.nodes if graph.nodes[n].get("z") is not None)
    log.info("Höhe gesetzt für %d von %d Knoten", n_with_z, len(graph.nodes))
    return graph


def compute_edge_slopes(graph: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """Pro gerichteter Kante ``slope = (z_v − z_u) / length`` setzen.

    Steigung ist asymmetrisch: bergauf positiv, bergab negativ. Auf einem
    ``MultiDiGraph`` werden u→v und v→u als getrennte Kanten gespeichert,
    erhalten also entgegengesetzte Vorzeichen. Das Ergebnis wird in
    :data:`time_min` (durch :func:`zh15min.isochron.add_walk_time_tobler`)
    in eine asymmetrische Walking-Zeit übersetzt.

    Kanten ohne valide Höhen-Information oder mit ``length <= 0`` werden
    übersprungen (``slope = None``).
    """
    if not isinstance(graph, nx.MultiDiGraph):
        log.warning(
            "Graph ist kein MultiDiGraph (%s) — Steigungs-Asymmetrie kann "
            "nicht garantiert werden.", type(graph).__name__,
        )

    n_total = graph.number_of_edges()
    n_skipped = 0

    for u, v, key, data in graph.edges(keys=True, data=True):
        z_u = graph.nodes[u].get("z")
        z_v = graph.nodes[v].get("z")
        length = data.get("length", 0)

        if z_u is None or z_v is None or not length or length <= 0:
            data["slope"] = None
            n_skipped += 1
            continue

        data["slope"] = (z_v - z_u) / float(length)

    log.info(
        "Steigung gesetzt für %d von %d Kanten (%d übersprungen, da Höhe/Länge fehlt)",
        n_total - n_skipped, n_total, n_skipped,
    )
    return graph


def slope_summary(graph: nx.MultiDiGraph) -> dict[str, float]:
    """Statistische Übersicht der Kanten-Steigungen — nützlich fürs Notebook.

    Rückgabe enthält:
        - n_edges_with_slope, n_edges_total
        - mean_abs_slope, max_abs_slope (in Prozent: ×100 für menschliche Lesbarkeit)
        - p25 / p50 / p75 / p95 der absoluten Steigungen (in Prozent)
    """
    import numpy as np

    slopes = [
        d["slope"]
        for _, _, _, d in graph.edges(keys=True, data=True)
        if d.get("slope") is not None
    ]
    n_total = graph.number_of_edges()
    if not slopes:
        return {"n_edges_with_slope": 0, "n_edges_total": n_total}

    arr = np.abs(np.array(slopes)) * 100  # in Prozent
    return {
        "n_edges_with_slope": len(slopes),
        "n_edges_total": n_total,
        "mean_abs_slope_pct": float(arr.mean()),
        "p25_abs_slope_pct": float(np.percentile(arr, 25)),
        "p50_abs_slope_pct": float(np.percentile(arr, 50)),
        "p75_abs_slope_pct": float(np.percentile(arr, 75)),
        "p95_abs_slope_pct": float(np.percentile(arr, 95)),
        "max_abs_slope_pct": float(arr.max()),
    }

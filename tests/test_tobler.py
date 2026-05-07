"""Tests für die Tobler-Hiking-Funktion und die Kanten-Gewichtung."""

from __future__ import annotations

import math

import networkx as nx
import pytest

from zh15min import config
from zh15min.isochron import (
    add_walk_time,
    add_walk_time_tobler,
    tobler_speed_kmh,
)


# ---------------------------------------------------------------------------
# Reine Funktion: tobler_speed_kmh
# ---------------------------------------------------------------------------


def test_tobler_optimum_bergab_5_prozent():
    """Tobler-Maximum liegt bei s = -0.05 (5 % bergab) und beträgt 6 km/h."""
    assert tobler_speed_kmh(-0.05) == pytest.approx(6.0, abs=1e-9)


def test_tobler_flach_nahe_5_kmh():
    """Bei flachem Gelände (s = 0) liefert Tobler ≈ 5.04 km/h."""
    expected = 6.0 * math.exp(-3.5 * 0.05)
    assert tobler_speed_kmh(0.0) == pytest.approx(expected)
    assert 5.0 < tobler_speed_kmh(0.0) < 5.1


def test_tobler_bergauf_langsamer_als_bergab():
    """Bei gleichem |s| ist bergauf (s > 0) langsamer als bergab (s < 0)."""
    for slope in (0.05, 0.10, 0.20, 0.30):
        assert tobler_speed_kmh(+slope) < tobler_speed_kmh(-slope)


def test_tobler_clipping_bei_extremen_slopes():
    """Slopes über max_slope werden auf max_slope gedeckelt (kein Crash, kein 0)."""
    # +500 % Slope (OSM-Treppen-Artefakt) → wie +50 % behandelt
    speed_clipped = tobler_speed_kmh(5.0, max_slope=0.5)
    speed_at_clip = tobler_speed_kmh(0.5, max_slope=0.5)
    assert speed_clipped == pytest.approx(speed_at_clip)
    # … und immer positiv (kein Division-by-zero in add_walk_time_tobler)
    assert speed_clipped > 0


def test_tobler_none_liefert_fallback():
    """Slope = None (DEM-Lücke) liefert WALK_SPEED_KMH als Fallback."""
    assert tobler_speed_kmh(None) == pytest.approx(config.WALK_SPEED_KMH)


# ---------------------------------------------------------------------------
# Graph-Integration: add_walk_time_tobler
# ---------------------------------------------------------------------------


def _toy_graph() -> nx.MultiDiGraph:
    """Mini-Graph mit drei Kanten: bergauf, bergab, flach."""
    g = nx.MultiDiGraph()
    g.add_node("A", x=8.5, y=47.4)
    g.add_node("B", x=8.5, y=47.4)
    g.add_node("C", x=8.5, y=47.4)
    g.add_node("D", x=8.5, y=47.4)
    # 100 m flache Kante
    g.add_edge("A", "B", key=0, length=100.0, slope=0.0)
    # 100 m bergauf 10 %
    g.add_edge("B", "C", key=0, length=100.0, slope=+0.10)
    # 100 m bergab 10 %
    g.add_edge("C", "B", key=0, length=100.0, slope=-0.10)
    # 100 m ohne Slope (DEM-Lücke)
    g.add_edge("C", "D", key=0, length=100.0, slope=None)
    return g


def test_add_walk_time_tobler_setzt_time_min_pro_kante():
    g = _toy_graph()
    add_walk_time_tobler(g)
    for _u, _v, _k, data in g.edges(keys=True, data=True):
        assert "time_min" in data
        assert data["time_min"] > 0


def test_bergauf_dauert_laenger_als_bergab():
    """Auf MultiDiGraph: gleiche Länge, aber bergauf-Kante hat grösseres time_min."""
    g = _toy_graph()
    add_walk_time_tobler(g)
    t_up = g.edges["B", "C", 0]["time_min"]
    t_down = g.edges["C", "B", 0]["time_min"]
    assert t_up > t_down


def test_kante_ohne_slope_nutzt_fallback_5_kmh():
    """slope=None → time_min entspricht 5 km/h auf der Kante."""
    g = _toy_graph()
    add_walk_time_tobler(g)
    t_none = g.edges["C", "D", 0]["time_min"]
    expected = 100.0 / (config.WALK_SPEED_KMH * 1000.0 / 60.0)
    assert t_none == pytest.approx(expected)


def test_add_walk_time_tobler_aendert_existierendes_add_walk_time_nicht():
    """Reine Sicherstellung, dass die flache Funktion unverändert bleibt."""
    g = _toy_graph()
    # erst flach gewichten
    add_walk_time(g)
    flat_times = {(u, v, k): d["time_min"] for u, v, k, d in g.edges(keys=True, data=True)}
    # flach erneut → identische Werte
    add_walk_time(g)
    for k, t in flat_times.items():
        u, v, kk = k
        assert g.edges[u, v, kk]["time_min"] == pytest.approx(t)

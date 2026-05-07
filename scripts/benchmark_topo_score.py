"""Benchmark: misst Dijkstra-Laufzeit für den topografischen Score.

Ablauf
------
1. Lädt Tobler-gewichteten Walking-Graph (zh_walk_graph_topo.graphml).
2. Wendet add_walk_time_tobler() an (setzt time_min pro Kante).
3. Lädt 8092 POIs.
4. Misst die Laufzeit von 10 zufällig gezogenen POI-Dijkstras (cutoff=15min)
   und extrapoliert auf die volle Anzahl POIs.

Ausgabe ist die geschätzte Gesamt-Laufzeit für topographic_accessibility().
Damit kann man entscheiden, ob der volle Lauf praktikabel ist (z. B. < 5 min)
oder ob man Anpassungen braucht (kleinerer Cutoff, weniger Kategorien etc.).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import logging

import geopandas as gpd
import osmnx as ox

from zh15min import config
from zh15min.isochron import add_walk_time_tobler
from zh15min.score_network import benchmark_dijkstra_per_poi

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("benchmark")


def main() -> int:
    graph_path = ROOT / "data" / "processed" / "zh_walk_graph_topo.graphml"
    pois_path = ROOT / "data" / "processed" / "zh_pois.gpkg"

    if not graph_path.exists():
        log.error("Topo-Graph fehlt: %s — bitte zuerst NB02b ausführen.", graph_path)
        return 1
    if not pois_path.exists():
        log.error("POIs fehlen: %s", pois_path)
        return 1

    log.info("Lade Tobler-Graph aus %s ...", graph_path.name)
    t0 = time.perf_counter()
    G = ox.load_graphml(graph_path)
    # GraphML serialisiert alles als String → 'slope' und 'length' zurück zu float
    for _u, _v, data in G.edges(data=True):
        if "slope" in data and isinstance(data["slope"], str):
            data["slope"] = float(data["slope"]) if data["slope"] not in ("None", "") else None
        if "length" in data and isinstance(data["length"], str):
            data["length"] = float(data["length"])
    log.info("Graph geladen: %d Knoten / %d Kanten (%.1fs)",
             len(G.nodes), len(G.edges), time.perf_counter() - t0)

    log.info("Setze Tobler-time_min auf alle Kanten ...")
    t0 = time.perf_counter()
    add_walk_time_tobler(G)
    log.info("Fertig (%.1fs).", time.perf_counter() - t0)

    log.info("Lade POIs aus %s ...", pois_path.name)
    pois_all = gpd.read_file(pois_path, layer="all")
    log.info("POIs: %d Features", len(pois_all))

    log.info("Benchmark — 10 POI-Dijkstras ...")
    bench = benchmark_dijkstra_per_poi(G, pois_all, sample_size=10)

    print()
    print("================== BENCHMARK ==================")
    print(f"  Sample-Grösse:                {bench['sample_size']}")
    print(f"  Mean Zeit pro POI:            {bench['mean_time_per_poi_s']*1000:.0f} ms")
    print(f"  Median Zeit pro POI:          {bench['median_time_per_poi_s']*1000:.0f} ms")
    print(f"  Mean erreichte Knoten / POI:  {bench['mean_reached_nodes']:.0f}")
    print(f"  Anzahl POIs total:            {bench['n_pois_total']}")
    print(f"  → Geschätzte Gesamt-Laufzeit: {bench['estimated_total_s']:.1f} s "
          f"({bench['estimated_total_s']/60:.1f} min)")
    print("===============================================")
    print()
    print("Hinweis: die Schätzung ist linear extrapoliert. Die wirkliche")
    print("Laufzeit kann etwas tiefer liegen (mehrere POIs auf gleichem")
    print("Source-Knoten ⇒ Dedup spart Dijkstras).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

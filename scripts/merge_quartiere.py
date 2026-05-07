"""Merge Stadt-Zürich-Quartiere: Polygone (V) + Beschriftungs-Punkte (B_P).

Hintergrund:
    Der WFS-Endpunkt der Stadt Zürich für statistische Quartiere lieferte zum
    Auswertungszeitpunkt HTTP 500. Als Fallback laden wir die offiziellen
    GeoJSON-Layer manuell von:

        https://www.stadt-zuerich.ch/geodaten/download/Statistische_Quartiere
        → Service-Schnittstellen → GeoJSON

    Wir bekommen dabei drei Files:
        ADM_STATISTISCHE_QUARTIERE_V.json     — Polygone (objid, objectid, geometry)
        ADM_STATISTISCHE_QUARTIERE_B_P.json   — Beschriftungs-Punkte (objid, name, kuerzel)
        ADM_STATISTISCHE_QUARTIERE_MAP.json   — Karten-Variante (kein zusätzlicher Wert)

    Wichtig: ``objid`` ist nicht zwischen V und B_P konsistent (es ist nur ein
    interner Layer-Zähler). Wir mergen daher per **räumlichem Join**: jeder
    Beschriftungspunkt liegt innerhalb genau eines Polygons.

Aufruf::

    python scripts/merge_quartiere.py \\
        path/to/ADM_STATISTISCHE_QUARTIERE_V.json \\
        path/to/ADM_STATISTISCHE_QUARTIERE_B_P.json \\
        data/external/quartiere.geojson
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def point_in_polygon(point: tuple[float, float], ring: list[list[float]]) -> bool:
    """Klassischer Ray-Casting-Algorithmus für Punkt-in-Polygon."""
    x, y = point
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi
        ):
            inside = not inside
        j = i
    return inside


def merge(v_path: Path, bp_path: Path, out_path: Path) -> None:
    with v_path.open() as f:
        v = json.load(f)
    with bp_path.open() as f:
        bp = json.load(f)

    merged = {
        "type": "FeatureCollection",
        "name": "Statistische Quartiere Stadt Zürich (offiziell, 34)",
        "features": [],
    }

    for vfeat in v["features"]:
        poly = vfeat["geometry"]
        rings = (
            [poly["coordinates"]] if poly["type"] == "Polygon" else poly["coordinates"]
        )

        matched = None
        for bpfeat in bp["features"]:
            pt = bpfeat["geometry"]["coordinates"]
            for ring_set in rings:
                outer = ring_set[0]
                if point_in_polygon(pt, outer):
                    matched = bpfeat["properties"]
                    break
            if matched:
                break

        merged["features"].append(
            {
                "type": "Feature",
                "geometry": vfeat["geometry"],
                "properties": {
                    "objid": vfeat["properties"]["objid"],
                    "objectid": vfeat["properties"]["objectid"],
                    "name": matched.get("name") if matched else None,
                    "kuerzel": matched.get("kuerzel") if matched else None,
                },
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)

    matched_count = sum(1 for f in merged["features"] if f["properties"]["name"])
    print(f"OK — {len(merged['features'])} Quartiere gemerged ({matched_count} mit Namen).")
    print(f"     gespeichert nach {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(2)
    merge(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))

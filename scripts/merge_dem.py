"""Führt die heruntergeladenen SwissALTI3D-Kacheln zu einer GeoTIFF zusammen.

Erwartet die Kacheln in ``data/external/swissalti3d_tiles/`` (so wie sie
``download_dem_tiles.py`` ablegt) und schreibt das Ergebnis nach
``data/external/swissalti3d_zh.tif`` — exakt der Pfad, den
``src/zh15min/elevation.py:DEFAULT_DEM_PATH`` erwartet.

Optionales Clipping auf den Bounding-Box der Stadt Zürich verhindert,
dass die GeoTIFF unnötig gross wird, falls die swisstopo-Kacheln über
die Gemeindegrenze hinaus heruntergeladen wurden.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TILES_DIR = ROOT / "data" / "external" / "swissalti3d_tiles"
DEFAULT_OUTPUT = ROOT / "data" / "external" / "swissalti3d_zh.tif"

# Stadt Zürich Bounding-Box in LV95 (etwas grosszügig — wir clippen später
# im Notebook ohnehin pro Knoten). Aus den Quartiergrenzen abgeleitet.
ZURICH_BBOX_LV95 = (2675500.0, 1241500.0, 2691500.0, 1255500.0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tiles-dir",
        type=Path,
        default=DEFAULT_TILES_DIR,
        help=f"Verzeichnis mit den Kacheln (Default: {DEFAULT_TILES_DIR.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Ziel-GeoTIFF (Default: {DEFAULT_OUTPUT.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--no-clip",
        action="store_true",
        help="Auf Bounding-Box clippen NICHT durchführen (Default: clippen).",
    )
    parser.add_argument(
        "--pattern",
        default="*.tif",
        help="Glob-Pattern für die Kacheln (Default: *.tif)",
    )
    args = parser.parse_args()

    try:
        import rasterio
        from rasterio.merge import merge
    except ImportError:
        print(
            "FEHLER: rasterio nicht installiert. Bitte `pip install rasterio` (oder via conda).",
            file=sys.stderr,
        )
        return 1

    tiles = sorted(args.tiles_dir.glob(args.pattern))
    if not tiles:
        print(
            f"FEHLER: Keine Kacheln in {args.tiles_dir} gefunden (Pattern: {args.pattern}).",
            file=sys.stderr,
        )
        return 1
    print(f"{len(tiles)} Kachel(n) gefunden in {args.tiles_dir}")

    sources = [rasterio.open(t) for t in tiles]
    try:
        bounds = ZURICH_BBOX_LV95 if not args.no_clip else None
        if bounds:
            print(f"Clipping auf Bounding-Box (LV95): {bounds}")
        mosaic, transform = merge(sources, bounds=bounds)

        meta = sources[0].meta.copy()
        meta.update(
            {
                "driver": "GTiff",
                "height": mosaic.shape[1],
                "width": mosaic.shape[2],
                "transform": transform,
                "compress": "deflate",
                "tiled": True,
                "predictor": 3,  # für floats: empfohlen
                "BIGTIFF": "IF_SAFER",
            }
        )

        args.output.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(args.output, "w", **meta) as dst:
            dst.write(mosaic)
    finally:
        for s in sources:
            s.close()

    size_mb = args.output.stat().st_size / 1024 / 1024
    with rasterio.open(args.output) as ds:
        print()
        print(f"Geschrieben: {args.output}  ({size_mb:.1f} MB)")
        print(f"  CRS:    {ds.crs}")
        print(f"  Shape:  {ds.shape}")
        print(f"  Bounds: {tuple(round(b, 1) for b in ds.bounds)}")
        print(f"  Auflösung: {ds.res}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

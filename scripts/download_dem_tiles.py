"""Lädt SwissALTI3D-Kacheln gemäss swisstopo-CSV-Export herunter.

Nutzung
-------
1. Auf https://www.swisstopo.admin.ch/de/geodata/height/alti3d.html
   → "swissALTI3D Daten beziehen" → Auswahl mit Gemeinde Zürich,
   Format = "Cloud Optimized GeoTIFF" oder "GeoTIFF",
   Auflösung = 2 m, CRS = LV95, Zeitstand = aktuell.
2. "Suchen" → "Alle Links exportieren" → CSV abspeichern (z. B.
   ~/Downloads/ch.swisstopo.swissalti3d-XYZ.csv).
3. python scripts/download_dem_tiles.py <pfad-zur-csv>
   (Default: data/external/swissalti3d_tiles)

Anschliessend `python scripts/merge_dem.py` aufrufen, um die Kacheln zu
einer einzigen GeoTIFF zusammenzuführen.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TILES_DIR = ROOT / "data" / "external" / "swissalti3d_tiles"
USER_AGENT = "zh15min/1.0 (FS2026 ZHAW project)"


def find_url_column(header: list[str]) -> int:
    """Suche heuristisch die Spalte mit den Tile-URLs."""
    for i, name in enumerate(header):
        if name.strip().lower() in {"url", "link", "downloadurl", "download_url"}:
            return i
    # Fallback: erste Spalte, deren Werte mit http beginnen — wird beim ersten
    # Daten-Sample geprüft. Hier liefern wir -1, der Caller löst das auf.
    return -1


def parse_csv(csv_path: Path) -> list[str]:
    """Liest die swisstopo-CSV und liefert eine Liste der Download-URLs."""
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        raise ValueError(f"CSV ist leer: {csv_path}")

    # Variante 1: Header vorhanden
    header = rows[0]
    url_col = find_url_column(header)

    # Variante 2: kein Header — swisstopo liefert manchmal nur eine Spalte
    if url_col == -1:
        # Erste Zeile auf URL prüfen
        if header and header[0].strip().lower().startswith("http"):
            return [r[0].strip() for r in rows if r and r[0].strip().startswith("http")]

        # Andernfalls: in Header-Zeile die Spalte finden, die im ersten Datensatz
        # mit http beginnt
        if len(rows) > 1:
            first_data = rows[1]
            for i, val in enumerate(first_data):
                if val.strip().startswith("http"):
                    url_col = i
                    break

    if url_col == -1:
        raise ValueError(
            f"Keine URL-Spalte gefunden. Erste Zeile: {header}\n"
            "Bitte CSV manuell prüfen oder URLs in eine Datei mit einer URL pro "
            "Zeile umkopieren."
        )

    urls: list[str] = []
    data_rows = rows[1:] if any(c for c in header if not c.strip().startswith("http")) else rows
    for row in data_rows:
        if len(row) > url_col:
            v = row[url_col].strip()
            if v.startswith("http"):
                urls.append(v)
    return urls


def filename_from_url(url: str) -> str:
    name = Path(urlparse(url).path).name
    return name or "tile.tif"


def download(url: str, dest: Path, timeout: float = 60.0) -> tuple[bool, str]:
    """Lädt eine einzelne URL nach dest. Skippt, wenn dest bereits existiert."""
    if dest.exists() and dest.stat().st_size > 0:
        return True, "skip-existing"

    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=timeout) as resp:
            data = resp.read()
    except Exception as e:  # noqa: BLE001
        return False, f"error: {e}"

    if not data:
        return False, "error: empty response"

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return True, f"ok ({len(data) / 1024 / 1024:.1f} MB)"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path, help="swisstopo-CSV mit Download-Links")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_TILES_DIR,
        help=f"Zielverzeichnis (Default: {DEFAULT_TILES_DIR.relative_to(ROOT)})",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Nur die ersten N Kacheln laden (zum Testen).",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.2,
        help="Pause zwischen Requests in Sekunden (Default: 0.2).",
    )
    args = parser.parse_args()

    if not args.csv_path.exists():
        print(f"FEHLER: CSV nicht gefunden: {args.csv_path}", file=sys.stderr)
        return 1

    urls = parse_csv(args.csv_path)
    print(f"CSV gelesen: {len(urls)} URL(s) gefunden")
    if args.limit:
        urls = urls[: args.limit]
        print(f"Limit aktiv: lade nur die ersten {len(urls)}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Zielverzeichnis: {args.out_dir}")
    print()

    n_ok = n_skip = n_fail = 0
    for i, url in enumerate(urls, 1):
        dest = args.out_dir / filename_from_url(url)
        success, msg = download(url, dest)
        prefix = f"[{i:>4}/{len(urls)}]"
        if success:
            if "skip" in msg:
                n_skip += 1
            else:
                n_ok += 1
            print(f"{prefix} {dest.name:<60} {msg}")
        else:
            n_fail += 1
            print(f"{prefix} {dest.name:<60} {msg}", file=sys.stderr)
        time.sleep(args.sleep)

    print()
    print(f"Fertig. ok={n_ok}  skip={n_skip}  fail={n_fail}")
    return 0 if n_fail == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())

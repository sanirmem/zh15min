"""Pytest-Setup: macht ``src/zh15min`` importierbar, ohne dass das Paket
installiert sein muss."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

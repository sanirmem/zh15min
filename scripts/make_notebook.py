"""Hilfs-Skript: Schreibt Jupyter-Notebooks (.ipynb) als JSON.

Aufruf:
    from make_notebook import nb, md, code, save
    save("01_load_osm.ipynb", nb([md("# Titel"), code("print('hi')")]))
"""

import json
from pathlib import Path


def md(*lines: str) -> dict:
    src = "\n".join(lines)
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": src.splitlines(keepends=True),
    }


def code(*lines: str) -> dict:
    src = "\n".join(lines)
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": src.splitlines(keepends=True),
    }


def nb(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (zh15min)",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "pygments_lexer": "ipython3",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def save(path: str | Path, notebook: dict) -> None:
    Path(path).write_text(
        json.dumps(notebook, indent=1, ensure_ascii=False),
        encoding="utf-8",
    )

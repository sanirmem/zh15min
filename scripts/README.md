# Scripts

Helfer-Skripte für Wartung & Re-Generierung des Projekts.

| Datei | Zweck |
|---|---|
| `build_slides.js` | Erzeugt `reports/zh15min_slides.pptx` mit `pptxgenjs`. Aufruf: `node scripts/build_slides.js`. |
| `make_notebook.py` | Hilfsbibliothek (Funktionen `md`, `code`, `nb`, `save`) zum Erzeugen valider `.ipynb`-Dateien. |
| `build_nb_01.py` … `build_nb_07.py` | Re-generieren die jeweiligen Notebooks aus den Skripten — nützlich, wenn ihr Notebook-Skelette anpassen wollt, ohne Jupyter zu öffnen. |

## Workflow zum Re-Build

```bash
# Notebooks regenerieren (aus den Build-Skripten)
for f in scripts/build_nb_*.py; do python3 "$f"; done

# Slides neu generieren
node scripts/build_slides.js
```

Anschliessend `git diff notebooks/` & `git diff reports/` prüfen.

# KI-Einsatz im Projekt — Transparenz-Anhang

Gemäss Kurs-Hinweis (FS 2026, Folie zu „Software used in this course": ChatGPT 5.x, MS Copilot) und der Anregung im Projekt-Briefing dokumentieren wir hier offen, wie wir generative KI im Projekt eingesetzt haben.

## 1. Eingesetzte Werkzeuge

| Werkzeug | Zweck |
|---|---|
| **Claude (Sonnet/Opus 4.x)** | Code-Generierung, Architektur, Datenquellen-Recherche, Methodendokumentation |
| **GitHub Copilot** | Inline-Autocompletion in den Notebooks |
| **ChatGPT 5.x** | Zweitmeinung beim Refactoring, Hypothesen-Brainstorming |

## 2. Wo & Wie

### 2.1 Code-Optimierung

Initiale Score-Berechnung war eine doppelte for-Schleife (Zellen × POIs) → O(n·m). KI-Vorschlag: `scipy.spatial.cKDTree.query_ball_point(cells, r=d_max)` reduziert auf O((n+m)·log(n)). Resultat: Score-Berechnung in < 1 s für 744 Hex-Zellen × 8 092 POIs (vs. mehrere Minuten naive O(n·m)).

### 2.2 Hypothesen-Generierung

Ausgangsfrage: „Welche zwei testbaren Hypothesen lassen sich aus dem 15-Minuten-Stadt-Konzept und Zürcher Immobilienmarkt ableiten?" → KI lieferte sechs Vorschläge, wir haben zwei (H1: Score↔Mietpreis-Korrelation, H2: „Wüsteneffekt" in Neubaugebieten) übernommen und literarisch verankert.

### 2.3 Datenquellen-Recherche

KI hat uns die korrekten WFS-Endpunkte für Stadt Zürich Open Data und den BFS-Download-Link für STATPOP 2023 geliefert. Wir haben jeden Link manuell überprüft (HTTP 200, plausible Spaltenstruktur) bevor wir ihn ins Notebook übernommen haben.

### 2.4 Methodische Beratung

Frage: „Welcher Distance-Decay-Parameter ist für Walking-Erreichbarkeit angemessen?" → Empfehlung Huff-Modell mit β ≈ 1.5 (siehe Huff 1964; Sevtsuk & Mekonnen 2012). Wir haben die Empfehlung in `src/zh15min/config.py:HUFF_BETA` als Parameter exponiert, sodass eine Sensitivitäts-Analyse möglich ist.

### 2.5 Topografische Score-Erweiterung

Aufgabenstellung: „Wir wollen den flachen 5-km/h-Score topografisch korrigieren — was ist die saubere Architektur?" → KI hat einen 4-Schritt-Plan entworfen:

1. **`src/zh15min/elevation.py`** — Höhen-Anreicherung des OSMnx-Graphs aus dem SwissALTI3D-DEM. Inklusive Reprojektion WGS84→LV95 via pyproj-Transformer und vektorisiertem `rasterio.sample()` für 60'000+ Knoten.
2. **`src/zh15min/isochron.py`** — Tobler-Hiking-Funktion `W = 6·exp(-3.5·|s + 0.05|)` als zusätzliche Kanten-Gewichtung, **additiv** zum bestehenden flat-Pfad. Slope-Clipping bei ±50 % gegen OSM-Treppen-Artefakte (392 % Maxima durch übereinander liegende Edge-Endpunkte).
3. **`src/zh15min/score_network.py`** — POI-zentriertes `single_source_dijkstra_path_length` mit 15-Min-Cutoff. Statt 744 Zell-Dijkstras × 6 Kategorien laufen wir pro POI einen Dijkstra; nach Source-Knoten-Dedup landen wir bei ~3 000 unique Dijkstras für alle 8 092 POIs. Ergebnis: ~33 s Gesamtlaufzeit.
4. **`notebooks/06b_delta.ipynb`** — Δ-Visualisierung mit drei Karten und Quartier-Ranking.

KI-Beitrag: Architektur-Vorschlag, Tobler-Formel-Implementierung, Performance-Optimierung (vektorisierter Inner-Loop via `pd.Series.reindex` statt Python-`for`-Schleife). Wir haben den Code anhand von 9 Pytest-Cases verifiziert (Tobler-Maximum bei −5 %, Bergauf-Bergab-Asymmetrie, Slope-Clipping, None-Fallback, Graph-Integration) — alle Tests grün. Plausibilitätsbefund auf 34 Quartieren (Top-Verlierer Oberstrass −13.8, Fluntern −11.2; Top-Gewinner Mühlebach +8.5, Seefeld +6.3) entspricht der Topografie Zürichs — die KI-vorgeschlagene Implementierung verhält sich wie erwartet.

### 2.6 Slide-Deck-Generation

`scripts/build_slides.js` ist ein pptxgenjs-Generator, der das 20-folige Deck reproduzierbar aus Code erstellt (statt manueller PowerPoint-Bearbeitung). KI hat das Layout-Framework (Cards, Section-Tags, Big-Stats, Footer) entworfen; Inhalte sind manuell überprüft, jede Datenaussage gegen das jeweilige Notebook-Output-Cell verglichen.

## 3. Was wir nicht durch KI machen lassen

- Keine vollautomatische **Interpretation** der Resultate. Schlussfolgerungen schreiben wir selbst.
- Keine **Plagiate**: Quellen prüfen wir manuell.
- Keine **erfundenen** Datenquellen. Jeder Endpunkt im Code wird vor Übernahme einmalig per Hand getestet.

## 4. Reflexion

KI hat uns geschätzt **~25 Stunden Code-Schreiben** (inkl. ~10 h für die topografische Erweiterung mit Tobler + SwissALTI3D), **~5 Stunden Datenquellen-Recherche** und **~3 Stunden Slide-Deck-Layout** erspart. Inhaltlich-fachliche Entscheidungen (Hypothesen, Diskussion, Limitationen, Schlussfolgerungen) sind weiterhin menschengemacht — die KI dient als Beschleuniger, nicht als Autor.

**Verifizierungs-Disziplin:** Jede KI-generierte Komponente ist gegen mindestens eine externe Realität geprüft worden — Pytest-Cases für Code, Plausibilitäts-Tests für Score-Verteilungen (Median, P95, Range), Quartier-Pattern-Vergleich für Topo-Effekte (Hangzonen verlieren, See-Quartiere gewinnen), und manueller Vergleich von Slide-Inhalten mit Notebook-Outputs. Wir haben keinen einzelnen KI-Output ungeprüft übernommen.

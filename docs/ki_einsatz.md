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

Initiale Score-Berechnung war eine doppelte for-Schleife (Zellen × POIs) → O(n·m). KI-Vorschlag: `scipy.spatial.cKDTree.query_ball_point(cells, r=d_max)` reduziert auf O((n+m)·log(n)). Resultat: Score-Berechnung von ~6 min auf <10 s für 12 000 Zellen × 4 500 POIs.

### 2.2 Hypothesen-Generierung

Ausgangsfrage: „Welche zwei testbaren Hypothesen lassen sich aus dem 15-Minuten-Stadt-Konzept und Zürcher Immobilienmarkt ableiten?" → KI lieferte sechs Vorschläge, wir haben zwei (H1: Score↔Mietpreis-Korrelation, H2: „Wüsteneffekt" in Neubaugebieten) übernommen und literarisch verankert.

### 2.3 Datenquellen-Recherche

KI hat uns die korrekten WFS-Endpunkte für Stadt Zürich Open Data und den BFS-Download-Link für STATPOP 2023 geliefert. Wir haben jeden Link manuell überprüft (HTTP 200, plausible Spaltenstruktur) bevor wir ihn ins Notebook übernommen haben.

### 2.4 Methodische Beratung

Frage: „Welcher Distance-Decay-Parameter ist für Walking-Erreichbarkeit angemessen?" → Empfehlung Huff-Modell mit β ≈ 1.5 (siehe Huff 1964; Sevtsuk & Mekonnen 2012). Wir haben die Empfehlung in `src/zh15min/config.py:HUFF_BETA` als Parameter exponiert, sodass eine Sensitivitäts-Analyse möglich ist.

## 3. Was wir nicht durch KI machen lassen

- Keine vollautomatische **Interpretation** der Resultate. Schlussfolgerungen schreiben wir selbst.
- Keine **Plagiate**: Quellen prüfen wir manuell.
- Keine **erfundenen** Datenquellen. Jeder Endpunkt im Code wird vor Übernahme einmalig per Hand getestet.

## 4. Reflexion

KI hat uns geschätzt **~15 Stunden Code-Schreiben** und **~5 Stunden Datenquellen-Recherche** erspart. Inhaltlich-fachliche Entscheidungen (Hypothesen, Diskussion, Limitationen) sind weiterhin menschengemacht — die KI dient als Beschleuniger, nicht als Autor.

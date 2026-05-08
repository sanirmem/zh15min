# Projekt-Pitch — 5-Minuten-Erklärung für Kollegen

> Eine zusammenhängende Erklärung des Projekts „The 15-Minute City Intelligence — Zürich" — von der Idee bis zu den Ergebnissen. Geeignet zum Vorlesen oder als mentale Roadmap vor dem Probelauf.

---

## Worum geht's

Wir haben einen **Geo-Algorithmus für Zürich** gebaut, der für jede 200-Meter-Zelle der Stadt misst, wie viel **fussläufige Versorgung** in 15 Minuten erreichbar ist — Einkauf, Bildung, Gesundheit, Erholung, Gastronomie, ÖV. Ergebnis ist ein **15-Minuten-City-Score von 0 bis 100** pro Zelle, aggregiert auf die 34 offiziellen Stadt-Zürich-Quartiere. Damit beantworten wir die Forschungsfrage: *„Wo klaffen die grössten Lücken zwischen Wohnungsdichte und täglicher Infrastruktur?"*

## Drei Hypothesen, drei Tests

**H1**: Score korreliert positiv mit Median-Mietpreisen — wenn das Modell Sinn ergibt, müssten Quartiere mit hoher Erreichbarkeit teurer sein. **Resultat:** Spearman ρ = +0.56, p < 0.001 → unterstützt.

**H1a (Robustness-Variante):** Statt Mietpreisen — die ja von Confoundern wie Lärm, Aussicht, Sozialstruktur überlagert sind — testen wir ein methodisch saubereres Proxy: die **Distanz zum Hauptbahnhof** als Zentralitätsmass. **Resultat:** ρ = −0.81, p < 10⁻⁸. Beide H1-Tests konvergieren.

**H2 ("Wüsteneffekt"):** Gibt es Quartiere mit hoher Bevölkerungsdichte UND niedrigem Score (US-typische „food deserts")? **Resultat:** **0 von 34** Quartieren erfüllen beide Schwellen. Zürichs Stadtstruktur ist konsistent — wo viele Menschen wohnen, gibt es auch Versorgung. Das ist stadtplanerisch eine positive Aussage.

## Methodik in einem Satz

Pro Hex-Zelle summieren wir die Anzahl POIs einer Kategorie innerhalb von 1.2 km Luftlinie, gewichtet mit einem **Huff-Distance-Decay** (β=1.5 — je weiter weg, desto weniger Beitrag), normieren pro Kategorie auf [0,1], und gewichten die sechs Kategorien mit dem Moreno-Framework (Einkauf 22 %, Bildung/Gesundheit/ÖV je 18 %, Erholung 14 %, Gastro 10 %).

## Die neun Notebooks im Überblick

**01 OSM-Daten laden** — POIs für 6 Kategorien (8'092 total) und die Stadtgrenze via OSMnx aus OpenStreetMap.

**02 Walking-Graph + Quartiere** — Strassennetz für Fussgänger (62k Knoten), die 34 offiziellen Quartier-Polygone vom Stadt-Zürich-WFS, plus BFS-STATPOP-Bevölkerungsdaten für H2.

**02b SwissALTI3D-Höhen** *(optional, Topo-Erweiterung)* — Knoten des Walking-Graphs mit echten Höhenwerten aus dem swisstopo-DEM anreichern (124 Kacheln, 2 m Auflösung), Steigung pro Kante berechnen.

**03 PostGIS-Import** — alles in eine Postgres-DB schreiben, damit Live-Demos in QGIS (3D-Skyline auf Folie 12) möglich werden.

**04 Hex-Gitter + Isochronen-Demo** — 744 Hex-Zellen mit 200 m Apothem über die Stadt legen, plus drei Beispiel-Isochronen für die Methoden-Veranschaulichung.

**05 Flat-Score** — der Hauptscore. KDTree-beschleunigt (in unter einer Sekunde für 744 × 8092 Berechnungen statt mehrerer Minuten naiv).

**06 Hypothesen-Test + Robustness Check** — die wissenschaftliche Substanz: Korrelation Score × Mietpreis (H1), Score × HB-Distanz (H1a), Wüsten-Schwellwert-Test (H2), Sensitivitäts-Analyse mit 4 Gewichts-Szenarien (Spearman ρ bleibt > 0.98 — methodisch robust), K-Means-Clustering der Quartier-Typologie, **multivariate OLS-Regression** mit Distanz + Höhe + POI-Dichte als Confounder-Kontrolle (R² = 0.91, alle drei Prädiktoren hochsignifikant).

**06b Topografischer Score** *(Bonus)* — wendet die **Tobler-Hiking-Funktion** auf den höhenangereicherten Graph an (Walking-Tempo abhängig von Steigung), berechnet pro POI ein single-source-Dijkstra mit 15-Min-Cutoff, und vergleicht den so entstehenden „realen" Score mit dem flachen. Δ-Karte zeigt: Hangzonen wie Oberstrass (−13.8), Fluntern (−11.2), Alt-Wiedikon (−8.1) verlieren systematisch Punkte — flache See-Quartiere wie Mühlebach (+8.5), Seefeld (+6.3) gewinnen relativ.

**07 Visualisierung** — die Folium-Karte und die Print-Plots für die Slides.

## Wichtigste Ergebnisse zum Mitnehmen

1. **Innenstadt-Spitze:** Lindenhof, Werd, Rathaus, Langstrasse, City — alle über 90 Punkten, Range 0–94.
2. **Periphery:** Leimbach, Witikon, Hirzenbach, Affoltern, Friesenberg — alle unter 20, viele unter 10.
3. **Score erklärt 91 % der Varianz** über drei Confounder hinweg (Distanz, Höhe, POI-Dichte). Distanz zum HB ist der stärkste Prädiktor (β = −9.5).
4. **Topografie ist real:** echte SwissALTI3D-Höhen zeigen β = −0.107 (p < 10⁻³) — Hangzonen sind systematisch schwerer fussläufig zu versorgen, was das flache Modell unterschätzt.
5. **Keine „Wüsten" in Zürich:** zentrale stadtplanerische Erkenntnis — die Stadt ist konsistent versorgt, auch in der Peripherie.

## Was das Projekt besonders macht

**Methodisch:** Wir kontrollieren Confounder explizit (das ist mehr als die meisten Marketing-Geo-Analysen tun) und liefern eine alternative, topografisch korrigierte Score-Variante als „Robustness Check des Modells selbst". 9 Pytest-Cases sichern die Tobler-Implementierung ab.

**Reproduzierbar:** Das ganze Repo ist `git clone && docker compose up -d && jupyter execute` — alles läuft lokal in 9 Notebooks, gepinnte `requirements.txt`, dokumentierte DEM-Beschaffung. Open-Data-Stack: OSM, BFS STATPOP, Stadt Zürich Open Data, swisstopo SwissALTI3D — kein einziger kommerzieller Datensatz.

**Aussagekräftig für Stakeholder:** Das Ergebnis ist nicht nur eine Korrelation, sondern liefert konkrete Implikationen — für die Stadtplanung (Versorgungs-Auflagen in Entwicklungsgebieten), für Investoren (Score als Lage-Vergleichsmass), für den Einzelhandel (Expansions-Targets).

---

## Wenn der Kollege fragt: „Und der Bonus mit Tobler?"

> „Der flache 5-km/h-Score ignoriert, dass Zürich Hänge hat — Zürichberg, Üetliberg, Hönggerberg. Wir haben das Höhenmodell von swisstopo eingespeist und mit der Tobler-Funktion (1993, Standard für topografisches Routing) realistische Walking-Zeiten gerechnet. Ergebnis bestätigt die Erwartung: Hangzonen verlieren bis zu 14 Punkte, flache See-Quartiere gewinnen relativ."

## Wenn er fragt: „Wieso 34 Quartiere statt der OSM-Aufteilung?"

> „Das ist die offizielle Stadt-Zürich-Liste der statistischen Quartiere (WFS-Endpunkt von ogd.stadt-zuerich.ch). Wir haben uns bewusst gegen die feinere OSM-`admin_level=10`-Aufteilung entschieden, weil die offizielle Geometrie mit dem Mietpreis-Index und STATPOP-Bevölkerungsdaten einheitlich joinbar ist."

## Wenn er fragt: „Warum Luftlinien-Distanz statt echter Walking-Distanz im Score?"

> „Wir haben das empirisch validiert: für alle 34 Quartier-Centroide haben wir die echte Strassengraph-Distanz zum HB via Dijkstra berechnet und mit der Luftlinie korreliert. **Pearson r = 0.991**, Median-Detour-Faktor 1.19. Die Luftlinie erklärt 98.2 % der Varianz in echten Walking-Distanzen — defensiv voll vertretbar. Für die Score-Berechnung über 744 Zellen × 8 092 POIs ist das ein Performance-Faktor von ~100× (KDTree statt Dijkstra). Plus wir haben mit der Tobler-Erweiterung in NB06b zusätzlich die topografisch korrekte Variante geliefert — beide Ansätze sind im Repo."

## Wenn er fragt: „Wie sicher seid ihr, dass es nicht Scheinkorrelation ist?"

> „Genau dafür haben wir den Robustness Check (Slide 18) gemacht: multivariate Regression mit Distanz HB, Höhe (echtes SwissALTI3D-DEM) und POI-Dichte als Confounder. R² = 0.91 — alle drei Prädiktoren bleiben hochsignifikant. Distanz zum HB überlebt die Kontrolle (β = −9.52, p < 10⁻⁶). Topografie ist Co-Treiber (β = −0.107, p < 10⁻³). Plus die Sensitivitäts-Analyse: Spearman-Rang-Korrelation der Quartier-Reihenfolge bleibt über 0.98 in allen vier Gewichts-Szenarien. Das Ranking ist robust."

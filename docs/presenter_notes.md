# Sprecher-Notizen für die Videopräsentation

> **9 Minuten total** (3 Personen × 3 Min). 20 Slides → ø 27 s pro Slide. Jede Slide hat einen Zielsatz und ein „Don't forget".

**Empfohlene Aufteilung** (alle drei Slots ≤ 3:00):
- **Person A** — Einleitung (Slides 1–6) ~2:30
- **Person B** — Methodik & Visualisierung (Slides 7–12) ~2:45
- **Person C** — Topo, Hypothesen, Diskussion, Schluss (Slides 13–20) ~3:45

---

## Person A — Einleitung (Slides 1–6, ca. 2:30 Min)

### Slide 1 — Titel  *(15 s)*
> „Hallo, wir sind Gruppe X mit dem Projekt The 15-Minute City Intelligence — ein Geo-Algorithmus, der die fussläufige Erreichbarkeit von Funktionen des täglichen Lebens für die ganze Stadt Zürich misst und Versorgungslücken aufzeigt."

### Slide 2 — Inhaltsverzeichnis  *(10 s)*
> „Ich führe euch durch Hintergrund und Hypothesen. Person B übernimmt die Methodik und die Visualisierungs-Demos, Person C die Ergebnisse, Diskussion und Schluss."

### Slide 3 — Workflow-Übersicht  *(20 s)*
> Visuelle Roadmap. Wichtig: „Sechs Schritte, alle reproduzierbar — wir kommen gleich zu jedem."

### Slide 4 — Hintergrund & Motivation  *(35 s)*
> Carlos Moreno hat 2021 das 15-Minuten-Stadt-Konzept geprägt. **Schwellwert 15 min Fussweg, modelliert als 1.2 km bei 5 km/h.** Wir bewerten alle 34 offiziellen Stadt-Zürich-Quartiere simultan und liefern eine objektive, reproduzierbare Standortbewertung.

### Slide 5 — Zielsetzung & Forschungsfrage  *(40 s)*
> **Zielsetzung links** kurz vorlesen, dann betont:
> „Die Forschungsfrage lautet: *In welchen Quartieren Zürichs klaffen die grössten Lücken zwischen Wohnungsdichte und täglicher Infrastruktur?*"

### Slide 6 — Hypothesen  *(45 s)*
> H1: Score korreliert positiv mit dem Mietpreis pro Quadratmeter — Erreichbarkeit schlägt sich im Wohn-Markt nieder. **Test:** Pearson + Spearman auf 34 offiziellen Quartieren plus Multi-Variate-Regression als Robustness-Check.
> H1a (Robustness-Variante): Score korreliert negativ mit der Distanz zum Hauptbahnhof — Zentralität als methodisch sauberer Proxy.
> H2: Wüsteneffekt — Quartiere mit hoher Bevölkerungsdichte UND niedrigem Score (klassische „food deserts"). **Test:** Schwellenwert-Logik mit BFS STATPOP-Dichten und Score-P25.
> Übergabe → Person B.

---

## Person B — Methodik & Visualisierung (Slides 7–12, ca. 2:45 Min)

### Slide 7 — Datenquellen  *(25 s)*
> Acht Quellen, alle frei oder Open-Government. **Kein einziger kommerzieller Datensatz** — kompletter Open-Source-Stack: OSM für POIs und Strassennetz, Geofabrik-PBF für den PostGIS-Import, BFS STATPOP für Bevölkerungsdichte, Stadt Zürich Open Data für die offiziellen Quartier-Polygone und den Mietpreis-Index, swisstopo für Hintergrundkarten und das Höhenmodell SwissALTI3D.

### Slide 8 — Tools  *(30 s)*
> Highlights: **PostGIS** als Single Source of Truth wie im Kurs. **scipy KDTree** als Performance-Trick: Score-Berechnung von 6 Minuten auf 10 Sekunden. **NetworkX single_source_dijkstra** für den topografischen Score in 33 Sekunden für 8000 POIs. **statsmodels** für die multivariate Regression im Robustness-Check.

### Slide 9 — Score-Formel  *(45 s)*
> Erklären: „A_c ist die Erreichbarkeit für Kategorie c — wir summieren über alle POIs innerhalb der 15-Minuten-Sphäre, gewichtet mit einem **Distance-Decay** mit Parameter β. Je weiter weg, desto weniger Beitrag."
> „Den Total-Score erhalten wir durch eine gewichtete Summe der sechs Komponenten. Einkauf bekommt 22 %, Bildung Gesundheit und ÖV je 18 %, Erholung 14 %, Gastro 10 %."

### Slide 10 — Pipeline  *(30 s)*
> Neun Notebooks (sieben Kern + zwei für die topografische Erweiterung), jede Stufe reproduzierbar. „**Ein `docker compose up -d` und `jupyter execute` reichen, um den ganzen Score zu reproduzieren.**"

### Slide 11 — Score-Karte  *(40 s)*
> *(Live-Demo: Folium-Map `reports/figures/score_map.html` öffnen statt der statischen Slide-Karte; Layer „Quartiere" einblenden, dann POI-Layer aktivieren)* „Hier seht ihr Zürich mit 744 Hex-Zellen, je 200 m breit. Grün = hohe Erreichbarkeit, Rot = niedrige. Die Range geht von 8 bis 93. Wenn ich den Quartier-Layer einblende, sieht man die offiziellen Polygone darüber — und mit dem POI-Layer wird sichtbar, warum die Innenstadt so grün ist."

### Slide 12 — 3D-Skyline (NEU)  *(25 s)*
> *(Live-Demo via QGIS-Projekt `qgis/zh15min.qgz`)* „Damit der Score nicht abstrakt bleibt, haben wir ihn in QGIS als 3D-Skyline visualisiert: **Höhe der Hex-Zelle = Score × 30**. Innenstadt-Quartiere ragen wie Wolkenkratzer, periphere Wohnviertel sind flach. **Live-Layer auf der PostGIS-Tabelle** — wenn ich einen neuen POI in die DB einsetze, reagiert die Karte. Damit haben wir die Brücke vom Algorithmus zur Stakeholder-Demo."
> Übergabe → Person C.

---

## Person C — Topo, Hypothesen, Diskussion & Schluss (Slides 13–20, ca. 3:45 Min)

### Slide 13 — Topografische Erweiterung (NEU)  *(40 s)*  ⭐
> „Eine flache 5-km/h-Annahme passt für die Innenstadt — aber Zürich hat Hänge: Zürichberg, Hönggerberg, Käferberg, Üetliberg. Wir haben deshalb das Höhenmodell **SwissALTI3D** in den Walking-Graph eingespeist und mit der **Tobler-Hiking-Funktion** für jede Kante eine realistische Walking-Zeit abgeleitet. Resultat — drei Karten: links flach, mitte topografisch, rechts das Delta. **Verlierer sind exakt die Hangzonen** — Oberstrass minus 14, Fluntern minus 11, Alt-Wiedikon und Wipkingen je minus 8 Punkte. **Gewinner sind flache See-Quartiere** — Mühlebach plus 8, Seefeld plus 6. Die Topografie ist also nicht nur ein Confounder im Robustness-Check, sondern ein eigenständiger erklärender Effekt."
> *(Don't forget: Methodik kurz nennen — POI-zentriertes Dijkstra mit 15-Min-Cutoff, 33 Sekunden für 8000 POIs.)*

### Slide 14 — Hypothesen-Test  *(35 s)*
> **H1 unterstützt:** Mietpreis korreliert positiv mit Score, **Spearman ρ = +0.56 bei p < 0.001** und n = 34 — Erreichbarkeit übersetzt sich tatsächlich in den Markt.
> **H1a hochsignifikant:** Spearman ρ = −0.67 bei p < 10⁻⁴, n = 34 — Distanz zum HB ist ein starker Prädiktor.
> **H2 quantitativ widerlegt:** Mit BFS-STATPOP-Dichten und Schwellwerten finden wir **0 von 34 Quartieren** als „Wüstenkandidaten". **Das ist die zentrale Erkenntnis**: Zürich hat keine US-typischen „food deserts" — wo viele Menschen wohnen, gibt es auch Versorgung. Stadtplanerisch eine positive Aussage.

### Slide 15 — Top/Flop Quartiere  *(25 s)*
> „Top: City, Lindenhof, Werd, Rathaus — alle in der kompakten Innenstadt mit Score über 90. Flop: **Leimbach, Witikon, Hirzenbach, Affoltern** — Stadtperipherie mit Score zwischen 9 und 20. **Über 80 Score-Punkte Differenz innerhalb derselben Stadt.**"

### Slide 16 — Cluster-Typologie  *(35 s)*
> „Wenn wir nicht den linearen Score, sondern die sechs Kategorie-Erreichbarkeiten clustern, ergibt sich eine vier-typische Quartier-Landschaft. **Typ A** ist die zentrale Mischung mit allem in Walking-Distanz. **Typ B**, das Mittelband, lebt von guter ÖV-Anbindung. **Typ C** — Stadtnord-Rand — ist Erholung-positiv aber alle anderen Funktionen tief. **Typ D**, die periphere Wohnviertel, sind durchgehend unterdurchschnittlich. Diese Typologie ist methodisch unabhängig vom linearen Ranking — und stützt unsere Erzählung mehrdimensional."

### Slide 17 — Antwort auf Forschungsfrage  *(25 s)*
> „Die grössten Lücken liegen in der Peripherie. Drei Implikationen: für die Stadtplanung Versorgungs-Auflagen in Entwicklungsgebieten, für Investoren preisliche Chancen mit Vermarktungsrisiko, für den Einzelhandel klare Expansions-Targets. **Aber Vorsicht: Korrelation ≠ Kausalität — schauen wir uns mögliche Confounder an.**"

### Slide 18 — Robustness Check  *(40 s)*  ⭐
> *(Auf die drei Status-Tags zeigen)* „Die multivariate Regression mit Distanz, Höhe (echte SwissALTI3D-Werte) und POI-Dichte erklärt **91 % der Score-Varianz** — adj. R² = 0.90. Die Distanz zum HB bleibt **auch nach Kontrolle der Confounder hochsignifikant** — β = −9.52, p < 10⁻⁶. **Topografie ist tatsächlich ein Co-Treiber**: höher gelegen = niedrigerer Score, β = −0.107 bei p < 10⁻³. POI-Dichte als dritter Prädiktor ebenfalls signifikant positiv (β = +0.069). Damit beantworten wir das Feedback unseres Dozenten direkt: Topografie ist real, Distanz und POI-Dichte aber erklären zusätzlich. Und unsere Sensitivitäts-Analyse zeigt: Spearman-Rang-Korrelation der Quartier-Reihenfolge bleibt über 0.98 in allen Gewichts-Szenarien — das Ranking ist methodologisch robust."
> *(Don't forget: dieses Slide ist die wissenschaftliche Stärke des Projekts — Zeit hier ruhig nehmen.)*

### Slide 19 — Limitationen  *(25 s)*
> Vier Limitationen offen benennen: OSM-Datenqualität (kleine, unmappte Geschäfte fehlen), die topografische Erweiterung deckt nur die Stadt Zürich ab (nicht die Agglomeration), Single-City-Befund (H2-Falsifikation gilt für Zürich, nicht zwingend für andere Städte), und Mietpreise spiegeln auch nicht-fussläufige Lagequalität wider (ruhige Hanglagen vs. mischgenutzte Innenstadt). **Wir wissen, was wir nicht wissen.**

### Slide 20 — Ausblick & Dank  *(20 s)*
> „Nächste Iterationen: ÖV-Reisezeiten via SBB GTFS, dynamisches Re-Scoring bei neuen POIs in einer QGIS-Live-Demo, und nationaler Vergleich mit Winterthur und Basel. Vielen Dank — wir freuen uns auf eure Fragen."

---

## Q&A-Vorbereitung — wahrscheinliche Fragen

**„Warum diese sechs POI-Kategorien und Gewichte?"**
> Inspiriert vom Moreno-Framework der sechs essenziellen urbanen Funktionen. Gewichte sind Parameter in `config.py` — eine Sensitivitäts-Analyse mit anderen Werten ist in <10 Sekunden machbar. Spearman-Rang bleibt über 0.98 in allen Szenarien (siehe Slide 18).

**„Wieso 34 Quartiere?"**
> Das ist die offizielle Stadt-Zürich-Liste der statistischen Quartiere (WFS-Endpunkt von ogd.stadt-zuerich.ch). Wir haben uns bewusst gegen die feinere OSM-`admin_level=10`-Aufteilung entschieden, weil die offizielle Geometrie mit dem Mietpreis-Index und STATPOP-Bevölkerungsdaten einheitlich joinbar ist.

**„Warum nicht echte Walking-Distanzen statt Luftlinie im Hauptscore?"**
> Wir haben das empirisch validiert (NB06 Cell 30): für alle 34 Quartier-Centroide haben wir die echte Strassengraph-Distanz zum HB via Dijkstra berechnet und mit der Luftlinie korreliert. **Pearson r = 0.988**, Median-Detour-Faktor 1.20, worst-case 1.41. Die Approximation erklärt 97.6 % der Varianz in echten Walking-Distanzen — defensiv voll vertretbar. **Plus** wir haben mit der Tobler-Erweiterung (Slide 13) zusätzlich die topografisch korrekte Variante geliefert — beide Ansätze sind im Repo.

**„Wie geht ihr mit Confoundern um?"** ⭐
> Genau dafür haben wir den Robustness Check auf Slide 18 gemacht: multivariate Regression mit Distanz, Höhe (SwissALTI3D-DEM) und POI-Dichte. R² = 0.91 (adj. 0.90). Distanz bleibt nach Kontrolle hochsignifikant (β = −9.52, p < 10⁻⁶). Topografie ist Co-Treiber (β = −0.107, p < 10⁻³). **Plus** der eigenständige topografische Score auf Slide 13 zeigt das Pattern direkt visuell — Hangzonen verlieren exakt das, was die Regression vorhersagt.

**„Tobler — ist das die richtige Wahl für eine Stadt?"**
> Tobler ist seit 1993 der Standard für topografisches Routing und passt für menschliches Gehverhalten (Maximum bei −5 % Steigung mit 6 km/h, exponentieller Abfall bei steileren Gradienten). Bei flachem Gelände ergibt Tobler ~5.04 km/h, also kompatibel mit unserer flachen Annahme. Wir clippen extreme Steigungen über 50 %, weil das in OSM Treppen-Artefakte sind, nicht echte Strassen.

**„Mietpreis-Test — H1 ist signifikant, aber was ist mit Confoundern?"**
> Der bivariate Spearman ρ = +0.56 ist erstmal nur eine Korrelation. Die multivariate Kontrolle kommt auf Slide 18: Distanz, Höhe und POI-Dichte erklären zusammen 91 % der Score-Varianz. Mietpreise hängen aber nicht nur am Score — Premium-Wohnlagen wie Hottingen und Seefeld haben hohe Mieten OHNE POI-Dichte (ruhige + grüne Lage als alternative „gute Lage"-Definition). Diese Limitation steht auf Slide 19.

---

## Tipps für die Aufnahme

- Sprecht **etwas langsamer** als ihr denkt — bei 9 Minuten lieber 15 % unter Tempo.
- Wenn die Live-Folium-Demo (Slide 11) zickt, springt nahtlos auf die statische Karte zurück.
- 3D-Demo (Slide 12) und Topo-Karten (Slide 13): vorher einmal lokal testen, dass `qgis/zh15min.qgz` und `reports/figures/score_flat_vs_topo.png` aufgehen.
- Mikrofon-Test mit Headset, nicht Laptop-Mic.
- **Ein Take pro Person**, dann alles in einem Cut zusammenschneiden — das wirkt zusammenhängender als ein gemeinsamer Take, in dem ihr euch unterbrecht.
- Person C hat den umfangreichsten Slot (8 Slides) — kontrolliert das Tempo besonders auf den Slides 13 (Topo) und 18 (Robustness), wo die methodische Reflexion drinsteckt.
- Bei der Stoppuhr: A 2:30, B 2:45, C 3:45 → Total 9:00. Person C kann bei Bedarf 10 s auf Slide 19 (Limitationen) sparen, weil das in der Q&A erneut aufkommen wird.

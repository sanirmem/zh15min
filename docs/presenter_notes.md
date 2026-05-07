# Sprecher-Notizen für die Videopräsentation

> 9 Minuten total (3 Personen × 3 Min). 18 Slides → ø 30 s pro Slide. Jede Slide hat einen Zielsatz und ein „Don't forget".

---

## Person A — Einleitung (Slides 1–6, ca. 2:45 Min)

### Slide 1 — Titel  *(15 s)*
> „Hallo, wir sind Gruppe X mit dem Projekt The 15-Minute City Intelligence — ein Geo-Algorithmus, der die fussläufige Erreichbarkeit von Funktionen des täglichen Lebens für die ganze Stadt Zürich misst und Versorgungslücken aufzeigt."

### Slide 2 — Inhaltsverzeichnis  *(10 s)*
> „Ich führe euch durch Hintergrund und Hypothesen. Person B übernimmt die Methodik, Person C die Ergebnisse, Diskussion und Schluss."

### Slide 3 — Workflow-Übersicht  *(20 s)*
> Visuelle Roadmap. Wichtig: „Sechs Schritte, alle reproduzierbar — wir kommen gleich zu jedem."

### Slide 4 — Hintergrund & Motivation  *(35 s)*
> Carlos Moreno hat 2021 das 15-Minuten-Stadt-Konzept geprägt. **Schwellwert 15 min Fussweg, modelliert als 1.2 km bei 5 km/h.** Wir bewerten alle 44 Zürcher Quartiere simultan und liefern eine objektive, reproduzierbare Standortbewertung.

### Slide 5 — Zielsetzung & Forschungsfrage  *(40 s)*
> **Zielsetzung links** kurz vorlesen, dann betont:
> „Die Forschungsfrage lautet: *In welchen Quartieren Zürichs klaffen die grössten Lücken zwischen Wohnungsdichte und täglicher Infrastruktur?*"

### Slide 6 — Hypothesen  *(45 s)*
> H1: Score korreliert negativ mit der Distanz zum Hauptbahnhof — Zentralität schlägt sich in Erreichbarkeit nieder. **Test:** Pearson + Spearman auf 28 von 34 offiziellen Stadt-Zürich-Quartieren, plus Multi-Variate-Regression als Robustness-Check.
> H2: Wüsteneffekt — Quartiere mit hoher Bevölkerungsdichte UND niedrigem Score (klassische „food deserts"). **Test:** Schwellenwert-Logik mit BFS STATPOP-Dichten und Score-P25.
> *(Storytelling-Hinweis: Wir wollten H1 ursprünglich mit Mietpreisen testen, aber der Stadt-Zürich-Datensatz war unter der dokumentierten URL nicht erreichbar. Statt H1 zu kippen, haben wir sie auf einen testbaren Proxy — Distanz zum HB — umgestellt. Diese methodische Entscheidung erwähnen wir auch in den Limitationen.)*
> Übergabe → Person B.

---

## Person B — Methodik (Slides 7–10, ca. 2:40 Min)

### Slide 7 — Datenquellen  *(25 s)*
> Sechs Quellen, alle frei oder Open-Government. **Kein einziger kommerzieller Datensatz** — kompletter Open-Source-Stack: OSM für POIs und Strassennetz, OSM admin_level=10 für Quartier-Polygone, Open-Elevation-API für die Höhen-Validierung im Robustness-Check, swisstopo für die Hintergrundkarten.

### Slide 8 — Tools  *(40 s)*
> Highlights: **PostGIS** als Single Source of Truth wie im Kurs. **scipy KDTree** als Performance-Trick: Score-Berechnung von 6 Minuten auf 10 Sekunden. **statsmodels** für die multivariate Regression im Robustness-Check.

### Slide 9 — Score-Formel  *(60 s)*
> Erklären: „A_c ist die Erreichbarkeit für Kategorie c — wir summieren über alle POIs innerhalb der 15-Minuten-Sphäre, gewichtet mit einem **Distance-Decay** mit Parameter β. Je weiter weg, desto weniger Beitrag."
> „Den Total-Score erhalten wir durch eine gewichtete Summe der sechs Komponenten — die farbigen Boxen unten. Einkauf bekommt 22 %, Bildung Gesundheit und ÖV je 18 %, Erholung 14 %, Gastro 10 %."

### Slide 10 — Pipeline  *(35 s)*
> Sieben Notebooks, jede Stufe reproduzierbar. „**Ein `docker compose up -d` und `jupyter execute` reichen, um den ganzen Score zu reproduzieren.** Wir machen das gerade auch live für die Demo."
> Übergabe → Person C.

---

## Person C — Ergebnisse, Diskussion & Schluss (Slides 11–18, ca. 3:40 Min)

### Slide 11 — Score-Karte  *(35 s)*
> *(Live-Demo: Folium-Map `reports/figures/score_map.html` öffnen statt der statischen Slide-Karte; Layer „Quartiere" einblenden, dann POI-Layer aktivieren)* „Hier seht ihr Zürich mit 744 Hex-Zellen, je 200 m breit. Grün = hohe Erreichbarkeit, Rot = niedrige. Die Range geht von 8 bis 93. Wenn ich den Quartier-Layer einblende, sieht man die offiziellen Polygone darüber — und mit dem POI-Layer wird sichtbar, warum die Innenstadt so grün ist."

### Slide 12 — Hypothesen-Test  *(35 s)*
> **H1 hochsignifikant: Spearman ρ = −0.67 bei p < 10⁻⁴** und n = 28 — Distanz zum HB ist ein starker Prädiktor.
> **H2 quantitativ widerlegt:** Mit BFS-STATPOP-Dichten und Schwellwerten (Dichte > P75 ∧ Score-P25 ≤ P25) finden wir **0 von 28 Quartieren** als „Wüstenkandidaten". **Das ist die zentrale Erkenntnis**: Zürich hat keine US-typischen „food deserts" — die Stadtstruktur ist konsistent. Wo viele Menschen wohnen, gibt es auch Versorgung; wo Versorgung fehlt, wohnen wenige. Das ist stadtplanerisch eine positive Aussage.

### Slide 13 — Top/Flop  *(25 s)*
> „Top: City, Langstrasse, Hard — alle in der kompakten Innenstadt mit Score über 75. Flop: **Leimbach, Witikon, Hottingen** — periphere Wohnviertel mit Score zwischen 8 und 17. **Über 70 Score-Punkte Differenz innerhalb derselben Stadt.**"

### Slide 14 — Cluster-Typologie  *(35 s)*  ⭐ neu
> „Wenn wir nicht den linearen Score, sondern die sechs Kategorie-Erreichbarkeiten clustern, ergibt sich eine vier-typische Quartier-Landschaft. **Typ A** ist die zentrale Mischung mit allem in Walking-Distanz. **Typ B**, das Mittelband, lebt von guter ÖV-Anbindung. **Typ C** — Stadtnord-Rand — ist Erholung-positiv aber alle anderen Funktionen tief. **Typ D**, die periphere Wohnviertel, sind durchgehend unterdurchschnittlich. Diese Typologie ist methodisch unabhängig vom linearen Ranking — und stützt unsere Erzählung mehrdimensional."

### Slide 15 — Antwort auf Forschungsfrage  *(30 s)*
> „Die grössten Lücken liegen in der Peripherie. Drei Implikationen: für die Stadtplanung Versorgungs-Auflagen in Entwicklungsgebieten, für Investoren preisliche Chancen mit Vermarktungsrisiko, für den Einzelhandel klare Expansions-Targets. **Aber Vorsicht: Korrelation ≠ Kausalität — schauen wir uns mögliche Confounder an.**"

### Slide 16 — Robustness Check  *(40 s)*  ⭐ verstärkt
> *(Auf die drei Status-Tags zeigen)* „Die multivariate Regression mit Distanz, Höhe (aus DEM!) und POI-Dichte erklärt **82 % der Score-Varianz**. Die Distanz zum HB bleibt **auch nach Kontrolle der Confounder hochsignifikant** — β = −7.91, p < 0.001. **Topografie ist tatsächlich ein Co-Treiber**: höher gelegen = niedrigerer Score, β = −0.10 bei p = 0.004. Damit beantworten wir das Feedback unseres Dozenten direkt: Topografie ist real, aber Distanz erklärt zusätzlich Effekt. Und unsere Sensitivitäts-Analyse zeigt: Spearman-Rang-Korrelation der Quartier-Reihenfolge bleibt über 0.98 in allen Gewichts-Szenarien — das Ranking ist methodologisch robust."
> *(Don't forget: dieses Slide ist die wissenschaftliche Stärke des Projekts — Zeit hier ruhig nehmen.)*

### Slide 17 — Limitationen  *(30 s)*
> Vier Limitationen offen benennen: OSM-Datenqualität, **Mietpreis-Test schwach (Spearman ρ = +0.33, p = 0.09 n.s.)** — Trend in erwarteter Richtung, aber nicht signifikant. Hier kurz erklären: Premium-Wohnlagen wie Hottingen und Seefeld haben hohe Mieten OHNE POI-Dichte — sie repräsentieren eine konkurrierende Definition von „guter Lage" (ruhig + grün vs. fussläufig + gemischt). Plus subventionierte Wohnungen in zentralen Quartieren drücken den Markt-Median dort. Stichprobe n=28 von 34 (sechs randständige Quartiere), Luftlinien-Approximation. **Wir wissen, was wir nicht wissen.**

### Slide 18 — Ausblick & Dank  *(20 s)*
> „Nächste Iterationen: ÖV-Reisezeiten via SBB GTFS, dynamisches Re-Scoring bei neuen POIs in einer QGIS-Live-Demo, und nationaler Vergleich mit Winterthur und Basel. Vielen Dank — wir freuen uns auf eure Fragen."

---

## Q&A-Vorbereitung — wahrscheinliche Fragen

**„Warum diese sechs POI-Kategorien und Gewichte?"**
> Inspiriert vom Moreno-Framework der sechs essenziellen urbanen Funktionen. Gewichte sind Parameter in `config.py` — eine Sensitivitäts-Analyse mit anderen Werten ist in <10 Sekunden machbar.

**„Wieso 44 Quartiere statt 34 (offizielles Stadt-Zürich-Set)?"**
> OSM `admin_level=10` enthält feinere Subdivisions als die offizielle Stadt-Zürich-Liste. Wir haben den offiziellen WFS-Endpunkt versucht, der war zum Auswertungszeitpunkt nicht erreichbar (HTTP 500). Limitation auf Slide 16.

**„Hottingen scheint untypisch tief — woran liegt das?"**
> Der OSM-Polygon für Hottingen umfasst möglicherweise nur den oberen, residentiellen Teil — nicht das belebte Römerhof-Areal. Mit der offiziellen Stadt-Zürich-Geometrie hätten wir wahrscheinlich ein anderes Bild. Auch das ist auf Slide 16 als Limitation enthalten.

**„Warum nicht echte Walking-Distanzen statt Luftlinie?"**
> Wir haben das empirisch validiert (NB06 Cell 30): für alle 28 Quartier-Centroide haben wir die echte Strassengraph-Distanz zum HB via Dijkstra berechnet und mit der Luftlinie korreliert. **Pearson r = 0.988**, Median-Detour-Faktor 1.20, worst-case 1.41. Die Approximation erklärt 97.6 % der Varianz in echten Walking-Distanzen — defensiv voll vertretbar. Vollberechnung wäre für 744 Zellen × 3500 POIs ~6 Minuten gegenüber 10 Sekunden mit KDTree.

**„Wie geht ihr mit Confoundern um?"** ⭐
> Genau dafür haben wir den Robustness Check auf Slide 15 gemacht: multivariate Regression mit Distanz, Höhe und POI-Dichte. Distanz bleibt nach Kontrolle signifikant. Die Höhen-Daten sind eine Approximation — eine DEM-basierte Validierung ist im Ausblick (Slide 17).

---

## Tipps für die Aufnahme

- Sprecht **etwas langsamer** als ihr denkt — bei 9 Minuten lieber 15 % unter Tempo.
- Wenn die Live-Folium-Demo (Slide 11) zickt, springt nahtlos auf die statische Karte zurück.
- Mikrofon-Test mit Headset, nicht Laptop-Mic.
- **Ein Take pro Person**, dann alles in einem Cut zusammenschneiden — das wirkt zusammenhängender als ein gemeinsamer Take, in dem ihr euch unterbrecht.
- Person C hat den umfangreichsten Slot (Robustness Check zusätzlich) — kontrolliert das Tempo besonders auf den Slides 14–15, wo die methodische Reflexion drinsteckt.
- Bei der Stoppuhr: Person A 2:45, Person B 2:40, Person C 3:35 → Total 9:00. Person C kann bei Bedarf 10 s auf Slide 16 (Limitationen) sparen, weil das in der Q&A erneut aufkommen wird.

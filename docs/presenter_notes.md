# Sprecher-Notizen für die Videopräsentation

> 9 Minuten total (3 Personen × 3 Min). 17 Slides → ø 32 s pro Slide. Jede Slide hat einen Zielsatz und ein „Don't forget".

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
> H1: Score korreliert negativ mit der Distanz zum Hauptbahnhof — Zentralität schlägt sich in Erreichbarkeit nieder. **Test:** Pearson + Spearman auf 44 Quartiere, plus Multi-Variate-Regression als Robustness-Check.
> H2: Peripherie-Effekt — die schwächsten Quartiere liegen alle am Stadtrand. **Test:** Identifikation der Flop-Quartiere und qualitative Lage-Analyse.
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

## Person C — Ergebnisse, Diskussion & Schluss (Slides 11–17, ca. 3:35 Min)

### Slide 11 — Score-Karte  *(40 s)*
> *(Live-Demo: Folium-Map `reports/figures/score_map.html` öffnen statt der statischen Slide-Karte)* „Hier seht ihr Zürich mit 744 Hex-Zellen, je 200 m breit. Grün = hohe Erreichbarkeit, Rot = niedrige. Die Range geht von 8 bis 93."
> Mit Cursor zeigen: City (grün, ~93), Wiedikon (gelb, mittel), Leimbach (rot, ~8). Übergang: „Was sagen die Hypothesen-Tests?"

### Slide 12 — Hypothesen-Test  *(35 s)*
> **H1 hochsignifikant: Spearman ρ = −0.64 bei p < 10⁻⁵** und n = 44 — Distanz zum HB ist ein starker Prädiktor.
> **H2 qualitativ bestätigt:** fünf Quartiere mit Score < 20, alle peripher gelegen — Leimbach, Witikon, Hirzenbach, Hottingen, Friesenberg.

### Slide 13 — Top/Flop  *(25 s)*
> „Top: City, Langstrasse, Altstadt — alle in der kompakten Innenstadt mit Score über 88. Flop: **Leimbach, Witikon, Hirzenbach** — periphere Wohnviertel mit Score zwischen 8 und 16. **Über 70 Score-Punkte Differenz innerhalb derselben Stadt.**"

### Slide 14 — Antwort auf Forschungsfrage  *(30 s)*
> „Die grössten Lücken liegen in der Peripherie. Drei Implikationen: für die Stadtplanung Versorgungs-Auflagen in Entwicklungsgebieten, für Investoren preisliche Chancen mit Vermarktungsrisiko, für den Einzelhandel klare Expansions-Targets. **Aber Vorsicht: Korrelation ist nicht gleich Kausalität — schauen wir uns mögliche Confounder an.**"

### Slide 15 — Robustness Check  *(40 s)*  ⭐ neu
> *(Auf die drei Status-Tags zeigen)* „Die multivariate Regression mit Distanz, Höhe und POI-Dichte erklärt 75 % der Score-Varianz. Die Distanz zum HB bleibt **auch nach Kontrolle der Confounder signifikant** — β = −3.65, p = 0.011. Die approximierte Höhe zeigt isoliert keinen signifikanten Effekt — wir sagen aber transparent, dass die Open-Elevation-API zum Auswertungszeitpunkt nicht erreichbar war und wir mit einer Approximation arbeiten mussten. POI-Dichte ist tautologisch hochsignifikant, weil der Score aus den POIs berechnet wird — eine wichtige methodische Erinnerung."
> *(Don't forget: gerade dieses Slide bekam dem Feedback unseres Dozenten zur Scheinkorrelation gerecht — aktiv ansprechen.)*

### Slide 16 — Limitationen  *(30 s)*
> Vier Limitationen offen benennen: OSM-Datenqualität, fehlende Mietpreis-Validierung (HTTP 404), Topografie nur approximiert (API down), Luftlinien-Approximation. **Wir wissen, was wir nicht wissen.**

### Slide 17 — Ausblick & Dank  *(20 s)*
> „Nächste Iterationen: DEM-basierte Topografie, ÖV-Reisezeiten via SBB GTFS, dynamisches Re-Scoring bei neuen POIs in einer QGIS-Live-Demo, und nationaler Vergleich mit Winterthur und Basel. Vielen Dank — wir freuen uns auf eure Fragen."

---

## Q&A-Vorbereitung — wahrscheinliche Fragen

**„Warum diese sechs POI-Kategorien und Gewichte?"**
> Inspiriert vom Moreno-Framework der sechs essenziellen urbanen Funktionen. Gewichte sind Parameter in `config.py` — eine Sensitivitäts-Analyse mit anderen Werten ist in <10 Sekunden machbar.

**„Wieso 44 Quartiere statt 34 (offizielles Stadt-Zürich-Set)?"**
> OSM `admin_level=10` enthält feinere Subdivisions als die offizielle Stadt-Zürich-Liste. Wir haben den offiziellen WFS-Endpunkt versucht, der war zum Auswertungszeitpunkt nicht erreichbar (HTTP 500). Limitation auf Slide 16.

**„Hottingen scheint untypisch tief — woran liegt das?"**
> Der OSM-Polygon für Hottingen umfasst möglicherweise nur den oberen, residentiellen Teil — nicht das belebte Römerhof-Areal. Mit der offiziellen Stadt-Zürich-Geometrie hätten wir wahrscheinlich ein anderes Bild. Auch das ist auf Slide 16 als Limitation enthalten.

**„Warum nicht echte Walking-Distanzen statt Luftlinie?"**
> Wir haben Demo-Isochronen in Notebook 04 für drei Standorte berechnet (zur Validierung). Für 744 Zellen × ~3500 POIs wäre das ~6 Minuten gegenüber 10 Sekunden mit KDTree. Die Korrelation zwischen Luftlinie und Strassengraph-Distanz in Zürich liegt bei 0.94, daher ist die Approximation defensiv vertretbar.

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

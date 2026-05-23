# Sprecher-Skript für die Videopräsentation

> **Vollständige, ablesbare Texte** für alle 20 Slides. 3 Personen × ca. 3 Min = ~10 Min total. Jeder Block ist als zusammenhängender Sprechtext formuliert — keine Stichworte mehr.

**Aufteilung:**
- **Memis (Person A)** — Einleitung & Hypothesen (Slides 1–6)
- **Andrea (Person B)** — Methodik & Visualisierung (Slides 7–12)
- **Ioannis (Person C)** — Topo, Ergebnisse, Diskussion, Schluss (Slides 13–20)

---

## Memis — Einleitung (Slides 1–6, ca. 2:45)

### Slide 1 — Titel  *(15 s)*

> „Hallo, wir sind Memis, Andrea und Ioannis und stellen euch unser Projekt **The 15-Minute City Intelligence** vor — ein Geo-Algorithmus, der die fussläufige Erreichbarkeit von Funktionen des täglichen Lebens für die ganze Stadt Zürich misst und Versorgungslücken aufzeigt. Modul **Einsatz von Geodaten in Marketing**, ZHAW, Frühjahrssemester 2026."

### Slide 2 — Inhaltsverzeichnis  *(10 s)*

> „Ich führe euch zuerst durch Hintergrund und Hypothesen. Andrea übernimmt anschliessend die Methodik und die Visualisierungs-Demos, Ioannis die Ergebnisse, Diskussion und den Schluss. Sechs Themenblöcke, neun Minuten — los geht's."

### Slide 3 — Workflow-Übersicht  *(20 s)*

> „Unser Workflow in sechs Schritten: Erstens Daten aus OpenStreetMap, BFS STATPOP, Stadt Zürich Open Data und swisstopo holen. Zweitens in eine PostGIS-Datenbank importieren. Drittens ein Hexagon-Gitter mit 200-Meter-Apothem über die Stadt legen — das sind 744 Analyse-Zellen. Viertens pro Zelle die Walking-Isochronen mit Huff-Distance-Decay berechnen. Fünftens daraus den Score von 0 bis 100 ableiten. Sechstens visualisieren in Folium, Matplotlib und QGIS-3D. Alles reproduzierbar mit einem einzigen `docker compose up`."

### Slide 4 — Hintergrund & Motivation  *(35 s)*

> „Die 15-Minuten-Stadt ist heute Leitbild moderner Stadtplanung — geprägt von Carlos Moreno im Jahr 2021. Die Grundidee: jede Funktion des täglichen Lebens innerhalb eines 15-minütigen Fussweges. Wir modellieren das mit einem Schwellwert von 1.2 Kilometern bei 5 km/h. Was in Zürich zunehmend zum harten Wertfaktor für Immobilien und Einzelhandel wird, lässt sich so erstmals datenbasiert messen. Wir bewerten **alle 34 offiziellen Stadt-Zürich-Quartiere simultan** — mit einer Score-Spanne von 9 bis 92, also über 80 Punkte Differenz innerhalb derselben Stadt. Das ist die strukturelle Ungleichheit, die unser Algorithmus sichtbar macht."

### Slide 5 — Zielsetzung & Forschungsfrage  *(40 s)*

> „Unsere Zielsetzung: einen automatisierten, reproduzierbaren Geo-Algorithmus zu entwickeln, der die Erreichbarkeit der wichtigsten Funktionen des täglichen Lebens für jeden Punkt in Zürich quantifiziert — als Grundlage für Stadtplanung und Immobilien-Bewertung. Daraus leiten wir unsere Forschungsfrage ab: ***In welchen Quartieren Zürichs klaffen die grössten Lücken zwischen Wohnungsdichte und täglicher Infrastruktur?*** Gemeint sind die sechs Funktionen Einkauf, Bildung, Gesundheit, Erholung, Gastronomie und ÖV. Die Antwort wollen wir nicht qualitativ formulieren, sondern mit drei testbaren Hypothesen — und das ist die nächste Slide."

### Slide 6 — Hypothesen  *(45 s)*

> „Drei Hypothesen. **H1**: Score korreliert positiv mit dem Median-Mietpreis — wenn unser Modell sinnvoll ist, müssten Quartiere mit hoher Erreichbarkeit auch höhere Mieten haben. Test: Pearson und Spearman über alle 34 Quartiere mit den Mietpreis-Daten von Stadt Zürich Open Data. **H1a** als Robustness-Variante: Score korreliert negativ mit der Distanz zum Hauptbahnhof — das ist ein methodisch sauberer Proxy für Zentralität, ohne Marktdaten-Confounder wie Sozialstruktur oder Lärm. **H2**, der Wüsteneffekt: Gibt es Quartiere mit hoher Bevölkerungsdichte aber niedrigem Score? Das wäre eine klassische 'food desert'-Konstellation aus den USA. Test: Schwellenwert-Logik — Dichte über P75 *und* Score im untersten Quartil. Damit übergebe ich an Andrea."

---

## Andrea — Methodik & Visualisierung (Slides 7–12, ca. 3:15)

### Slide 7 — Datenquellen  *(25 s)*

> „Acht Datenquellen, alle Open Government oder Open Data — wir nutzen **keinen einzigen kommerziellen Datensatz**. OpenStreetMap via OSMnx liefert die POIs in sechs Kategorien und das Strassennetz. Geofabrik stellt das vollständige Schweiz-PBF für den optionalen PostGIS-Import bereit. BFS STATPOP liefert die Bevölkerungsdichte auf Hektar-Raster. Stadt Zürich Open Data liefert die 34 offiziellen Quartiergrenzen und den Mietpreis-Index. Swisstopo liefert Hintergrundkarten und das 2-Meter-Höhenmodell SwissALTI3D, plus der HB als LV95-Referenzpunkt für H1a."

### Slide 8 — Tools  *(30 s)*

> „Drei Performance-Highlights aus unserem Stack. Erstens: **PostGIS** als Single Source of Truth — alle räumlichen Joins per SQL mit GIST-Indizes, genau wie im Kurs gezeigt. Zweitens: **scipy KDTree** als Beschleuniger — Score-Berechnung von ursprünglich sechs Minuten naiv auf unter eine Sekunde, Faktor 400. Drittens: **NetworkX single-source-Dijkstra** für den topografischen Score — 33 Sekunden für 8092 POIs. Plus **statsmodels** für die multivariate Regression als wissenschaftliche Absicherung. **OSMnx** wickelt Overpass-API und Walking-Graph in einer Zeile Code ab."

### Slide 9 — Score-Formel  *(45 s)*

> „Die Formel: Für jede Kategorie c und jede Hex-Zelle z summieren wir alle POIs innerhalb von 1.2 Kilometern Luftlinie, gewichtet mit einem **Huff-Distance-Decay** — das `e hoch minus β mal Distanz durch d-max`. Beta ist 1.5 — je weiter weg ein POI, desto weniger Beitrag. Das Ergebnis pro Kategorie liegt zwischen 0 und 1. Den Total-Score erhalten wir aus einer gewichteten Summe der sechs Kategorien, mal hundert. **Einkauf bekommt 22 Prozent**, **Bildung, Gesundheit und ÖV je 18 Prozent**, **Erholung 14 Prozent**, **Gastronomie 10 Prozent**. Die Gewichte sind angelehnt an Moreno, alle Parameter sind in `config.py` — eine Sensitivitäts-Analyse mit alternativen Werten läuft in 10 Sekunden."

### Slide 10 — Pipeline  *(30 s)*

> „Unsere Pipeline besteht aus **neun Notebooks** — sieben Kern-Notebooks plus zwei mit Stern markierte für die topografische Erweiterung. Schritt eins lädt POIs und Stadtgrenze aus OSM. Zwei den Walking-Graph plus Quartiere und STATPOP. Drei reichert den Graph mit SwissALTI3D-Höhen an. Vier importiert alles in PostGIS. Fünf erstellt das Hex-Gitter mit Demo-Isochronen. Sechs berechnet den Score per KDTree. Sieben macht Hypothesen-Test und Robustness Check. Acht der topografische Tobler-Score mit Delta-Vergleich. Neun die finalen Karten. **Reproduzierbar mit `docker compose up` und `jupyter execute`.**"

### Slide 11 — Score-Karte  *(40 s)*

> „Hier seht ihr die Score-Karte: 744 Hex-Zellen über Zürich, je 200 Meter breit. Grün ist hohe Erreichbarkeit, Rot ist niedrige. Die **Hex-Score-Range geht von 0 bis 94, Median 23, Mittelwert 30**. Über 90 Punkte: Lindenhof, Werd, Rathaus, Langstrasse und City — der kompakte Innenstadtkern mit maximaler Funktionsmischung. Im Mittelfeld zwischen 40 und 70: Sihlfeld, Hard, Oerlikon und Enge — Wohnviertel mit guter ÖV-Anbindung. Unter 20 Punkten: Leimbach, Witikon, Hirzenbach, Affoltern und Friesenberg — Stadtperipherie und Hangwohnen. Die interaktive Folium-Karte mit allen Layern liegt im Repo unter `reports/figures/score_map.html` — wer mehr sehen will, kann sie nach dem Video selbst öffnen."

### Slide 12 — 3D-Skyline  *(25 s)*

> „Damit der Score nicht abstrakt bleibt, haben wir ihn in QGIS als **3D-Skyline** visualisiert: Die Höhe einer Hex-Zelle entspricht Score mal 30. Innenstadt-Quartiere ragen wie Wolkenkratzer, die Peripherie ist flach. Die Karte basiert auf einem Live-Layer auf der PostGIS-Tabelle — wer einen neuen POI in die Datenbank einsetzt, sieht die Höhe automatisch reagieren. Das QGIS-Projekt liegt im Repo unter `qgis/zh15min.qgz`. Damit übergebe ich an Ioannis."

---

## Ioannis — Topo, Ergebnisse, Diskussion & Schluss (Slides 13–20, ca. 4:05)

### Slide 13 — Topografische Erweiterung  *(45 s)*  ⭐

> „Eine flache 5-km/h-Annahme passt für die Innenstadt — aber Zürich hat Hänge: Zürichberg, Hönggerberg, Käferberg, Üetliberg. Deshalb haben wir das **SwissALTI3D-Höhenmodell** mit 2-Meter-Auflösung über 124 Kacheln in den Walking-Graph eingespeist und mit der **Tobler-Hiking-Funktion** für jede Kante eine realistische, steigungsabhängige Walking-Zeit abgeleitet — bergauf langsamer, bergab schneller. Der Vergleich zum flachen Score zeigt ein klares Muster: **Verlierer sind exakt die Hangzonen** — Oberstrass minus 14, Fluntern minus 11, **Gewerbeschule minus 10** — die liegt mitten in der Stadt, aber am Üetlibergstrasse-Hang — Alt-Wiedikon und Wipkingen je minus 8 Punkte. **Gewinner sind flache See-Quartiere** — Mühlebach plus 8.5, Seefeld plus 6, Oerlikon plus 4. Median-Delta minus 2.3, Range minus 33 bis plus 19. Topografie ist also nicht nur Confounder, sondern eigenständiger Effekt — den wir auf Slide 18 nochmal in der Regression aufgreifen."

### Slide 14 — Hypothesen-Test  *(35 s)*

> „Die drei Hypothesen quantitativ getestet. **H1 unterstützt**: Score und Median-Mietpreis korrelieren positiv mit Spearman ρ gleich plus 0.56, Pearson r identisch, p unter 10 hoch minus 3 bei n gleich 34. Erreichbarkeit übersetzt sich tatsächlich in den Wohnungsmarkt. **H1a hochsignifikant**: ρ minus 0.81, r minus 0.84, p unter 10 hoch minus 8. Distanz zum Hauptbahnhof ist ein noch stärkerer, methodisch sauberer Prädiktor. Beide H1-Tests konvergieren. **H2 quantitativ widerlegt**: null von 34 Quartieren erfüllen die Wüsten-Schwellen. **Zürich hat keine US-typischen 'food deserts'** — wo Menschen wohnen, gibt es auch Versorgung. Stadtplanerisch eine positive Aussage."

### Slide 15 — Top- & Flop-Quartiere  *(25 s)*

> „Die Top fünf: Lindenhof, Werd, Rathaus und Langstrasse mit 91 bis 92 Punkten, City mit 91 — alle in der kompakten Innenstadt. Die Flop fünf: Leimbach mit 9 Punkten, Witikon mit 10, Hirzenbach, Affoltern und Friesenberg je 19 Punkte — alle in der Peripherie, drei davon in Hanglagen. **Über 80 Score-Punkte Differenz innerhalb derselben Stadt** — das ist die räumliche Ungleichheit, die unser Algorithmus exakt quantifiziert."

### Slide 16 — Cluster-Typologie  *(35 s)*

> „Wenn wir nicht den linearen Total-Score, sondern die sechs Kategorie-Erreichbarkeiten clustern, ergibt sich eine vier-typische Quartier-Landschaft. **Typ A — zentrale Mischung** — alle sechs Funktionen in Walking-Distanz, sieben Quartiere, Durchschnitt 90. **Typ B — Mittelband mit ÖV** — neun Wohnquartiere mit guter Tram- und Bus-Anbindung, Durchschnitt 59. **Typ C — Grünraum-dominiert** — Saatlen, Seebach, Schwamendingen-Mitte und Friesenberg. Erholung-Wert 0.63 — der höchste über alle Cluster — alles andere tief. Wald- und Parknähe statt zentraler Versorgung. **Typ D — Periphere Wohnviertel** — 14 Quartiere mit durchgehend unterdurchschnittlichen Werten. Diese Typologie ist methodisch unabhängig vom linearen Ranking und stützt die Erzählung mehrdimensional."

### Slide 17 — Antwort auf Forschungsfrage  *(25 s)*

> „Die grössten Versorgungslücken liegen klar in der Peripherie — Leimbach, Witikon, Hirzenbach, Affoltern, Friesenberg — über 80 Punkte Abstand zum Zentrum. Daraus drei konkrete Implikationen: für die Stadtplanung Versorgungs-Auflagen bei Entwicklungsgebieten vor der Erstvermietung, für Investoren preisliche Chancen in Score-unter-40-Lagen mit Vermarktungsrisiko, für den Einzelhandel klare Expansions-Targets. **Aber Vorsicht: Korrelation ist nicht Kausalität** — deshalb schauen wir uns Confounder an."

### Slide 18 — Robustness Check  *(45 s)*  ⭐

> *(Auf die drei Status-Tags zeigen)*
> „Die multivariate Regression mit drei Prädiktoren — Distanz zum Hauptbahnhof, Höhe aus dem echten SwissALTI3D-DEM und POI-Dichte — erklärt **91 Prozent der Score-Varianz**, adjustiertes R² gleich 0.90. **Distanz bleibt nach Kontrolle hochsignifikant**: β minus 9.52 bei p unter 10 hoch minus 6. **Topografie ist tatsächlich Co-Treiber**: höher gelegen gleich niedrigerer Score, β minus 0.107 bei p unter 10 hoch minus 3. POI-Dichte als dritter Prädiktor ebenfalls hochsignifikant. Damit ist **H1a robust gegen Confounder**. Plus: die Sensitivitäts-Analyse über vier Gewichts-Szenarien zeigt Spearman-Rang-Korrelation über 0.98 in allen Varianten — das Ranking ist **methodisch stabil**. Und die Luftlinien-Approximation im Score: Pearson 0.991 gegen echte Strassennetz-Distanz — also defensiv vertretbar."

### Slide 19 — Limitationen  *(25 s)*

> „Vier Limitationen, die wir offen benennen. Erstens **OSM-Datenqualität** — kleine, unmappte Geschäfte fehlen, wir nehmen die Verzerrung als gering an. Zweitens **Tobler-Modell-Annahme** — die Funktion ist auf Wandern in offenem Gelände kalibriert, nicht auf städtisches Gehen mit Ampeln und Querstrassen. Drittens **Single-City-Befund** — die H2-Falsifikation gilt für Zürich, nicht zwingend für andere Städte. Viertens **Mietpreis-Confounder** — Premium-Wohnlagen wie Hottingen oder Seefeld haben hohe Mieten trotz niedrigem Score, weil ruhige Hanglage auch Lagequalität ist. **Wir wissen, was wir nicht wissen.**"

### Slide 20 — Ausblick & Dank  *(20 s)*

> „Vier nächste Iterationen: ÖV-Reisezeiten via SBB GTFS, Echtzeit-Re-Scoring bei neuen POIs in einer QGIS-Live-Demo, multivariate Erweiterung mit ÖV-Anbindung, und nationaler Vergleich mit Winterthur und Basel. Das gesamte Repository steht öffentlich auf **github.com/sanirmem/zh15min**, reproduzierbar mit `docker compose up`. Vielen Dank für eure Aufmerksamkeit — wir freuen uns auf eure Fragen."

---

## Q&A — vorbereitete Antworten

### „Warum genau diese sechs POI-Kategorien und Gewichte?"

> „Inspiriert vom Moreno-Framework der sechs essenziellen urbanen Funktionen. Die Gewichte sind Parameter in `src/zh15min/config.py` — eine Sensitivitäts-Analyse mit alternativen Werten ist in unter 10 Sekunden machbar. Wir haben vier Szenarien getestet — Original, ÖV-fokussiert, Erholung-fokussiert und Equal-Weights. **Die Spearman-Rang-Korrelation der Quartier-Reihenfolge bleibt in allen Szenarien über 0.98** — das Ranking ist methodisch robust. Steht so auf Slide 18."

### „Wieso 34 Quartiere und nicht eine feinere Aufteilung?"

> „Das ist die **offizielle Stadt-Zürich-Liste der statistischen Quartiere** — bezogen über den WFS-Endpunkt von `ogd.stadt-zuerich.ch`. Wir haben uns bewusst gegen die feinere OSM-`admin_level=10`-Aufteilung entschieden, weil die offizielle Geometrie mit dem Mietpreis-Index und den STATPOP-Bevölkerungsdaten einheitlich joinbar ist. **Konsistente Datengrundlage** ist wichtiger als feinere Granularität — und mit 744 Hex-Zellen auf 200 m Apothem haben wir die räumliche Auflösung intern ohnehin viel feiner."

### „Warum Luftlinien-Distanz statt echter Walking-Distanz im Hauptscore?"

> „Wir haben das empirisch validiert in Notebook 06: für alle 34 Quartier-Centroide haben wir die echte Strassengraph-Distanz zum HB via Dijkstra berechnet und mit der Luftlinie korreliert. **Pearson r = 0.991, Median-Detour-Faktor 1.20, Worst-Case 1.41.** Die Luftlinie erklärt **98.2 Prozent der Varianz** in echten Walking-Distanzen — defensiv voll vertretbar. Für die Score-Berechnung über 744 Zellen mal 8 092 POIs ist das ein Performance-Faktor von rund 400 (KDTree statt Dijkstra). **Plus** wir haben mit der Tobler-Erweiterung in Notebook 06b zusätzlich die topografisch korrekte Variante geliefert — beide Ansätze sind im Repo."

### „Wie geht ihr mit Confoundern um?" ⭐

> „Genau dafür haben wir den Robustness Check auf Slide 18 gemacht: multivariate OLS-Regression mit Distanz, Höhe aus echtem SwissALTI3D-DEM und POI-Dichte. **R² = 0.91, adjustiert 0.90.** Distanz bleibt nach Kontrolle hochsignifikant — β minus 9.52, p unter 10 hoch minus 6. Topografie ist Co-Treiber — β minus 0.107, p unter 10 hoch minus 3. POI-Dichte als dritter Prädiktor ebenfalls hochsignifikant. **Plus** der eigenständige topografische Score auf Slide 13 zeigt das Pattern visuell — Hangzonen verlieren exakt das, was die Regression vorhersagt. Konvergenz zwischen Regressionsmodell und Score-Differenzkarte."

### „Tobler — ist das die richtige Wahl für eine Stadt?"

> „Tobler 1993 ist seit über 30 Jahren der Standard für topografisches Routing und passt für menschliches Gehverhalten — Maximum bei minus 5 Prozent Steigung mit 6 km/h, exponentieller Abfall bei steileren Gradienten. Bei flachem Gelände ergibt Tobler ungefähr 5.04 km/h — also kompatibel mit unserer flachen 5-km/h-Annahme. **Wir clippen extreme Steigungen über 50 Prozent**, weil das in OSM Treppen-Artefakte sind, nicht echte Strassen. Die Limitation, dass Tobler nicht stadt-spezifisch ist (Ampeln, Querstrassen), benennen wir auf Slide 19 offen."

### „H1 ist signifikant — aber Mietpreise haben doch ganz andere Treiber?"

> „Stimmt — der bivariate Spearman ρ gleich plus 0.56 ist erstmal nur eine Korrelation. **Die multivariate Kontrolle kommt auf Slide 18**: Distanz, Höhe und POI-Dichte erklären zusammen 91 Prozent der Score-Varianz. Mietpreise hängen aber nicht nur am Score — Premium-Wohnlagen wie Hottingen und Seefeld haben hohe Mieten OHNE hohe POI-Dichte (ruhige plus grüne Lage als alternative 'gute Lage'-Definition). Diese Limitation steht explizit auf Slide 19. Was H1 unterstützt: die Richtung der Korrelation ist robust positiv und konvergiert mit H1a."

### „Warum gerade 1.2 km als d-max und nicht 1.25 km?"

> „5 km/h mal 15 Minuten gibt geometrisch 1.25 km. Wir runden auf 1.2 km, weil wir konservativ schätzen und weil OSM-POIs nicht zentimetergenau lokalisiert sind. **Die Sensitivität gegenüber dieser Annahme ist klein** — wir haben in Notebook 06 die Score-Rangkorrelation für d-max von 1.0, 1.2 und 1.5 km getestet — Spearman bleibt über 0.97."

### „Warum keine ÖV-Reisezeiten statt nur ÖV-POIs?"

> „Aktuell zählen wir Tram-/Bus-Haltestellen als ÖV-POIs — das gewichtet *physische Erreichbarkeit der Haltestelle*, nicht *Reisezeit zum Ziel*. Das ist eine bewusste Vereinfachung — die SBB-GTFS-Erweiterung steht explizit als nächster Schritt auf Slide 20. Mit GTFS könnten wir 'Reisezeit zum HB' als Score-Komponente integrieren und nicht nur 'Distanz zur Haltestelle'."

---

## Tipps für die Aufnahme

- **Tempo**: ein bisschen langsamer sprechen als ihr denkt — bei 9 Minuten lieber 15 % unter Tempo. Lieber kleine Pausen als überstürztes Vorlesen.
- **Mikrofon**: Headset, nicht Laptop-Mic. Vor der Aufnahme einmal in Quicktime einen 10-Sekunden-Test machen.
- **Slides mit Bildern**: alle Visualisierungen sind als statische Screenshots ins Deck eingebettet (`score_map.png`, `qgis_3d_score.png`, `score_flat_vs_topo.png`). Im Video wird **nichts live geöffnet** — wir sprechen jeweils über das, was die Folie schon zeigt. Die interaktiven Versionen (Folium-HTML, QGIS-Projekt) liegen im Repo und werden im Sprechtext kurz erwähnt, damit die Hörer wissen, wo sie selbst klicken können.
- **Aufnahme-Strategie**: **ein Take pro Person**, dann alles in einem Cut zusammenschneiden — das wirkt zusammenhängender als ein gemeinsamer Take, in dem ihr euch gegenseitig unterbrechen müsst.
- **Stoppuhr**: Memis 2:45, Andrea 3:15, Ioannis 4:05 → Total ~10:05. Wenn ihr unter 9:30 bleiben wollt, kann Ioannis bei Slide 19 (Limitationen) 10 Sekunden sparen — das kommt in der Q&A sowieso wieder hoch.
- **Übergänge**: Memis endet auf „Damit übergebe ich an Andrea." Andrea endet auf „Damit übergebe ich an Ioannis." Ioannis schliesst mit „Vielen Dank für eure Aufmerksamkeit."
- **Bei Verzählen**: ruhig durchziehen, nicht neu ansetzen — die Aufnahme ist ohnehin durchschnittlich nicht perfekt, und Stocken wirkt natürlicher als ein zweites Take mit hörbarem „Ach Mist".

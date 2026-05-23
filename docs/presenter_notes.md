# Sprecher-Skript für die Videopräsentation

Vollständige, ablesbare Texte für alle 20 Slides. Drei Personen, ca. 3 Minuten pro Person, gesamthaft ungefähr 9 bis 10 Minuten.

Aufteilung:
- Memis: Slides 1–6 (Einleitung)
- Andrea: Slides 7–12 (Methodik und Visualisierung)
- Ioannis: Slides 13–20 (Topografie, Ergebnisse, Diskussion, Schluss)

---

## Memis — Einleitung (Slides 1–6)

### Slide 1 — Titel  *(15 s)*

> Diese Präsentation behandelt das Projekt "The 15-Minute City Intelligence". Es handelt sich um einen Geo-Algorithmus, der die fussläufige Erreichbarkeit von Funktionen des täglichen Lebens für die Stadt Zürich berechnet und Versorgungslücken identifiziert. Das Projekt wurde im Rahmen des Moduls "Einsatz von Geodaten in Marketing" an der ZHAW im Frühjahrssemester 2026 erstellt.

### Slide 2 — Inhaltsverzeichnis  *(10 s)*

> Die Präsentation gliedert sich in sechs Themenblöcke: Übersicht und Workflow, Einleitung mit Hintergrund und Hypothesen, Methodik, Ergebnisse, Diskussion und Schlussfolgerungen sowie Limitationen und Ausblick. Diese Struktur entspricht den Modulvorgaben.

### Slide 3 — Workflow-Übersicht  *(20 s)*

> Der Workflow besteht aus sechs Schritten. Erstens werden die Daten aus OpenStreetMap, BFS STATPOP, Stadt Zürich Open Data und swisstopo geladen. Zweitens folgt der Import in eine PostGIS-Datenbank. Drittens wird ein Hexagon-Gitter mit 200 Metern Apothem über die Stadt gelegt, was 744 Analyse-Zellen ergibt. Viertens werden die Walking-Isochronen mit einem Huff-Distance-Decay berechnet. Fünftens wird daraus der Score auf einer Skala von 0 bis 100 abgeleitet. Sechstens erfolgt die Visualisierung in Folium, Matplotlib und QGIS.

### Slide 4 — Hintergrund und Motivation  *(35 s)*

> Das Konzept der 15-Minuten-Stadt wurde 2021 von Carlos Moreno geprägt. Es beschreibt die Idee, dass alle Funktionen des täglichen Lebens innerhalb eines 15-minütigen Fussweges erreichbar sein sollen. Im Modell wird der Schwellwert mit 1.2 Kilometern bei 5 km/h Gehgeschwindigkeit operationalisiert. Das Konzept ist in der Stadtplanung etabliert und gewinnt zunehmend Relevanz für Immobilien- und Einzelhandelsbewertungen. In der vorliegenden Arbeit werden alle 34 offiziellen statistischen Quartiere der Stadt Zürich simultan bewertet. Die Score-Werte reichen auf Quartiersebene von 9 bis 92 Punkten.

### Slide 5 — Zielsetzung und Forschungsfrage  *(40 s)*

> Die Zielsetzung des Projekts ist die Entwicklung eines automatisierten und reproduzierbaren Geo-Algorithmus, der die Erreichbarkeit der wichtigsten Funktionen des täglichen Lebens für jeden Punkt in Zürich quantifiziert. Die Ergebnisse sollen als Grundlage für Stadtplanung und Immobilien-Bewertung dienen. Die Forschungsfrage lautet: In welchen Quartieren Zürichs klaffen die grössten Lücken zwischen Wohnungsdichte und täglicher Infrastruktur? Unter täglicher Infrastruktur verstehen wir die sechs Funktionen Einkauf, Bildung, Gesundheit, Erholung, Gastronomie und ÖV.

### Slide 6 — Hypothesen  *(45 s)*

> Aus der Forschungsfrage werden drei testbare Hypothesen abgeleitet. Hypothese 1 postuliert eine positive Korrelation zwischen Score und Median-Mietpreis. Getestet wird sie mit Pearson- und Spearman-Korrelationen über alle 34 Quartiere unter Verwendung der Mietpreis-Daten von Stadt Zürich Open Data. Hypothese 1a ist eine Robustness-Variante: Sie postuliert eine negative Korrelation zwischen Score und Distanz zum Hauptbahnhof. Die HB-Distanz dient als Proxy für Zentralität ohne Markt-Confounder. Hypothese 2 untersucht den sogenannten Wüsteneffekt, also die Existenz von Quartieren mit hoher Bevölkerungsdichte bei gleichzeitig niedrigem Score. Getestet wird sie mit einer Schwellenwert-Logik: Dichte oberhalb des 75. Perzentils und Score im untersten Quartil. Damit übergebe ich an Andrea.

---

## Andrea — Methodik und Visualisierung (Slides 7–12)

### Slide 7 — Datenquellen  *(25 s)*

> Das Projekt verwendet acht Datenquellen, alle aus Open Government oder Open Data. Es wurden keine kommerziellen Datensätze verwendet. OpenStreetMap liefert über die OSMnx-Bibliothek die POIs in sechs Kategorien sowie das Walking-Strassennetz. Geofabrik stellt das vollständige Schweiz-PBF für den optionalen PostGIS-Import bereit. BFS STATPOP liefert die Bevölkerungsdichte auf Hektar-Raster. Stadt Zürich Open Data liefert die 34 offiziellen Quartiergrenzen und den Mietpreis-Index. Swisstopo liefert Hintergrundkarten und das 2-Meter-Höhenmodell SwissALTI3D.

### Slide 8 — Tools  *(30 s)*

> Der Tech-Stack besteht aus folgenden Komponenten: PostGIS dient als zentrale Datenhaltung, mit räumlichen Joins via SQL und GIST-Indizes. OSMnx kombiniert Overpass-API-Zugriff und Walking-Graph-Aufbau. Die Bibliothek scipy stellt mit der KDTree-Implementation einen effizienten Distanz-Lookup zur Verfügung, der die Score-Berechnung von ursprünglich rund sechs Minuten auf unter eine Sekunde reduziert. NetworkX wird für den single-source-Dijkstra-Algorithmus eingesetzt, der den topografischen Score in 33 Sekunden für 8092 POIs berechnet. Die multivariate Regression wird mit statsmodels umgesetzt.

### Slide 9 — Score-Formel  *(45 s)*

> Der Score wird in zwei Stufen berechnet. Erstens wird für jede Kategorie c und jede Hex-Zelle z eine Accessibility-Komponente A_c bestimmt. Dabei werden alle POIs der Kategorie innerhalb von 1.2 Kilometern Luftlinie summiert, jedoch gewichtet mit einem Huff-Distance-Decay der Form exponential von minus β mal Distanz geteilt durch d_max. Der Parameter β beträgt 1.5. Je grösser die Distanz, desto geringer der Beitrag eines POIs. Der Total-Score ergibt sich aus der gewichteten Summe der sechs Kategorien, multipliziert mit 100. Die Gewichte sind: Einkauf 22 Prozent, Bildung 18 Prozent, Gesundheit 18 Prozent, Erholung 14 Prozent, Gastronomie 10 Prozent, ÖV 18 Prozent. Die Gewichte sind angelehnt an Moreno und in der Datei config.py parametrisiert.

### Slide 10 — Pipeline  *(30 s)*

> Die Implementation besteht aus neun Jupyter-Notebooks. Die Notebooks 02b und 06b sind die topografische Erweiterung. Notebook 1 lädt POIs und Stadtgrenze aus OSM. Notebook 2 erstellt den Walking-Graph und lädt STATPOP sowie die Quartiergrenzen. Notebook 2b reichert den Graph mit SwissALTI3D-Höhen an. Notebook 3 importiert alle Daten nach PostGIS. Notebook 4 erstellt das Hex-Gitter und Demo-Isochronen. Notebook 5 berechnet den Score. Notebook 6 testet die Hypothesen und führt den Robustness Check durch. Notebook 6b berechnet den topografischen Tobler-Score mit Delta-Vergleich. Notebook 7 erstellt die finalen Karten. Die gesamte Pipeline ist via docker compose und jupyter execute reproduzierbar.

### Slide 11 — Score-Karte  *(40 s)*

> Die Score-Karte zeigt 744 Hexagonal-Zellen über der Stadt Zürich, je 200 Meter breit. Die Farbskala reicht von Grün für hohe Erreichbarkeit zu Rot für niedrige. Die Hex-Score-Range geht von 0 bis 94, der Median liegt bei 23, der Mittelwert bei 30. Über 90 Punkte erreichen die Quartiere Lindenhof, Werd, Rathaus, Langstrasse und City — der kompakte Innenstadtkern. Im Mittelfeld zwischen 40 und 70 Punkten liegen Sihlfeld, Hard, Oerlikon und Enge — Wohnviertel mit guter ÖV-Anbindung. Unter 20 Punkten liegen Leimbach, Witikon, Hirzenbach, Affoltern und Friesenberg — alle in der Stadtperipherie oder in Hanglagen. Die interaktive Folium-Version der Karte findet sich im Repository unter reports/figures/score_map.html.

### Slide 12 — 3D-Skyline  *(25 s)*

> Zur Veranschaulichung wurde der Score in QGIS als 3D-Skyline visualisiert. Die Höhe einer Hex-Zelle entspricht dem Score multipliziert mit 30. Innenstadt-Quartiere erscheinen dadurch erhöht, während die Peripherie flach bleibt. Die QGIS-Visualisierung basiert auf einem direkten Layer-Zugriff auf die PostGIS-Tabelle. Bei einer Änderung der Datenbasis aktualisiert sich die Darstellung entsprechend. Das QGIS-Projekt liegt im Repository unter qgis/zh15min.qgz. Damit übergebe ich an Ioannis.

---

## Ioannis — Topografie, Ergebnisse, Diskussion und Schluss (Slides 13–20)

### Slide 13 — Topografische Erweiterung  *(45 s)*

> Eine konstante Gehgeschwindigkeit von 5 km/h ist für ebenes Gelände eine adäquate Annahme. Die Stadt Zürich weist jedoch mehrere ausgeprägte Hanglagen auf, darunter Zürichberg, Hönggerberg, Käferberg und Üetliberg. Aus diesem Grund wurde das Höhenmodell SwissALTI3D mit 2 Metern Auflösung über 124 Kacheln in den Walking-Graph eingespeist. Mittels Tobler-Hiking-Funktion wurde für jede Kante eine steigungsabhängige Walking-Zeit abgeleitet. Der Vergleich zwischen flachem und topografischem Score zeigt ein konsistentes Muster. Die grössten Verluste entstehen in Hangzonen: Oberstrass minus 13.8, Fluntern minus 11.2, Gewerbeschule minus 10.1 — letzteres trotz zentraler Lage, da am Üetlibergstrasse-Hang gelegen — Alt-Wiedikon minus 8.1 und Wipkingen minus 8.0. Gewinner sind flache See-Quartiere: Mühlebach plus 8.5, Seefeld plus 6.3, Oerlikon plus 4.4. Das Median-Delta liegt bei minus 2.3 Punkten, die Range zwischen minus 33 und plus 19.

### Slide 14 — Hypothesen-Test  *(35 s)*

> Die drei Hypothesen wurden quantitativ überprüft. Hypothese 1 wird unterstützt: Score und Median-Mietpreis korrelieren positiv mit einem Spearman-Koeffizienten von plus 0.56 und einem Pearson-Wert von ebenfalls plus 0.56, bei einem p-Wert unter 10 hoch minus 3 und n gleich 34. Hypothese 1a ist hochsignifikant: Spearman gleich minus 0.81, Pearson gleich minus 0.84, p-Wert unter 10 hoch minus 8. Die Distanz zum Hauptbahnhof erweist sich als stärkerer Prädiktor als der Mietpreis. Hypothese 2 wird quantitativ widerlegt: Kein einziges der 34 Quartiere erfüllt die definierten Wüsten-Schwellwerte. Die Stadtstruktur Zürichs ist in diesem Sinne konsistent.

### Slide 15 — Top- und Flop-Quartiere  *(25 s)*

> Die fünf höchstplatzierten Quartiere sind Lindenhof, Werd und Rathaus mit je 92 Punkten sowie Langstrasse und City mit je 91 Punkten. Die fünf niedrigsten sind Leimbach mit 9 Punkten, Witikon mit 10 Punkten sowie Hirzenbach, Affoltern und Friesenberg mit je 19 Punkten. Die Spannweite zwischen den Extremen beträgt über 80 Score-Punkte innerhalb derselben Stadt.

### Slide 16 — Cluster-Typologie  *(35 s)*

> Als ergänzende Analyse wurde ein K-Means-Clustering mit k gleich 4 auf den sechs Kategorie-Erreichbarkeiten durchgeführt, nicht auf dem aggregierten Score. Es resultieren vier Quartier-Typen. Typ A umfasst die zentrale Mischung mit allen sechs Funktionen in Walking-Distanz: sieben Quartiere, durchschnittlicher Score 90. Typ B ist das Mittelband mit ÖV-Anbindung: neun Wohnquartiere, Durchschnitt 59. Typ C ist Grünraum-dominiert und umfasst Saatlen, Seebach, Schwamendingen-Mitte und Friesenberg: Erholung-Accessibility 0.63 im Mittel, andere Kategorien unterdurchschnittlich. Typ D umfasst 14 periphere Wohnviertel mit durchgehend unterdurchschnittlichen Werten. Die Typologie liefert eine mehrdimensionale Charakterisierung jenseits des linearen Rankings.

### Slide 17 — Antwort auf die Forschungsfrage  *(25 s)*

> Die grössten Versorgungslücken liegen in der Stadtperipherie. Konkret betroffen sind Leimbach, Witikon, Hirzenbach, Affoltern und Friesenberg, mit einem Abstand von über 80 Punkten zum Stadtzentrum. Daraus ergeben sich drei Implikationen: Für die Stadtplanung Versorgungs-Auflagen bei Entwicklungsgebieten vor der Erstvermietung. Für Investoren preisliche Chancen in Score-unter-40-Lagen unter Berücksichtigung des Vermarktungsrisikos. Für den Einzelhandel klare Expansions-Targets.

### Slide 18 — Robustness Check  *(45 s)*

> Eine multivariate OLS-Regression wurde mit drei Prädiktoren durchgeführt: Distanz zum Hauptbahnhof, Höhe aus dem SwissALTI3D-DEM und POI-Dichte. Das Modell erklärt 91 Prozent der Varianz des Scores. Das adjustierte R² beträgt 0.90. Die Distanz zum Hauptbahnhof bleibt nach Kontrolle der Confounder hochsignifikant mit einem partiellen β von minus 9.52 und p kleiner 10 hoch minus 6. Die Topografie ist ein signifikanter Co-Treiber: höhere Lage korreliert mit niedrigerem Score, β gleich minus 0.107 bei p kleiner 10 hoch minus 3. Die POI-Dichte ist als dritter Prädiktor ebenfalls hochsignifikant. Die Sensitivitäts-Analyse mit vier alternativen Gewichts-Szenarien zeigt eine Spearman-Rang-Korrelation grösser als 0.98 in allen Varianten. Die Luftlinien-Approximation des Scores wurde gegen die echte Strassennetz-Distanz validiert; der Pearson-Koeffizient beträgt 0.991.

### Slide 19 — Limitationen  *(25 s)*

> Vier Limitationen sind zu nennen. Erstens die Datenqualität von OSM: kleine, nicht erfasste Geschäfte fehlen. Wir gehen von einer geringen Verzerrung aus, da Geschäfte ähnlicher Klassifikation in OSM konsistent erfasst sind. Zweitens die Tobler-Modell-Annahme: die Funktion ist auf Wandern in offenem Gelände kalibriert, nicht auf städtisches Gehen mit Ampeln und Querstrassen. Drittens der Single-City-Befund: die Falsifikation von Hypothese 2 gilt für Zürich, jedoch nicht zwingend für andere Städte. Viertens der Mietpreis-Confounder: Premium-Wohnlagen wie Hottingen oder Seefeld weisen hohe Mieten trotz niedrigerem Score auf.

### Slide 20 — Ausblick  *(20 s)*

> Vier mögliche Erweiterungen wurden identifiziert: Erstens die Integration von DEM-basierter Topografie und multivariater Regression mit ÖV-Anbindung. Zweitens Echtzeit-Mobilitätsdaten via SBB GTFS und ZVV-Reisezeiten. Drittens dynamisches Re-Scoring bei neuen POIs. Viertens die methodische Erweiterung auf Winterthur und Basel als nationaler Vergleich. Das vollständige Repository steht unter github.com/sanirmem/zh15min zur Verfügung. Damit endet unsere Präsentation.

---

## Q&A — vorbereitete Antworten

### „Warum genau diese sechs POI-Kategorien und Gewichte?"

> Die Kategorien folgen dem Moreno-Framework der sechs essenziellen urbanen Funktionen. Die Gewichte sind in src/zh15min/config.py parametrisiert. Wir haben eine Sensitivitäts-Analyse mit vier Szenarien durchgeführt: Original, ÖV-fokussiert, Erholung-fokussiert und Equal-Weights. Die Spearman-Rang-Korrelation der Quartier-Reihenfolge bleibt in allen Szenarien über 0.98. Das Ranking ist methodisch robust gegen die Gewichtswahl. Die entsprechenden Werte sind auf Slide 18 dokumentiert.

### „Wieso 34 Quartiere und nicht eine feinere Aufteilung?"

> Es handelt sich um die offizielle Stadt-Zürich-Liste der statistischen Quartiere, bezogen über den WFS-Endpunkt von ogd.stadt-zuerich.ch. Eine feinere Aufteilung wäre über OSM mit admin_level gleich 10 möglich, jedoch ist die offizielle Geometrie mit den Mietpreis-Daten und STATPOP-Bevölkerungsdaten konsistent joinbar. Die räumliche Auflösung bleibt mit 744 Hex-Zellen auf 200 Metern Apothem intern feiner.

### „Warum Luftlinien-Distanz statt echter Walking-Distanz im Hauptscore?"

> Diese Vereinfachung wurde empirisch validiert. Für alle 34 Quartier-Centroide wurde die Strassengraph-Distanz zum Hauptbahnhof per Dijkstra berechnet und mit der Luftlinie korreliert. Der Pearson-Koeffizient beträgt 0.991, der Median-Detour-Faktor 1.20 und der Worst-Case 1.41. Die Luftlinie erklärt 98.2 Prozent der Varianz in echten Walking-Distanzen. Der Performance-Gewinn beträgt rund Faktor 400 (KDTree statt Dijkstra). Zusätzlich liegt mit Notebook 06b die topografisch korrekte Variante via Tobler-Funktion vor.

### „Wie wird mit Confoundern umgegangen?"

> Der Robustness Check auf Slide 18 adressiert diese Frage. Eine multivariate OLS-Regression mit Distanz zum Hauptbahnhof, Höhe aus dem SwissALTI3D-DEM und POI-Dichte erklärt 91 Prozent der Score-Varianz. Adjustiertes R² gleich 0.90. Die Distanz bleibt nach Kontrolle hochsignifikant (β gleich minus 9.52, p kleiner 10 hoch minus 6). Die Topografie ist ein signifikanter Co-Treiber (β gleich minus 0.107, p kleiner 10 hoch minus 3). Die POI-Dichte ist als dritter Prädiktor ebenfalls hochsignifikant.

### „Ist die Tobler-Funktion für eine Stadt geeignet?"

> Die Tobler-Hiking-Funktion stammt aus dem Jahr 1993 und ist der etablierte Standard für topografisches Routing. Sie modelliert die Gehgeschwindigkeit als Funktion der Steigung, mit einem Maximum von 6 km/h bei minus 5 Prozent Steigung und exponentiellem Abfall bei steileren Gradienten. Bei ebenem Gelände ergibt die Funktion rund 5.04 km/h, was mit der flachen 5-km/h-Annahme konsistent ist. Extreme Steigungen über 50 Prozent werden geclippt, da es sich in OSM in der Regel um Treppen-Artefakte handelt. Die Limitation, dass die Funktion nicht speziell auf städtisches Gehen mit Ampeln und Querstrassen kalibriert ist, wurde auf Slide 19 transparent benannt.

### „Wie sind die Hypothesen-Ergebnisse vor Confoundern zu interpretieren?"

> Der bivariate Spearman-Koeffizient von plus 0.56 für Hypothese 1 ist eine reine Korrelation. Die multivariate Kontrolle erfolgt auf Slide 18, wo Distanz, Höhe und POI-Dichte zusammen 91 Prozent der Score-Varianz erklären. Mietpreise hängen nicht ausschliesslich am Score. Premium-Wohnlagen wie Hottingen und Seefeld weisen hohe Mieten ohne hohe POI-Dichte auf. Diese Limitation ist auf Slide 19 dokumentiert.

### „Warum d_max gleich 1.2 km und nicht 1.25 km?"

> Geometrisch ergibt sich aus 5 km/h mal 15 Minuten ein Wert von 1.25 Kilometern. Wir runden konservativ auf 1.2 Kilometer. Die Sensitivität gegenüber dieser Annahme wurde geprüft: Bei d_max von 1.0, 1.2 und 1.5 Kilometern bleibt der Spearman-Rang der Quartiere über 0.97 stabil.

### „Wieso werden ÖV-POIs gezählt statt Reisezeiten verwendet?"

> Die aktuelle Implementation zählt Tram- und Bushaltestellen als ÖV-POIs. Dies gewichtet die physische Erreichbarkeit der Haltestelle, nicht die Reisezeit zum Ziel. Eine Erweiterung mit SBB-GTFS-Daten ist als nächste Iteration auf Slide 20 vorgesehen.

---

## Aufnahme-Hinweise

- Tempo: bewusst etwas langsamer sprechen als gewohnt. Bei 9 bis 10 Minuten Gesamtlänge ist Verständlichkeit wichtiger als Zügigkeit.
- Mikrofon: Headset oder externes Mikrofon, nicht das interne Laptop-Mikrofon. Ein kurzer Pegel-Test vor der Aufnahme ist empfehlenswert.
- Folien: Alle Visualisierungen sind als statische Screenshots in das Deck eingebettet. Während der Aufnahme wird nichts live geöffnet. Die interaktiven Versionen (Folium-HTML, QGIS-Projekt) werden im Sprechtext einmal kurz erwähnt.
- Aufnahme-Strategie: Pro Person ein separater Take. Im Schnitt werden die drei Takes zu einem durchgehenden Video zusammengeführt.
- Stoppuhr-Plan: Memis ca. 2:45, Andrea ca. 3:15, Ioannis ca. 4:05. Gesamtlänge etwa 10 Minuten. Sollte das Gesamtvideo unter 9:30 bleiben müssen, kann auf Slide 19 (Limitationen) ca. 10 Sekunden gekürzt werden.
- Übergaben: Memis schliesst Slide 6 mit "Damit übergebe ich an Andrea." Andrea schliesst Slide 12 mit "Damit übergebe ich an Ioannis." Ioannis schliesst Slide 20 mit "Damit endet unsere Präsentation."
- Bei Versprechen: durchziehen, nicht neu ansetzen. Versprechen wirken im Schnitt unauffälliger als wiederholte Anfänge.

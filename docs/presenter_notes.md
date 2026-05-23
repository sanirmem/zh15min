# Sprecher-Skript für die Videopräsentation

Vollständige, ablesbare Texte für alle 20 Slides. Drei Personen, gesamthaft ungefähr 9 bis 10 Minuten.

Aufteilung:
- Ioannis: Slides 1–6 (Einleitung)
- Andrea: Slides 7–12 (Methodik und Visualisierung)
- Memis: Slides 13–20 (Topografie, Ergebnisse, Diskussion, Schluss)

---

## Ioannis — Einleitung (Slides 1–6)

### Slide 1 — Titel  *(15 s)*

> Diese Präsentation behandelt "The 15-Minute City Intelligence" — einen Geo-Algorithmus zur Quantifizierung der fussläufigen Erreichbarkeit täglicher Funktionen in Zürich. Das Projekt entstand im Modul "Einsatz von Geodaten in Marketing" an der ZHAW im Frühjahr 2026.

### Slide 2 — Inhaltsverzeichnis  *(8 s)*

> Die Präsentation folgt der vorgegebenen Modul-Struktur in sechs Themenblöcken.

### Slide 3 — Workflow-Übersicht  *(15 s)*

> Der Workflow besteht aus sechs Schritten — von der Datenbeschaffung über den PostGIS-Import, das Hex-Gitter mit 744 Analyse-Zellen, die Walking-Isochronen, die Score-Berechnung bis zur Visualisierung. Die Pipeline ist mit docker compose vollständig reproduzierbar.

### Slide 4 — Hintergrund und Motivation  *(25 s)*

> Das Konzept der 15-Minuten-Stadt wurde 2021 von Carlos Moreno geprägt: alle Funktionen des täglichen Lebens innerhalb eines 15-minütigen Fussweges. Im Modell entspricht das 1.2 Kilometern bei 5 km/h. Das Konzept gewinnt zunehmend Relevanz für Immobilien- und Einzelhandelsbewertungen. In der vorliegenden Arbeit werden alle 34 offiziellen Quartiere Zürichs simultan bewertet, mit Score-Werten von 9 bis 92 Punkten.

### Slide 5 — Zielsetzung und Forschungsfrage  *(25 s)*

> Ziel ist ein automatisierter, reproduzierbarer Geo-Algorithmus zur Quantifizierung der Erreichbarkeit für jeden Punkt in Zürich. Die Forschungsfrage lautet: In welchen Quartieren Zürichs klaffen die grössten Lücken zwischen Wohnungsdichte und täglicher Infrastruktur? Unter Infrastruktur verstehen wir sechs Funktionen: Einkauf, Bildung, Gesundheit, Erholung, Gastronomie und ÖV.

### Slide 6 — Hypothesen  *(30 s)*

> Wir testen drei Hypothesen. Hypothese 1: Score und Median-Mietpreis korrelieren positiv. Getestet mit Pearson und Spearman über alle 34 Quartiere. Hypothese 1a als Robustness-Variante: Score korreliert negativ mit der Distanz zum Hauptbahnhof — methodisch sauberer Proxy ohne Markt-Confounder. Hypothese 2 untersucht den Wüsteneffekt, also Quartiere mit hoher Bevölkerungsdichte und gleichzeitig niedrigem Score. Getestet mit Schwellenwert-Logik auf BFS-STATPOP-Dichten. Damit übergebe ich an Andrea.

---

## Andrea — Methodik und Visualisierung (Slides 7–12)

### Slide 7 — Datenquellen  *(18 s)*

> Acht Datenquellen, alle aus Open Government oder Open Data — kein kommerzieller Datensatz. OSM via OSMnx liefert POIs und Walking-Graph, BFS STATPOP die Bevölkerungsdichte, Stadt Zürich Open Data die 34 Quartiergrenzen und den Mietpreis-Index, swisstopo die Hintergrundkarten und das 2-Meter-Höhenmodell SwissALTI3D.

### Slide 8 — Tools  *(25 s)*

> Im Tech-Stack ist PostGIS die zentrale Datenhaltung mit räumlichen SQL-Joins. OSMnx kombiniert Overpass-API-Zugriff und Walking-Graph-Aufbau. Scipy KDTree beschleunigt die Score-Berechnung um Faktor 400 — von sechs Minuten naiv auf unter eine Sekunde. NetworkX berechnet den topografischen Score per single-source-Dijkstra in 33 Sekunden für 8092 POIs. Statsmodels erstellt die multivariate Regression.

### Slide 9 — Score-Formel  *(35 s)*

> Der Score wird in zwei Stufen berechnet. Pro Kategorie und Hex-Zelle summieren wir alle POIs innerhalb von 1.2 Kilometern, gewichtet mit einem Huff-Distance-Decay: exponential von minus 1.5 mal Distanz durch d_max. Je weiter weg ein POI, desto geringer der Beitrag. Der Total-Score ergibt sich aus der gewichteten Summe der sechs Kategorien mal hundert — Einkauf 22 Prozent, Bildung, Gesundheit und ÖV je 18 Prozent, Erholung 14 Prozent, Gastronomie 10 Prozent. Gewichte angelehnt an Moreno, alle Parameter in config.py.

### Slide 10 — Pipeline  *(20 s)*

> Die Pipeline besteht aus neun Jupyter-Notebooks, davon zwei für die topografische Erweiterung. Sie deckt OSM-Daten, Walking-Graph mit SwissALTI3D-Höhen, PostGIS-Import, Hex-Gitter, Score-Berechnung, Hypothesen-Test und Tobler-Topo-Score ab. Vollständig reproduzierbar via docker compose und jupyter execute.

### Slide 11 — Score-Karte  *(30 s)*

> Die Score-Karte zeigt 744 Hex-Zellen über Zürich, je 200 Meter breit. Die Hex-Score-Range geht von 0 bis 94, Median 23, Mittelwert 30. Über 90 Punkte: Lindenhof, Werd, Rathaus, Langstrasse und City — der Innenstadtkern. Im Mittelfeld zwischen 40 und 70: Sihlfeld, Hard, Oerlikon und Enge. Unter 20: Leimbach, Witikon, Hirzenbach, Affoltern und Friesenberg — Peripherie und Hangwohnen. Die interaktive Folium-Karte liegt im Repository.

### Slide 12 — 3D-Skyline  *(18 s)*

> Zur Veranschaulichung wurde der Score in QGIS als 3D-Skyline visualisiert. Die Höhe einer Hex-Zelle entspricht dem Score multipliziert mit 30. Die QGIS-Visualisierung basiert auf einem direkten Layer-Zugriff auf PostGIS. Damit übergebe ich an Memis.

---

## Memis — Topografie, Ergebnisse, Diskussion und Schluss (Slides 13–20)

### Slide 13 — Topografische Erweiterung  *(35 s)*

> Eine konstante Gehgeschwindigkeit von 5 km/h passt für ebenes Gelände, aber Zürich hat ausgeprägte Hänge — Zürichberg, Hönggerberg, Käferberg, Üetliberg. Wir haben deshalb das SwissALTI3D-Höhenmodell mit 2-Meter-Auflösung in den Walking-Graph eingespeist und mit der Tobler-Hiking-Funktion steigungsabhängige Walking-Zeiten abgeleitet. Die grössten Verluste entstehen in Hangzonen: Oberstrass minus 14, Fluntern minus 11, Gewerbeschule minus 10 — letzteres zentral am Üetliberg-Hang — Alt-Wiedikon und Wipkingen je minus 8. Gewinner sind flache See-Quartiere: Mühlebach plus 8.5, Seefeld plus 6. Median-Delta minus 2.3, Range zwischen minus 33 und plus 19.

### Slide 14 — Hypothesen-Test  *(25 s)*

> Die drei Hypothesen quantitativ überprüft. Hypothese 1 wird unterstützt: Score und Median-Mietpreis korrelieren mit Spearman plus 0.56 bei p unter 10 hoch minus 3. Hypothese 1a hochsignifikant: ρ minus 0.81 bei p unter 10 hoch minus 8 — Distanz zum Hauptbahnhof ist ein noch stärkerer Prädiktor. Hypothese 2 quantitativ widerlegt: kein einziges der 34 Quartiere erfüllt die Wüsten-Schwellwerte. Zürich hat in diesem Sinn keine "food deserts".

### Slide 15 — Top- und Flop-Quartiere  *(18 s)*

> Auf Quartiersebene erreichen Lindenhof, Werd und Rathaus 92 Punkte, Langstrasse und City je 91. Am unteren Ende: Leimbach mit 9, Witikon mit 10 sowie Hirzenbach, Affoltern und Friesenberg mit je 19 Punkten. Spannweite über 80 Punkte innerhalb derselben Stadt.

### Slide 16 — Cluster-Typologie  *(25 s)*

> Ergänzend ein K-Means-Clustering mit k gleich 4 auf den sechs Kategorie-Erreichbarkeiten. Vier Typen resultieren: Typ A zentrale Mischung mit allem in Walking-Distanz, sieben Quartiere, Score 90. Typ B Mittelband mit ÖV-Anbindung, neun Quartiere, Score 59. Typ C Grünraum-dominiert — Saatlen, Seebach, Schwamendingen-Mitte, Friesenberg — Erholung 0.63, andere Kategorien tief. Typ D 14 periphere Wohnviertel, durchgehend unterdurchschnittlich.

### Slide 17 — Antwort auf die Forschungsfrage  *(20 s)*

> Die grössten Versorgungslücken liegen in der Peripherie: Leimbach, Witikon, Hirzenbach, Affoltern, Friesenberg — über 80 Punkte Abstand zum Zentrum. Drei Implikationen: für die Stadtplanung Versorgungs-Auflagen bei Entwicklungsgebieten, für Investoren preisliche Chancen bei Score unter 40, für den Einzelhandel klare Expansions-Targets.

### Slide 18 — Robustness Check  *(30 s)*

> Die multivariate OLS-Regression mit drei Prädiktoren — Distanz zum Hauptbahnhof, Höhe aus SwissALTI3D und POI-Dichte — erklärt 91 Prozent der Score-Varianz. Distanz bleibt nach Kontrolle hochsignifikant: β minus 9.52 bei p kleiner 10 hoch minus 6. Topografie ist signifikanter Co-Treiber. Die Sensitivitäts-Analyse über vier Gewichts-Szenarien zeigt Spearman-Rang über 0.98 in allen Varianten. Die Luftlinien-Approximation gegen Strassennetz-Distanz: Pearson 0.991.

### Slide 19 — Limitationen  *(20 s)*

> Vier Limitationen. OSM-Datenqualität: kleine, nicht erfasste Geschäfte fehlen. Tobler-Modell-Annahme: kalibriert auf Wandern, nicht auf städtisches Gehen mit Ampeln. Single-City-Befund: die H2-Falsifikation gilt für Zürich, nicht zwingend für andere Städte. Mietpreis-Confounder: Premium-Wohnlagen wie Hottingen oder Seefeld haben hohe Mieten trotz niedrigerem Score.

### Slide 20 — Ausblick  *(15 s)*

> Vier mögliche Erweiterungen: DEM-basierte Topografie mit ÖV-Anbindung, Echtzeit-Mobilitätsdaten via SBB GTFS, dynamisches Re-Scoring bei neuen POIs, und Erweiterung auf Winterthur und Basel. Das Repository steht unter github.com/sanirmem/zh15min. Damit endet unsere Präsentation.

---

## Q&A — vorbereitete Antworten

### „Warum genau diese sechs POI-Kategorien und Gewichte?"

> Die Kategorien folgen dem Moreno-Framework. Die Gewichte sind in src/zh15min/config.py parametrisiert. Eine Sensitivitäts-Analyse mit vier Szenarien zeigt Spearman-Rang über 0.98 — das Ranking ist methodisch robust gegen die Gewichtswahl.

### „Wieso 34 Quartiere und nicht eine feinere Aufteilung?"

> Es handelt sich um die offizielle Stadt-Zürich-Liste der statistischen Quartiere, bezogen über den WFS-Endpunkt von ogd.stadt-zuerich.ch. Die offizielle Geometrie ist mit Mietpreis-Index und STATPOP-Bevölkerungsdaten konsistent joinbar. Die räumliche Auflösung bleibt mit 744 Hex-Zellen intern feiner.

### „Warum Luftlinien-Distanz statt echter Walking-Distanz im Hauptscore?"

> Die Vereinfachung wurde empirisch validiert. Pearson-Koeffizient 0.991 zwischen Luftlinie und Strassengraph-Distanz, Median-Detour 1.20. Die Luftlinie erklärt 98.2 Prozent der Varianz. Performance-Gewinn rund Faktor 400 durch KDTree statt Dijkstra. Zusätzlich liegt mit Notebook 06b die topografisch korrekte Variante vor.

### „Wie wird mit Confoundern umgegangen?"

> Der Robustness Check auf Slide 18 adressiert das. Multivariate OLS-Regression mit Distanz zum Hauptbahnhof, Höhe aus SwissALTI3D-DEM und POI-Dichte erklärt 91 Prozent der Score-Varianz. Distanz bleibt nach Kontrolle hochsignifikant. Topografie ist signifikanter Co-Treiber. POI-Dichte ebenfalls hochsignifikant.

### „Ist die Tobler-Funktion für eine Stadt geeignet?"

> Tobler 1993 ist der etablierte Standard für topografisches Routing. Bei ebenem Gelände ergibt die Funktion rund 5.04 km/h, kompatibel mit der flachen Annahme. Extreme Steigungen über 50 Prozent werden geclippt, da meist Treppen-Artefakte. Die Limitation, dass die Funktion nicht speziell auf städtisches Gehen kalibriert ist, ist auf Slide 19 benannt.

### „Wie sind die Hypothesen-Ergebnisse vor Confoundern zu interpretieren?"

> Der bivariate Koeffizient von 0.56 für Hypothese 1 ist eine reine Korrelation. Die multivariate Kontrolle auf Slide 18 erklärt 91 Prozent der Varianz mit Distanz, Höhe und POI-Dichte. Mietpreise hängen jedoch nicht ausschliesslich am Score — Premium-Lagen wie Hottingen oder Seefeld zeigen hohe Mieten ohne hohe POI-Dichte.

### „Warum d_max gleich 1.2 km und nicht 1.25 km?"

> Geometrisch ergäbe sich 1.25 Kilometer. Wir runden konservativ auf 1.2. Die Sensitivität wurde geprüft: bei 1.0, 1.2 und 1.5 Kilometern bleibt der Spearman-Rang über 0.97.

### „Wieso werden ÖV-POIs gezählt statt Reisezeiten verwendet?"

> Die aktuelle Implementation zählt Haltestellen als ÖV-POIs — also physische Erreichbarkeit, nicht Reisezeit. Eine SBB-GTFS-Erweiterung ist als nächste Iteration auf Slide 20 vorgesehen.

---

## Aufnahme-Hinweise

- Tempo: bewusst etwas langsamer sprechen, aber ohne Pausen. Bei 9 bis 10 Minuten Gesamtlänge ist Verständlichkeit wichtiger als Tempo.
- Mikrofon: Headset oder externes Mikrofon. Kurzer Pegel-Test vor der Aufnahme.
- Folien: alle Visualisierungen sind als statische Screenshots eingebettet. Im Video wird nichts live geöffnet.
- Aufnahme-Strategie: pro Person ein separater Take, im Schnitt zusammenführen.
- Stoppuhr-Plan: Ioannis ca. 2:00, Andrea ca. 2:30, Memis ca. 3:00 — Gesamtlänge ca. 9:30 inkl. Schnitten.
- Übergaben: Ioannis schliesst Slide 6 mit "Damit übergebe ich an Andrea." Andrea schliesst Slide 12 mit "Damit übergebe ich an Memis." Memis schliesst Slide 20 mit "Damit endet unsere Präsentation."
- Bei Versprechen: durchziehen, nicht neu ansetzen.

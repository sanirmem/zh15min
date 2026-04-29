# Sprecher-Notizen für die Videopräsentation

> 9 Minuten total (3 Personen × 3 Min). Jede Slide hat einen Zielsatz und ein „Don't forget".

---

## Person A — Einleitung (Slides 1–6, ca. 3 Min)

### Slide 1 — Titel  *(15 s)*
> „Hallo, wir sind Gruppe X mit dem Projekt The 15-Minute City Intelligence — ein Geo-Algorithmus, der die Erreichbarkeit von Funktionen des täglichen Lebens für die ganze Stadt Zürich misst und Versorgungslücken aufzeigt."

### Slide 2 — Inhaltsverzeichnis  *(10 s)*
> „Ich werde euch durch Hintergrund und Hypothesen führen. Person B übernimmt die Methodik, Person C die Ergebnisse."

### Slide 3 — Workflow-Übersicht  *(20 s)*
> Visuelle Roadmap. Wichtig: „Sechs Schritte, alle reproduzierbar — wir kommen gleich zu jedem."

### Slide 4 — Hintergrund & Motivation  *(35 s)*
> Carlos Moreno hat 2021 das 15-Minuten-Stadt-Konzept geprägt. Heute über 90 % der Firmen sehen Location Intelligence als kritisch. **UBS-Studie: +11 % Mietpreis-Premium für sehr gut erreichbare Lagen.** Wir wollten das messbar machen.

### Slide 5 — Zielsetzung & Forschungsfrage  *(40 s)*
> **Zielsetzung links** vorlesen, dann betont:
> „Die Forschungsfrage lautet: *In welchen Quartieren Zürichs klaffen die grössten Lücken zwischen Wohnungsdichte und täglicher Infrastruktur?*"

### Slide 6 — Hypothesen  *(45 s)*
> H1: Score korreliert negativ mit der Distanz zum Hauptbahnhof — Zentralität schlägt sich in Erreichbarkeit nieder. **Test:** Pearson + Spearman auf 44 Quartiere.
> H2: Peripherie-Effekt — die schwächsten Quartiere liegen alle am Stadtrand. **Test:** Identifikation der Flop-Quartiere und qualitative Lage-Analyse.
> *(Hinweis fürs Storytelling: Wir wollten ursprünglich H1 mit Mietpreisen testen, aber der Stadt-Zürich-Datensatz war unter der dokumentierten URL nicht erreichbar. Statt H1 zu kippen, haben wir sie auf einen testbaren Proxy — Distanz zum HB — umgestellt. Das erwähnen wir auch unter Limitationen.)*
> Übergabe → Person B.

---

## Person B — Methodik (Slides 7–10, ca. 3 Min)

### Slide 7 — Datenquellen  *(30 s)*
> Sieben Quellen, alle frei oder Open-Government. **Kein einziger kommerzieller Datensatz** — kompletter Open-Source-Stack.

### Slide 8 — Tools  *(40 s)*
> Highlights: **PostGIS** als Single Source of Truth wie im Kurs. **scipy KDTree** als Performance-Trick: Score-Berechnung von 6 Minuten auf 10 Sekunden.

### Slide 9 — Score-Formel  *(60 s)*
> Erklären: „A_c ist die Erreichbarkeit für Kategorie c — wir summieren über alle POIs innerhalb der 15-Minuten-Sphäre, gewichtet mit einem **Distance-Decay** β. Je weiter weg, desto weniger Beitrag."
> „Den Total-Score erhalten wir durch eine gewichtete Summe der sechs Komponenten unten in den farbigen Boxen."

### Slide 10 — Pipeline  *(40 s)*
> Sieben Notebooks, jede Stufe reproduzierbar. „**Ein `docker compose up -d` und `jupyter execute` reichen, um den ganzen Score zu reproduzieren.**"
> Übergabe → Person C.

---

## Person C — Ergebnisse & Schluss (Slides 11–16, ca. 3 Min)

### Slide 11 — Score-Karte  *(40 s)*
> *(Live-Demo: Folium-Map öffnen statt der statischen Slide-Karte)* „Hier seht ihr Zürich mit 744 Hex-Zellen. Rot = niedrig, Grün = hoch. Die Range geht von 8 bis 93."
> Zeigt drei Stellen mit dem Cursor: City (grün, ~93), Wiedikon (gelb, mittel), Leimbach (rot, ~8).

### Slide 12 — Hypothesen-Test  *(40 s)*
> **H1 hochsignifikant bestätigt mit Spearman ρ = −0.64 bei p < 10⁻⁵** und n = 44 — Zentralität ist der dominante Treiber des Scores.
> **H2 qualitativ bestätigt:** fünf Quartiere mit Score < 20 — alle in der Peripherie. Eine quantitative Validierung über Bevölkerungsdichte (STATPOP) steht offen.

### Slide 13 — Top/Flop  *(25 s)*
> „Top: City, Langstrasse, Altstadt — alle in der kompakten Innenstadt mit Score über 88. Flop: **Leimbach, Witikon, Hirzenbach** — periphere Wohnviertel mit Score zwischen 8 und 16. Über 70 Score-Punkte Differenz innerhalb derselben Stadt."

### Slide 14 — Antwort auf Forschungsfrage  *(35 s)*
> „Die grössten Lücken liegen in der Peripherie — Leimbach, Witikon, Hirzenbach, Hottingen, Friesenberg. Die Korrelation Score × Distanz HB von ρ = −0.64 ist eindeutig. Drei Implikationen: für die Stadtplanung Versorgungs-Auflagen in Entwicklungsgebieten, für Investoren preisliche Chancen mit Vermarktungsrisiko, für den Einzelhandel klare Expansions-Targets."

### Slide 15 — Limitationen  *(30 s)*
> Vier Limitationen klar benennen. Wichtige Ehrlichkeiten: **Mietpreis-Datensatz war unter dokumentierter URL nicht erreichbar (HTTP 404), deshalb wurde H1 über Distanz zum HB validiert. STATPOP-Bevölkerungsraster ist nur per manuellem Download verfügbar — Quantifizierung der Bevölkerungsdichte je Quartier steht aus.**

### Slide 16 — Ausblick & Dank  *(20 s)*
> „Im Ausblick: Echtzeit-Mobilitätsdaten, Sentiment-Scores aus Reviews. Vielen Dank — wir freuen uns auf eure Fragen."

---

## Tipps für die Aufnahme

- Sprecht **etwas langsamer** als ihr denkt — bei 9 Minuten lieber 15 % unter Tempo.
- Wenn die Live-Folium-Demo (Slide 11) zickt, springt nahtlos auf die statische Karte zurück.
- Microphon-Test mit Headset, nicht Laptop-Mic.
- **Ein Take pro Person**, dann alles in einem Cut zusammenschneiden — das wirkt zusammenhängender als ein gemeinsamer Take, in dem ihr euch unterbrecht.

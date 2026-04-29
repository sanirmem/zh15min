# QGIS-Projekt — Setup-Anleitung

> Ziel: Eine `.qgz`-Datei `zh15min.qgz`, die unsere PostGIS-Layer + den 15-Min-Score visualisiert, inkl. **3D-Map** mit Score als Höhe und einem **Print-Layout** für die Slides.

Da ein QGIS-Projekt programmatisch nur sehr unbequem zu erzeugen ist, hier eine 5-Minuten-Klick-Anleitung. Das Resultat speichert ihr direkt in diesen Ordner als `qgis/zh15min.qgz`.

---

## Schritt 1 — QGIS öffnen, neues Projekt anlegen

1. QGIS 3.40 LTR starten.
2. **Projekt → Neu**.
3. **Projekt → Eigenschaften → CRS** → `EPSG:2056` (CH1903+/LV95) setzen.

## Schritt 2 — PostGIS-Verbindung anlegen

1. Browser-Panel → Rechtsklick auf **PostgreSQL** → **Neue Verbindung**.
2. Werte:
   - Name: `zh15min`
   - Host: `localhost`
   - Port: `5432`
   - Datenbank: `zh15min`
   - Benutzername: `postgres`
   - Passwort: `postgres` (aus `.env`)
3. **Verbindung testen** → **OK**.

## Schritt 3 — Layer hinzufügen

Aus dem Browser-Panel → `PostgreSQL → zh15min → public/zh15min` per Drag & Drop in die Layer-Ansicht ziehen:

- `zh15min.boundary` — Stadtgrenze
- `zh15min.quartiere` — 34 Quartier-Polygone
- `zh15min.score` — Hex-Gitter mit Score
- `zh15min.pois` — alle POI-Punkte
- (optional) `public.planet_osm_point` — falls `osm2pgsql` ausgeführt wurde

## Schritt 4 — Score-Symbologie

Für Layer `zh15min.score`:

1. Doppelklick auf den Layer → **Symbolisierung**.
2. **Abgestuft (Graduated)**.
3. Spalte: `score`.
4. Methode: **Quantile (Equal Count)**, 7 Klassen.
5. Farbverlauf: **RdYlGn** (oben in der Liste).
6. Linienstärke: 0 (keine Umrisse).
7. Deckkraft: 75 %.

Für Layer `zh15min.quartiere`:

1. **Symbolisierung → Einzelsymbol**, Füllung `none`, Linien-Farbe `weiss`, Linienstärke `0.7 mm`.
2. **Beschriftung** → Aktivieren mit Spalte `name` (oder analoger Spalte).

Für Layer `zh15min.pois`:

1. **Kategorisiert**, Spalte `category`.
2. Klassifizieren → Symbolgrösse 1.5 mm, eigene Farbe je Kategorie.
3. (Layer initial **deaktivieren** — wird nur on-demand für die Demo eingeblendet.)

## Schritt 5 — 3D-Map (Score als Höhe)

1. **Ansicht → 3D-Karten-Ansichten → Neue 3D-Karten-Ansicht**.
2. Im 3D-Fenster: **Konfigurieren → Geländekarte** auf `flat` lassen.
3. Layer `zh15min.score` auswählen → **Eigenschaften → 3D-Ansicht**.
4. **3D-Renderer aktivieren**, Typ: `Polygon`.
5. **Höhe**: `score * 5` (so wird ein Score von 80 zu 400 m Pseudo-Höhe).
6. **Symbolisierung**: dieselbe RdYlGn-Datenrampe.
7. Speichern.

Für die Videopräsentation (animierter Kameraflug): 3D-Fenster → **Animation aktivieren** → Keyframes setzen.

## Schritt 6 — Print-Layout für die Slides

1. **Projekt → Neues Layout** → Name: `Score_Karte`.
2. Karte einfügen, Massstab 1:30 000.
3. Legende, Massstabsleiste, Nordpfeil, Quellen-Hinweis: *„© OpenStreetMap-Mitwirkende · Stadt Zürich Open Data · BFS STATPOP 2023"*.
4. **Layout → Als Bild exportieren** → `reports/figures/qgis_score_layout.png` (300 dpi).

## Schritt 7 — Speichern

**Projekt → Speichern unter** → `qgis/zh15min.qgz`.

Die `.qgz` enthält **nur die Verbindungs-Information**, nicht die Daten — d.h. das Projekt ist klein (~1 MB), aber jeder, der es öffnet, braucht eine PostGIS-Datenbank mit unseren Tabellen.

---

## Live-Demo-Idee (für die Präsentation)

> *„Was passiert, wenn die Stadt einen Supermarkt in Schwamendingen plant?"*

1. POI-Layer auf editierbar setzen (Toolbar-Stift).
2. Neuen Punkt hinzufügen, Attribut `category = 'einkauf'`.
3. Im Notebook 05 die Score-Berechnung erneut auslösen.
4. In QGIS: **Layer → Aktualisieren** — der Score in der Umgebung springt sichtbar.

Dieser Effekt — *ein neuer POI verbessert den Score eines ganzen Viertels live* — ist das Kernstück der Präsentation und wertet die Note unter „Medieneinsatz & Demonstrationen" deutlich auf.

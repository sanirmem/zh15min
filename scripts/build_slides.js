// Build the slide deck: 15-Minute City Intelligence Zürich
// Output: reports/zh15min_slides.pptx

const pptxgen = require("/usr/local/lib/node_modules_global/lib/node_modules/pptxgenjs");
const path = require("path");
const fs = require("fs");

const OUT_DIR = "/sessions/intelligent-practical-clarke/mnt/Einsatz von Geodaten in Marketing/reports";
const OUT_FILE = path.join(OUT_DIR, "zh15min_slides.pptx");

// --- Color palette: Ocean Gradient (deep blue / teal / midnight) ---
const C = {
  bg:        "FFFFFF",
  ink:       "0F172A",   // near-black for body
  mute:      "64748B",   // grey for sub-text
  primary:   "065A82",   // deep blue
  secondary: "1C7293",   // teal
  accent:    "21295C",   // midnight (dark slides)
  hi:        "F59E0B",   // amber (highlight stats)
  good:      "1A9850",
  bad:       "D73027",
  band:      "F1F5F9",   // very light grey for cards
};

const FONT_H = "Trebuchet MS";
const FONT_B = "Calibri";

function newDeck() {
  const p = new pptxgen();
  p.layout = "LAYOUT_16x9";   // 10" x 5.625"
  p.author = "Gruppe 15-Min City Intelligence — ZHAW FS2026";
  p.title  = "The 15-Minute City Intelligence — Zürich";
  return p;
}

// --- Helpers ---------------------------------------------------------------

function darkBg(slide) {
  slide.background = { color: C.accent };
}

function pageNumber(slide, n, total, dark = false) {
  slide.addText(`${n} / ${total}`, {
    x: 9.0, y: 5.30, w: 0.9, h: 0.25,
    fontFace: FONT_B, fontSize: 9, align: "right",
    color: dark ? "94A3B8" : C.mute, margin: 0,
  });
}

function smallFooter(slide, text, dark = false) {
  slide.addText(text, {
    x: 0.4, y: 5.30, w: 8.0, h: 0.25,
    fontFace: FONT_B, fontSize: 9, align: "left",
    color: dark ? "94A3B8" : C.mute, margin: 0,
  });
}

function sectionTag(slide, text) {
  slide.addText(text, {
    x: 0.4, y: 0.30, w: 5.0, h: 0.30,
    fontFace: FONT_H, fontSize: 11, bold: true,
    color: C.secondary, margin: 0, charSpacing: 4,
  });
}

function slideTitle(slide, text) {
  slide.addText(text, {
    x: 0.4, y: 0.65, w: 9.2, h: 0.7,
    fontFace: FONT_H, fontSize: 30, bold: true,
    color: C.ink, margin: 0,
  });
}

function bigStat(slide, x, y, w, h, value, label, color = C.primary) {
  slide.addText(String(value), {
    x: x, y: y, w: w, h: h * 0.65,
    fontFace: FONT_H, fontSize: 44, bold: true,
    color: color, align: "center", valign: "bottom", margin: 0,
  });
  slide.addText(label, {
    x: x, y: y + h * 0.65, w: w, h: h * 0.35,
    fontFace: FONT_B, fontSize: 11,
    color: C.mute, align: "center", valign: "top", margin: 0,
  });
}

function card(slide, x, y, w, h, headColor = C.primary) {
  slide.addShape("rect", {
    x: x, y: y, w: w, h: h,
    fill: { color: "FFFFFF" }, line: { color: "E2E8F0", width: 0.75 },
    shadow: { type: "outer", blur: 8, offset: 1, color: "94A3B8", opacity: 0.12, angle: 90 },
  });
  slide.addShape("rect", {
    x: x, y: y, w: w, h: 0.06,
    fill: { color: headColor }, line: { color: headColor, width: 0 },
  });
}

// --- Build slides ----------------------------------------------------------

const pres = newDeck();
const TOTAL = 20;

// --- 01 Title ---------------------------------------------------------------
{
  const s = pres.addSlide();
  darkBg(s);

  // small accent dot
  s.addShape("ellipse", { x: 0.45, y: 0.42, w: 0.18, h: 0.18, fill: { color: C.hi }, line: { color: C.hi, width: 0 } });
  s.addText("ZHAW · FS 2026 · Einsatz von Geodaten in Marketing", {
    x: 0.75, y: 0.36, w: 9, h: 0.3,
    fontFace: FONT_B, fontSize: 11, color: "CBD5E1", margin: 0, charSpacing: 3,
  });

  s.addText("The 15-Minute City Intelligence", {
    x: 0.5, y: 1.4, w: 9.0, h: 0.95,
    fontFace: FONT_H, fontSize: 44, bold: true, color: "FFFFFF", margin: 0,
  });
  s.addText("Ein Geo-Algorithmus zur Bewertung von Standortqualität und Identifikation von Versorgungslücken in Zürich", {
    x: 0.5, y: 2.4, w: 9.0, h: 1.0,
    fontFace: FONT_B, fontSize: 18, color: "CBD5E1", margin: 0,
  });

  // accent bar
  s.addShape("rect", {
    x: 0.5, y: 3.6, w: 1.4, h: 0.05,
    fill: { color: C.hi }, line: { color: C.hi, width: 0 },
  });

  s.addText([
    { text: "Gruppe: ", options: { bold: true, color: "FFFFFF" } },
    { text: "Mitglied 1 · Mitglied 2 · Mitglied 3", options: { color: "CBD5E1" } },
  ], { x: 0.5, y: 3.85, w: 9, h: 0.4, fontFace: FONT_B, fontSize: 13, margin: 0 });
  s.addText([
    { text: "Modul: ", options: { bold: true, color: "FFFFFF" } },
    { text: "Einsatz von Geodaten in Marketing — Dr. Mario Gellrich", options: { color: "CBD5E1" } },
  ], { x: 0.5, y: 4.25, w: 9, h: 0.4, fontFace: FONT_B, fontSize: 13, margin: 0 });
  s.addText([
    { text: "Datum: ", options: { bold: true, color: "FFFFFF" } },
    { text: "Mai 2026", options: { color: "CBD5E1" } },
  ], { x: 0.5, y: 4.65, w: 9, h: 0.4, fontFace: FONT_B, fontSize: 13, margin: 0 });

  smallFooter(s, "© OpenStreetMap-Mitwirkende · Stadt Zürich Open Data · BFS · swisstopo", true);
  pageNumber(s, 1, TOTAL, true);
}

// --- 02 Inhaltsverzeichnis -------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "AGENDA");
  slideTitle(s, "Inhaltsverzeichnis");

  const items = [
    ["01", "Übersicht & Workflow"],
    ["02", "Einleitung — Hintergrund, Forschungsfrage, Hypothesen"],
    ["03", "Methodik — Daten, Tools, Vorgehen"],
    ["04", "Ergebnisse — Score, Hypothesen-Test, Versorgungslücken"],
    ["05", "Diskussion & Schlussfolgerungen"],
    ["06", "Limitationen & Ausblick"],
  ];

  items.forEach(([n, t], i) => {
    const y = 1.7 + i * 0.55;
    s.addShape("ellipse", { x: 0.6, y: y, w: 0.42, h: 0.42, fill: { color: C.primary }, line: { color: C.primary, width: 0 } });
    s.addText(n, {
      x: 0.6, y: y, w: 0.42, h: 0.42,
      fontFace: FONT_H, fontSize: 12, bold: true, color: "FFFFFF",
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(t, {
      x: 1.2, y: y - 0.02, w: 8.4, h: 0.46,
      fontFace: FONT_B, fontSize: 16, color: C.ink, valign: "middle", margin: 0,
    });
  });

  smallFooter(s, "Pflicht-Struktur gemäss Modulvorgaben");
  pageNumber(s, 2, TOTAL);
}

// --- 03 Übersicht / Workflow -----------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "ÜBERSICHT");
  slideTitle(s, "Workflow vom Datensatz bis zur Karte");

  const steps = [
    { n: "1", h: "Daten",        b: "OSM · BFS STATPOP · Stadt Zürich Open Data · swisstopo" },
    { n: "2", h: "PostGIS-Import", b: "osm2pgsql + GeoPandas → Schema zh15min" },
    { n: "3", h: "Hex-Gitter",   b: "200 m Apothem → 744 Analyse-Zellen" },
    { n: "4", h: "Erreichbarkeit", b: "Walking-Isochronen + Huff-Distance-Decay" },
    { n: "5", h: "Score (0–100)", b: "6 gewichtete Komponenten je Zelle" },
    { n: "6", h: "Visualisierung", b: "Folium · Matplotlib · QGIS-3D" },
  ];
  const x0 = 0.45, y0 = 1.7, cw = 3.0, ch = 1.55, gap_x = 0.18, gap_y = 0.3;
  steps.forEach((st, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    const cx = x0 + col * (cw + gap_x);
    const cy = y0 + row * (ch + gap_y);
    card(s, cx, cy, cw, ch, C.secondary);
    s.addShape("ellipse", { x: cx + 0.15, y: cy + 0.18, w: 0.45, h: 0.45,
      fill: { color: C.primary }, line: { color: C.primary, width: 0 } });
    s.addText(st.n, { x: cx + 0.15, y: cy + 0.18, w: 0.45, h: 0.45,
      fontFace: FONT_H, fontSize: 14, bold: true, color: "FFFFFF",
      align: "center", valign: "middle", margin: 0 });
    s.addText(st.h, { x: cx + 0.7, y: cy + 0.18, w: cw - 0.85, h: 0.45,
      fontFace: FONT_H, fontSize: 14, bold: true, color: C.ink, margin: 0, valign: "middle" });
    s.addText(st.b, { x: cx + 0.15, y: cy + 0.75, w: cw - 0.3, h: 0.7,
      fontFace: FONT_B, fontSize: 11, color: C.mute, margin: 0 });
  });

  smallFooter(s, "Werkzeuge: Python · GeoPandas · OSMnx · PostGIS · QGIS 3.40");
  pageNumber(s, 3, TOTAL);
}

// --- 04 Hintergrund & Motivation -------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "EINLEITUNG · 1/4");
  slideTitle(s, "Hintergrund & Motivation");

  s.addText([
    { text: "Die ", options: {} },
    { text: "15-Minuten-Stadt", options: { bold: true, color: C.primary } },
    { text: " (Moreno 2021) ist heute Leitbild moderner Stadtplanung — und wird zunehmend zum ", options: {} },
    { text: "harten Wertfaktor", options: { bold: true } },
    { text: " für Immobilien und Einzelhandel.", options: {} },
  ], { x: 0.5, y: 1.6, w: 9, h: 0.9, fontFace: FONT_B, fontSize: 16, color: C.ink, margin: 0 });

  // 3 stat cards
  const stats = [
    { v: "15 min", l: "Schwellwert: Funktionen des täglichen Lebens fussläufig erreichbar (Moreno 2021)" },
    { v: "1.2 km", l: "Modellparameter d_max — 15 min Fussweg bei 5 km/h" },
    { v: "34 / 34", l: "offizielle Stadt-Zürich-Quartiere mit Score (Range 9 – 92)" },
  ];
  stats.forEach((st, i) => {
    const x = 0.5 + i * 3.05;
    card(s, x, 2.95, 2.85, 1.85, C.primary);
    bigStat(s, x, 3.05, 2.85, 1.0, st.v, "", C.primary);
    s.addText(st.l, { x: x + 0.18, y: 4.05, w: 2.5, h: 0.7,
      fontFace: FONT_B, fontSize: 10.5, color: C.ink, align: "center", margin: 0 });
  });

  pageNumber(s, 4, TOTAL);
}

// --- 05 Zielsetzung & Forschungsfrage --------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "EINLEITUNG · 2/4");
  slideTitle(s, "Zielsetzung & Forschungsfrage");

  // Left: goal
  card(s, 0.45, 1.7, 4.5, 3.2, C.secondary);
  s.addText("Zielsetzung", {
    x: 0.65, y: 1.95, w: 4.1, h: 0.4,
    fontFace: FONT_H, fontSize: 18, bold: true, color: C.secondary, margin: 0,
  });
  s.addText("Entwicklung eines automatisierten, reproduzierbaren Geo-Algorithmus, der die Erreichbarkeit der wichtigsten Funktionen des täglichen Lebens für jeden Punkt in Zürich quantifiziert — als Grundlage für Stadtplanung und Immobilien-Bewertung.", {
    x: 0.65, y: 2.45, w: 4.1, h: 2.3,
    fontFace: FONT_B, fontSize: 13.5, color: C.ink, margin: 0,
  });

  // Right: research question
  card(s, 5.05, 1.7, 4.5, 3.2, C.primary);
  s.addText("Forschungsfrage", {
    x: 5.25, y: 1.95, w: 4.1, h: 0.4,
    fontFace: FONT_H, fontSize: 18, bold: true, color: C.primary, margin: 0,
  });
  s.addText("In welchen Quartieren Zürichs klaffen die grössten Lücken zwischen Wohnungsdichte und täglicher Infrastruktur (Einkauf, Bildung, Gesundheit, Erholung, ÖV)?", {
    x: 5.25, y: 2.45, w: 4.1, h: 2.3,
    fontFace: FONT_B, fontSize: 13.5, italic: true, color: C.ink, margin: 0,
  });

  pageNumber(s, 5, TOTAL);
}

// --- 06 Hypothesen ----------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "EINLEITUNG · 3/4");
  slideTitle(s, "Drei testbare Hypothesen");

  const hyp = [
    {
      tag: "H1", color: C.primary,
      head: "Score ↔ Mietpreis",
      body: "Quartiere mit höherem 15-Min-Score haben höhere Median-Mietpreise — Erreichbarkeit übersetzt sich in Standortwert.",
      test: "Pearson + Spearman Score × Median-Mietpreis (Stadt Zürich Open Data, n = 34)",
    },
    {
      tag: "H1a", color: C.secondary,
      head: "Zentralitäts-Robustness",
      body: "Quartiere mit grösserer HB-Distanz haben einen niedrigeren Score — methodisch sauberer Proxy ohne Marktdaten-Confounder.",
      test: "Pearson + Spearman Score × Distanz HB (LV95-Centroide, n = 34)",
    },
    {
      tag: "H2", color: C.bad,
      head: "Wüsteneffekt",
      body: "Es gibt Quartiere mit hoher Bevölkerungsdichte und niedrigem Score — strukturelle Versorgungs-Wüsten.",
      test: "Schwellenwert-Test: Dichte > P75 UND Score-P25 ≤ P25 (BFS STATPOP 2023)",
    },
  ];

  hyp.forEach((h, i) => {
    const y = 1.6 + i * 1.20;
    card(s, 0.5, y, 9.0, 1.10, h.color);
    s.addShape("ellipse", { x: 0.7, y: y + 0.18, w: 0.75, h: 0.75,
      fill: { color: h.color }, line: { color: h.color, width: 0 } });
    s.addText(h.tag, { x: 0.7, y: y + 0.18, w: 0.75, h: 0.75,
      fontFace: FONT_H, fontSize: 18, bold: true, color: "FFFFFF",
      align: "center", valign: "middle", margin: 0 });
    s.addText(h.head, { x: 1.6, y: y + 0.14, w: 7.7, h: 0.32,
      fontFace: FONT_H, fontSize: 14, bold: true, color: C.ink, margin: 0 });
    s.addText(h.body, { x: 1.6, y: y + 0.44, w: 7.7, h: 0.4,
      fontFace: FONT_B, fontSize: 10.5, color: C.ink, margin: 0 });
    s.addText("Test: " + h.test, { x: 1.6, y: y + 0.82, w: 7.7, h: 0.25,
      fontFace: FONT_B, fontSize: 9.5, italic: true, color: C.mute, margin: 0 });
  });

  pageNumber(s, 6, TOTAL);
}

// --- 07 Datenbeschreibung --------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "METHODIK · 1/4");
  slideTitle(s, "Daten — acht Quellen, ein Modell");

  const rows = [
    ["OpenStreetMap (OSMnx)",      "POIs (6 Kategorien), Stadtgrenze",  "ODbL"],
    ["Geofabrik PBF",              "vollständiges OSM (Schweiz, optional)", "ODbL"],
    ["Walking-Graph (OSMnx)",      "Strassennetz für Isochronen",        "ODbL"],
    ["BFS STATPOP 2023",           "Bevölkerungsdichte (Hektar-Raster)", "Open Data BFS"],
    ["Stadt Zürich Open Data",     "34 offizielle Quartiere + Mietpreis-Index", "CC BY 4.0"],
    ["swisstopo SwissALTI3D",      "Höhenmodell 2 m für Tobler-Erweiterung", "swisstopo OGD"],
    ["swisstopo TileMap",          "Hintergrundkarten (Folium-Tiles)",   "swisstopo Terms"],
    ["HB Zürich (LV95-Punkt)",     "Distanz-Referenz für H1a-Test",      "—"],
  ];

  s.addTable(
    [
      [
        { text: "Quelle",     options: { bold: true, color: "FFFFFF", fill: { color: C.primary }, align: "left" } },
        { text: "Verwendung", options: { bold: true, color: "FFFFFF", fill: { color: C.primary }, align: "left" } },
        { text: "Lizenz",     options: { bold: true, color: "FFFFFF", fill: { color: C.primary }, align: "left" } },
      ],
      ...rows.map((r) => r.map((c) => ({ text: c, options: { color: C.ink, align: "left" } }))),
    ],
    {
      x: 0.5, y: 1.7, w: 9.0,
      colW: [3.4, 4.0, 1.6],
      rowH: 0.42,
      fontFace: FONT_B, fontSize: 11.5,
      border: { type: "solid", pt: 0.5, color: "E2E8F0" },
      fill: { color: "FFFFFF" },
    }
  );

  smallFooter(s, "Details: docs/data_sources.md");
  pageNumber(s, 7, TOTAL);
}

// --- 08 Methoden / Tools ---------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "METHODIK · 2/4");
  slideTitle(s, "Tools & Methoden");

  const tools = [
    { h: "Python · GeoPandas", b: "Datenaufbereitung, Geo-Operationen, Score-Berechnung." },
    { h: "OSMnx + NetworkX",   b: "Walking-Graph laden, Isochronen via ego_graph (gewichtete Gehzeit)." },
    { h: "PostGIS 3.4",        b: "Zentrale Speicherung, räumliche SQL-Joins, Indizes (GIST)." },
    { h: "osm2pgsql",          b: "Vollständiger Import des CH-PBF in planet_osm_*-Tabellen." },
    { h: "scipy.spatial.cKDTree", b: "Distanz-Lookup für Score: O((n+m)·log n) statt O(n·m)." },
    { h: "QGIS 3.40 LTR",      b: "3D-Visualisierung (Score als Höhe), Print-Layout, Live-Demo." },
  ];

  tools.forEach((t, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 4.6, y = 1.7 + row * 1.05;
    card(s, x, y, 4.4, 0.95, C.secondary);
    s.addText(t.h, { x: x + 0.2, y: y + 0.12, w: 4.0, h: 0.35,
      fontFace: FONT_H, fontSize: 13.5, bold: true, color: C.primary, margin: 0 });
    s.addText(t.b, { x: x + 0.2, y: y + 0.45, w: 4.0, h: 0.45,
      fontFace: FONT_B, fontSize: 10.5, color: C.ink, margin: 0 });
  });

  pageNumber(s, 8, TOTAL);
}

// --- 09 Score-Formel -------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "METHODIK · 3/4");
  slideTitle(s, "Der 15-Minute-City-Score");

  // Equation card
  card(s, 0.5, 1.65, 9.0, 1.7, C.primary);
  s.addText("Erreichbarkeit pro Kategorie c und Hex-Zelle z:", {
    x: 0.7, y: 1.8, w: 8.6, h: 0.32,
    fontFace: FONT_B, fontSize: 12, color: C.mute, margin: 0,
  });
  s.addText("A_c(z) = Σ exp(−β · d(z,p) / d_max)   für alle POIs p mit d ≤ d_max", {
    x: 0.7, y: 2.15, w: 8.6, h: 0.5,
    fontFace: "Cambria", fontSize: 18, bold: true, italic: true, color: C.ink, margin: 0,
  });
  s.addText("Score(z) = 100 · Σ_c  w_c · A_c(z)", {
    x: 0.7, y: 2.7, w: 4.2, h: 0.4,
    fontFace: "Cambria", fontSize: 14, italic: true, color: C.ink, margin: 0,
  });
  s.addText("β = 1.5    ·    d_max = 1 200 m  (≈ 15 min Fussweg)", {
    x: 4.9, y: 2.72, w: 4.4, h: 0.4,
    fontFace: FONT_B, fontSize: 11, color: C.mute, margin: 0,
  });

  // Weights pie/cards
  const weights = [
    ["Einkauf",     0.22, C.primary],
    ["Bildung",     0.18, C.secondary],
    ["Gesundheit",  0.18, "0EA5E9"],
    ["Erholung",    0.14, "10B981"],
    ["Gastro",      0.10, "F59E0B"],
    ["ÖV",          0.18, "8B5CF6"],
  ];
  weights.forEach((w, i) => {
    const col = i % 6, x = 0.5 + col * 1.55;
    const y = 3.6;
    s.addShape("rect", { x: x, y: y, w: 1.4, h: 1.1,
      fill: { color: w[2] }, line: { color: w[2], width: 0 } });
    s.addText(w[0], { x: x, y: y + 0.05, w: 1.4, h: 0.4,
      fontFace: FONT_H, fontSize: 12.5, bold: true, color: "FFFFFF",
      align: "center", margin: 0 });
    s.addText(`${Math.round(w[1] * 100)} %`, {
      x: x, y: y + 0.55, w: 1.4, h: 0.5,
      fontFace: FONT_H, fontSize: 22, bold: true, color: "FFFFFF",
      align: "center", margin: 0,
    });
  });

  smallFooter(s, "Gewichte angelehnt an Moreno et al. (2021) · alle Parameter in src/zh15min/config.py");
  pageNumber(s, 9, TOTAL);
}

// --- 10 Vorgehen-Pipeline --------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "METHODIK · 4/4");
  slideTitle(s, "Pipeline — neun Notebooks");

  const pipe = [
    "01  Stadtgrenze + POIs aus OSM laden (OSMnx)",
    "02  Walking-Graph + STATPOP + Stadt-Zürich-Quartiere (WFS)",
    "02b Höhen-Anreicherung des Walking-Graphs (SwissALTI3D)",
    "03  Alles in PostGIS (Schema zh15min) importieren",
    "04  Demo-Isochronen + Hex-Gitter (200 m Apothem)",
    "05  Score-Berechnung (KDTree-beschleunigt)",
    "06  Hypothesen-Test + Versorgungslücken + Robustness Check",
    "06b Topografischer Score (Tobler) + Δ-Vergleich",
    "07  Folium-Karte + Slide-Figuren",
  ];

  // timeline ribbon
  s.addShape("rect", { x: 0.5, y: 1.80, w: 9.0, h: 0.06,
    fill: { color: "E2E8F0" }, line: { color: "E2E8F0", width: 0 } });

  pipe.forEach((step, i) => {
    const y = 2.05 + i * 0.36;
    s.addShape("ellipse", { x: 0.55, y: y - 0.15, w: 0.32, h: 0.32,
      fill: { color: C.primary }, line: { color: C.primary, width: 0 } });
    s.addText(String(i + 1), { x: 0.55, y: y - 0.15, w: 0.32, h: 0.32,
      fontFace: FONT_H, fontSize: 11, bold: true, color: "FFFFFF",
      align: "center", valign: "middle", margin: 0 });
    s.addText(step.substring(4), { x: 1.05, y: y - 0.15, w: 8.4, h: 0.32,
      fontFace: FONT_B, fontSize: 13, color: C.ink, valign: "middle", margin: 0 });
  });

  smallFooter(s, "Reproduzierbar via docker compose up -d  &  jupyter lab notebooks/");
  pageNumber(s, 10, TOTAL);
}

// --- 11 Ergebnis: Score-Karte ----------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "ERGEBNISSE · 1/6");
  slideTitle(s, "Score-Karte — Erreichbarkeit Zürich");

  // Echte Score-Karte
  s.addImage({
    path: "/sessions/intelligent-practical-clarke/mnt/Einsatz von Geodaten in Marketing/reports/figures/score_map.png",
    x: 0.5, y: 1.6, w: 5.2, h: 3.4,
    sizing: { type: "contain", w: 5.2, h: 3.4 },
  });

  // Findings list
  card(s, 5.95, 1.6, 3.55, 3.4, C.secondary);
  s.addText("Was die Karte zeigt", {
    x: 6.15, y: 1.78, w: 3.2, h: 0.4,
    fontFace: FONT_H, fontSize: 16, bold: true, color: C.secondary, margin: 0,
  });
  s.addText([
    { text: "Höchste Werte (> 90)", options: { bold: true, color: C.good, breakLine: true } },
    { text: "Lindenhof, Werd, Rathaus, City — Kern-Innenstadt mit maximaler Funktionsmischung", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Mittelfeld (30 – 60)", options: { bold: true, color: C.hi, breakLine: true } },
    { text: "Sihlfeld, Wipkingen, Enge — Wohnviertel mit guter ÖV-Anbindung", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Niedrigste Werte (< 20)", options: { bold: true, color: C.bad, breakLine: true } },
    { text: "Leimbach, Witikon, Hirzenbach, Affoltern — Stadtperipherie und Hangwohnen" },
  ], { x: 6.15, y: 2.25, w: 3.2, h: 2.6,
    fontFace: FONT_B, fontSize: 10.5, color: C.ink, margin: 0 });

  smallFooter(s, "Score in [0, 100] · Quantil-Klassifikation (k=7) · RdYlGn");
  pageNumber(s, 11, TOTAL);
}

// --- 12 3D-Visualisierung (NEU) -------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "ERGEBNISSE · 2/6");
  slideTitle(s, "3D-Skyline — Score als Höhe");

  // Bild links (das QGIS-Screenshot)
  s.addImage({
    path: "/sessions/intelligent-practical-clarke/mnt/Einsatz von Geodaten in Marketing/reports/figures/qgis_3d_score.png",
    x: 0.5, y: 1.6, w: 5.2, h: 3.4,
    sizing: { type: "contain", w: 5.2, h: 3.4 },
  });

  // Erläuterung rechts
  card(s, 5.95, 1.6, 3.55, 3.4, C.primary);
  s.addText("Was die 3D-Karte zeigt", {
    x: 6.15, y: 1.78, w: 3.2, h: 0.4,
    fontFace: FONT_H, fontSize: 16, bold: true, color: C.primary, margin: 0,
  });
  s.addText([
    { text: "Höhe = Score × 30", options: { bold: true, color: C.good, breakLine: true } },
    { text: "Innenstadt-Quartiere ragen wie Wolkenkratzer (Score 90+)", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Farbe = RdYlGn-Verlauf", options: { bold: true, color: C.hi, breakLine: true } },
    { text: "Grün = hohe Erreichbarkeit, Rot = niedrige", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Live-Demo via PostGIS", options: { bold: true, color: C.secondary, breakLine: true } },
    { text: "QGIS 3.44 + PostGIS-Verbindung — neue POIs lassen sich live einsetzen, der Score reagiert dynamisch." },
  ], { x: 6.15, y: 2.25, w: 3.2, h: 2.6,
    fontFace: FONT_B, fontSize: 10.5, color: C.ink, margin: 0 });

  smallFooter(s, "QGIS-Projektdatei: qgis/zh15min.qgz · PostGIS-Quelle: zh15min.score");
  pageNumber(s, 12, TOTAL);
}

// --- 13 Topografische Erweiterung (Tobler + Delta) ------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "ERGEBNISSE · 3/6");
  slideTitle(s, "Topografische Erweiterung — flach vs. real");

  // Drei-Karten-Vergleich aus Notebook 06b
  s.addImage({
    path: "/sessions/intelligent-practical-clarke/mnt/Einsatz von Geodaten in Marketing/reports/figures/score_flat_vs_topo.png",
    x: 0.4, y: 1.55, w: 5.6, h: 2.0,
    sizing: { type: "contain", w: 5.6, h: 2.0 },
  });

  // Verlierer/Gewinner-Tabelle (Mini)
  card(s, 0.4, 3.7, 5.6, 1.45, C.bad);
  s.addText("Top-Verlierer (Δ Score)", {
    x: 0.55, y: 3.78, w: 2.6, h: 0.3,
    fontFace: FONT_H, fontSize: 11, bold: true, color: C.bad, margin: 0,
  });
  s.addText([
    { text: "Oberstrass  ", options: { color: C.ink } },
    { text: "−13.8", options: { bold: true, color: C.bad, breakLine: true } },
    { text: "Fluntern    ", options: { color: C.ink } },
    { text: "−11.2", options: { bold: true, color: C.bad, breakLine: true } },
    { text: "Alt-Wiedikon", options: { color: C.ink } },
    { text: " −8.1", options: { bold: true, color: C.bad, breakLine: true } },
    { text: "Wipkingen   ", options: { color: C.ink } },
    { text: " −8.0", options: { bold: true, color: C.bad } },
  ], { x: 0.55, y: 4.10, w: 2.6, h: 1.0,
    fontFace: "Courier New", fontSize: 10, color: C.ink, margin: 0 });

  s.addText("Top-Gewinner (Δ Score)", {
    x: 3.25, y: 3.78, w: 2.6, h: 0.3,
    fontFace: FONT_H, fontSize: 11, bold: true, color: C.good, margin: 0,
  });
  s.addText([
    { text: "Mühlebach   ", options: { color: C.ink } },
    { text: "+8.5", options: { bold: true, color: C.good, breakLine: true } },
    { text: "Seefeld     ", options: { color: C.ink } },
    { text: "+6.3", options: { bold: true, color: C.good, breakLine: true } },
    { text: "Oerlikon    ", options: { color: C.ink } },
    { text: "+4.4", options: { bold: true, color: C.good, breakLine: true } },
    { text: "Werd        ", options: { color: C.ink } },
    { text: "+3.0", options: { bold: true, color: C.good } },
  ], { x: 3.25, y: 4.10, w: 2.6, h: 1.0,
    fontFace: "Courier New", fontSize: 10, color: C.ink, margin: 0 });

  // Erläuterung rechts
  card(s, 6.2, 1.55, 3.4, 3.6, C.primary);
  s.addText("Was ändert sich?", {
    x: 6.4, y: 1.72, w: 3.0, h: 0.35,
    fontFace: FONT_H, fontSize: 15, bold: true, color: C.primary, margin: 0,
  });
  s.addText([
    { text: "Tobler-Hiking-Funktion", options: { bold: true, color: C.secondary, breakLine: true } },
    { text: "Walking-Tempo abhängig von Steigung pro Edge — bergauf langsamer, bergab schneller.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "SwissALTI3D 2 m DEM", options: { bold: true, color: C.secondary, breakLine: true } },
    { text: "Höhe pro Knoten · Steigung pro Kante · 124 swisstopo-Kacheln.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Plausibilität bestätigt", options: { bold: true, color: C.good, breakLine: true } },
    { text: "Verlierer = Hangzonen (Zürichberg, Käferberg, Üetliberg). Gewinner = flache See-Quartiere. ", options: { breakLine: true } },
    { text: "Median Δ = −2.3, Range [−33, +19]." },
  ], { x: 6.4, y: 2.15, w: 3.0, h: 2.9,
    fontFace: FONT_B, fontSize: 10, color: C.ink, margin: 0 });

  smallFooter(s, "Tobler · SwissALTI3D · Notebook 06b · 744 Hex × 8092 POIs · Dijkstra-Cutoff 15 min");
  pageNumber(s, 13, TOTAL);
}

// --- 14 Hypothesen-Test ----------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "ERGEBNISSE · 4/6");
  slideTitle(s, "Hypothesen-Test — H1, H1a, H2");

  // H1 — Mietpreis
  card(s, 0.4, 1.55, 3.0, 3.55, C.primary);
  s.addText("H1 — Score ↔ Mietpreis", {
    x: 0.55, y: 1.72, w: 2.7, h: 0.35,
    fontFace: FONT_H, fontSize: 12, bold: true, color: C.primary, margin: 0,
  });
  bigStat(s, 0.4, 2.18, 3.0, 0.9, "ρ = +0.56", "Spearman, n=34, p<10⁻³", C.primary);
  s.addText("Stützt H1: höherer Score ↔ höherer Median-Mietpreis (Pearson r = +0.56, p ≈ 5·10⁻⁴). Lindenhof, Rathaus mit hohen Score- UND hohen Miet-Werten; Leimbach, Witikon mit beiden tief.", {
    x: 0.55, y: 3.18, w: 2.7, h: 1.85,
    fontFace: FONT_B, fontSize: 9.5, color: C.ink, margin: 0,
  });

  // H1a — HB-Distanz (Robustness)
  card(s, 3.5, 1.55, 3.0, 3.55, C.secondary);
  s.addText("H1a — Score ↔ HB-Distanz", {
    x: 3.65, y: 1.72, w: 2.7, h: 0.35,
    fontFace: FONT_H, fontSize: 12, bold: true, color: C.secondary, margin: 0,
  });
  bigStat(s, 3.5, 2.18, 3.0, 0.9, "ρ = −0.81", "Spearman, n=34, p<10⁻⁸", C.secondary);
  s.addText("Stützt H1a hochsignifikant: je weiter vom HB, desto niedriger der Score. Pearson r = −0.84, p < 10⁻⁹. Konvergenz beider H1-Tests bestätigt das Zentralitäts-Muster ohne Markt-Confounder.", {
    x: 3.65, y: 3.18, w: 2.7, h: 1.85,
    fontFace: FONT_B, fontSize: 9.5, color: C.ink, margin: 0,
  });

  // H2 — Wüsteneffekt
  card(s, 6.6, 1.55, 3.0, 3.55, C.good);
  s.addText("H2 — Wüsteneffekt widerlegt", {
    x: 6.75, y: 1.72, w: 2.7, h: 0.35,
    fontFace: FONT_H, fontSize: 12, bold: true, color: C.good, margin: 0,
  });
  bigStat(s, 6.6, 2.18, 3.0, 0.9, "0 / 34", "Dichte > P75 ∧ Score-P25 ≤ P25", C.good);
  s.addText("Kein Quartier erfüllt beide Schwellen. Zürichs Stadtstruktur ist konsistent — keine US-typischen 'food deserts'. Periphere Quartiere haben tiefen Score (5 < 20), dort wohnen aber auch wenige Menschen.", {
    x: 6.75, y: 3.18, w: 2.7, h: 1.85,
    fontFace: FONT_B, fontSize: 9.5, color: C.ink, margin: 0,
  });

  smallFooter(s, "Werte aus 06_gap_analysis.ipynb · Live-Reproduzierbar");
  pageNumber(s, 14, TOTAL);
}

// --- 15 Top/Flop Quartiere -------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "ERGEBNISSE · 5/6");
  slideTitle(s, "Top- & Flop-Quartiere");

  const top = [
    ["Lindenhof",      92],
    ["Werd",           92],
    ["Rathaus",        92],
    ["Langstrasse",    91],
    ["City",           91],
  ];
  const flop = [
    ["Leimbach",        9],
    ["Witikon",        10],
    ["Hirzenbach",     19],
    ["Affoltern",      19],
    ["Friesenberg",    19],
  ];

  function chart(side, list, color, label) {
    const xb = side === "L" ? 0.5 : 5.05;
    card(s, xb, 1.65, 4.5, 3.4, color);
    s.addText(label, {
      x: xb + 0.2, y: 1.8, w: 4.1, h: 0.35,
      fontFace: FONT_H, fontSize: 14, bold: true, color: color, margin: 0,
    });
    list.forEach(([name, val], i) => {
      const y = 2.3 + i * 0.45;
      const w = (val / 100) * 2.5;
      s.addText(name, {
        x: xb + 0.2, y: y, w: 1.5, h: 0.32,
        fontFace: FONT_B, fontSize: 11, color: C.ink, margin: 0, valign: "middle",
      });
      s.addShape("rect", { x: xb + 1.7, y: y + 0.06, w: w, h: 0.22,
        fill: { color: color }, line: { color: color, width: 0 } });
      s.addText(String(val), {
        x: xb + 1.7 + w + 0.05, y: y, w: 0.55, h: 0.32,
        fontFace: FONT_H, fontSize: 11, bold: true, color: C.ink, margin: 0, valign: "middle",
      });
    });
  }

  chart("L", top,  C.good, "Top 5 Quartiere");
  chart("R", flop, C.bad,  "Flop 5 Quartiere");

  smallFooter(s, "Score-Mittelwert je Quartier · Gesamt-Range 9 – 92 · n = 34 (alle offiziellen Quartiere)");
  pageNumber(s, 15, TOTAL);
}

// --- 16 Cluster-Typologie (Ergebnisse 6/6) --------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "ERGEBNISSE · 6/6");
  slideTitle(s, "Quartier-Typologie via K-Means");

  // Erläuterung oben
  s.addText([
    { text: "Clustering der 28 Quartiere auf den ", options: {} },
    { text: "sechs Kategorie-Erreichbarkeiten", options: { bold: true } },
    { text: " (statt nur Total-Score) ergibt eine vier-typische Zürcher Quartier-Landschaft:", options: {} },
  ], { x: 0.5, y: 1.55, w: 9.0, h: 0.55,
       fontFace: FONT_B, fontSize: 13, color: C.ink, margin: 0 });

  // Vier Cluster-Karten in 2x2 Grid
  const clusters = [
    { tag: "Typ A", color: C.good, score: "⌀ 90", n: "n = 7",
      title: "Zentrale Mischung",
      members: "Lindenhof · Werd · Rathaus · Langstrasse · City · Hochschulen · Gewerbeschule",
      desc: "Alle sechs Funktionen in Walking-Distanz.",
    },
    { tag: "Typ B", color: C.primary, score: "⌀ 59", n: "n = 9",
      title: "Mittelband mit ÖV",
      members: "Sihlfeld · Hard · Oerlikon · Alt-Wiedikon · Unterstrass · Mühlebach · Escher Wyss · Enge · Wipkingen",
      desc: "Wohnviertel mit guter Tram-/Bus-Anbindung.",
    },
    { tag: "Typ C", color: C.hi, score: "⌀ 29", n: "n = 4",
      title: "Stadtnord-Rand",
      members: "Saatlen · Seebach · Schwamendingen-Mitte · Friesenberg",
      desc: "Erholung-positiv, alle anderen Funktionen tief.",
    },
    { tag: "Typ D", color: C.bad, score: "⌀ 23", n: "n = 14",
      title: "Periphere Wohnviertel",
      members: "Hottingen · Witikon · Leimbach · Affoltern · Hirzenbach · u. a.",
      desc: "Alle Funktionen unterdurchschnittlich.",
    },
  ];

  clusters.forEach((cl, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 4.6, y = 2.25 + row * 1.45;
    card(s, x, y, 4.4, 1.30, cl.color);

    // Tag-Pill links oben
    s.addShape("rect", { x: x + 0.15, y: y + 0.15, w: 0.7, h: 0.32,
      fill: { color: cl.color }, line: { color: cl.color, width: 0 } });
    s.addText(cl.tag, { x: x + 0.15, y: y + 0.15, w: 0.7, h: 0.32,
      fontFace: FONT_H, fontSize: 11, bold: true, color: "FFFFFF",
      align: "center", valign: "middle", margin: 0 });

    // Titel oben rechts
    s.addText(cl.title, { x: x + 0.95, y: y + 0.13, w: 2.6, h: 0.32,
      fontFace: FONT_H, fontSize: 13.5, bold: true, color: cl.color,
      margin: 0, valign: "middle" });

    // Score und n rechts
    s.addText(`${cl.score}  ·  ${cl.n}`, {
      x: x + 3.55, y: y + 0.13, w: 0.8, h: 0.32,
      fontFace: FONT_H, fontSize: 11, bold: true, color: cl.color,
      align: "right", margin: 0, valign: "middle",
    });

    // Mitglieder
    s.addText(cl.members, { x: x + 0.15, y: y + 0.55, w: 4.1, h: 0.42,
      fontFace: FONT_B, fontSize: 9.5, italic: true, color: C.ink,
      margin: 0 });

    // Beschreibung
    s.addText(cl.desc, { x: x + 0.15, y: y + 0.95, w: 4.1, h: 0.32,
      fontFace: FONT_B, fontSize: 10, color: C.mute,
      margin: 0 });
  });

  smallFooter(s, "K-Means (k=4) auf 6 standardisierten Kategorie-Accessibilities · sklearn");
  pageNumber(s, 16, TOTAL);
}

// --- 17 Diskussion / Beantwortung Forschungsfrage --------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "DISKUSSION · 1/2");
  slideTitle(s, "Antwort auf die Forschungsfrage");
  // (Slide 15 in der neuen Struktur)

  card(s, 0.5, 1.65, 9.0, 1.4, C.primary);
  s.addText([
    { text: "Die grössten Lücken zwischen Wohnen und täglicher Infrastruktur ", options: {} },
    { text: "liegen in der Stadtperipherie", options: { bold: true, color: C.primary } },
    { text: " (Leimbach, Witikon, Hirzenbach, Affoltern, Friesenberg) — über 80 Score-Punkte Abstand zum Zentrum. Die Korrelation Score × Distanz zum HB beträgt ", options: {} },
    { text: "ρ = −0.81 (p < 10⁻⁸)", options: { bold: true, color: C.bad } },
    { text: " — Zentralität ist der dominante Treiber. Multi-Variate-Modell erklärt 86 % der Score-Varianz.", options: {} },
  ], { x: 0.7, y: 1.85, w: 8.6, h: 1.05,
       fontFace: FONT_B, fontSize: 14, color: C.ink, margin: 0 });

  // 3 implications
  const impls = [
    { h: "Stadtplanung",   b: "Versorgungs-Auflagen für Entwicklungsgebiete vor der Erstvermietung." },
    { h: "Investoren",     b: "Lagen mit Score < 40 sind preislich Chance, bergen aber Vermarktungsrisiko." },
    { h: "Einzelhandel",   b: "Wüsten-Quartiere = priorisierte Standorte für Nahversorger-Expansion." },
  ];
  impls.forEach((im, i) => {
    const x = 0.5 + i * 3.05;
    card(s, x, 3.25, 2.85, 1.65, C.secondary);
    s.addText(im.h, { x: x + 0.2, y: 3.4, w: 2.5, h: 0.35,
      fontFace: FONT_H, fontSize: 14, bold: true, color: C.secondary, margin: 0 });
    s.addText(im.b, { x: x + 0.2, y: 3.78, w: 2.5, h: 1.0,
      fontFace: FONT_B, fontSize: 11, color: C.ink, margin: 0 });
  });

  pageNumber(s, 17, TOTAL);
}

// --- 18 Robustness Check ---------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "DISKUSSION · 2/2");
  slideTitle(s, "Robustness Check — H1 hält stand");

  // Linke Karte: Regressionstabelle
  card(s, 0.5, 1.65, 5.4, 3.4, C.primary);
  s.addText("Multi-Variate-Regression  (n = 34, R² = 0.91)", {
    x: 0.7, y: 1.8, w: 5.0, h: 0.35,
    fontFace: FONT_H, fontSize: 13, bold: true, color: C.primary, margin: 0,
  });

  // Tabellen-Header
  const tx = 0.7, ty = 2.25, colW = [1.7, 0.95, 0.95, 1.0, 0.6];
  const headers = ["Prädiktor", "bivar. r", "partiell β", "p-Wert", "Status"];
  let cx = tx;
  headers.forEach((h, i) => {
    s.addText(h, {
      x: cx, y: ty, w: colW[i], h: 0.3,
      fontFace: FONT_H, fontSize: 10, bold: true, color: C.mute, margin: 0,
    });
    cx += colW[i];
  });

  const rowsR = [
    ["Distanz HB",        "−0.84",  "−9.52",  "<10⁻⁶",   "***",  C.good],
    ["Höhe (SwissALTI3D)","−0.60",  "−0.107", "<10⁻³",   "***",  C.good],
    ["POI-Dichte",        "+0.86",  "+0.069", "<10⁻⁴",   "***",  C.hi],
  ];
  rowsR.forEach((row, ri) => {
    const ry = ty + 0.4 + ri * 0.42;
    let rx = tx;
    row.slice(0, 5).forEach((val, i) => {
      const isStatus = i === 4;
      s.addText(val, {
        x: rx, y: ry, w: colW[i], h: 0.32,
        fontFace: i === 0 ? FONT_B : "Consolas",
        fontSize: i === 0 ? 11 : 10.5,
        bold: isStatus || i === 0,
        color: isStatus ? row[5] : C.ink,
        margin: 0, valign: "middle",
      });
      rx += colW[i];
    });
  });

  s.addText("Signifikanz-Codes:  *** p<0.001 · ** p<0.01 · * p<0.05", {
    x: 0.7, y: 4.55, w: 5.0, h: 0.3,
    fontFace: FONT_B, fontSize: 9, italic: true, color: C.mute, margin: 0,
  });

  // Rechte Karte: drei Findings
  card(s, 6.0, 1.65, 3.5, 3.4, C.secondary);
  s.addText("Was das bedeutet", {
    x: 6.2, y: 1.8, w: 3.2, h: 0.35,
    fontFace: FONT_H, fontSize: 13, bold: true, color: C.secondary, margin: 0,
  });
  s.addText([
    { text: "H1 robust", options: { bold: true, color: C.good, breakLine: true } },
    { text: "Distanz hochsignifikant nach Kontrolle (β = −9.52).", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Topografie ist Co-Treiber", options: { bold: true, color: C.good, breakLine: true } },
    { text: "SwissALTI3D-Höhen: höher = niedrigerer Score (β = −0.107).", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Gewichts-robust", options: { bold: true, color: C.primary, breakLine: true } },
    { text: "Spearman ρ > 0.98 in allen Szenarien.", options: { breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "Distanz-Approximation valid", options: { bold: true, color: C.primary, breakLine: true } },
    { text: "Luftlinie vs. Strassennetz: r = 0.991.", options: {} },
  ], { x: 6.2, y: 2.25, w: 3.2, h: 2.7,
       fontFace: FONT_B, fontSize: 10, color: C.ink, margin: 0 });

  smallFooter(s, "OLS-Regression mit statsmodels · Daten: reports/robustness_data.csv");
  pageNumber(s, 18, TOTAL);
}

// --- 19 Limitationen -------------------------------------------------------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  sectionTag(s, "SCHLUSS · 1/2");
  slideTitle(s, "Limitationen unseres Modells");

  const lim = [
    { h: "Datenqualität OSM", b: "Kleine, unmappte Geschäfte fehlen. Annahme: Verzerrung gering, weil Geschäfte ähnlicher Klassifikation OSM-mässig konsistent sind." },
    { h: "Tobler-Modell-Annahme", b: "Die Tobler-Hiking-Funktion ist auf Wandern in offenem Gelände kalibriert (Tobler 1993), nicht auf städtisches Gehen mit Ampeln und Querstrassen. Der relative Unterschied flat vs. topografisch (Slide 13) bleibt aber aussagekräftig." },
    { h: "Single-City-Befund", b: "H2-Falsifikation (keine Wüsten) gilt für Zürich; die 15-Min-Stadt-Methodik ist nicht stadt-spezifisch und sollte für externe Validität auf weitere Städte angewendet werden." },
    { h: "Mietpreis-Confounder", b: "Premium-Wohnlagen wie Hottingen, Seefeld zeigen hohe Mieten trotz niedrigerer Score-Werte — andere Form von Lagequalität (ruhig, grün) als unsere fussläufige Mischnutzungs-Definition." },
  ];

  lim.forEach((l, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.5 + col * 4.6, y = 1.7 + row * 1.65;
    card(s, x, y, 4.4, 1.5, C.bad);
    s.addText(l.h, { x: x + 0.2, y: y + 0.18, w: 4.0, h: 0.4,
      fontFace: FONT_H, fontSize: 14, bold: true, color: C.bad, margin: 0 });
    s.addText(l.b, { x: x + 0.2, y: y + 0.6, w: 4.0, h: 0.85,
      fontFace: FONT_B, fontSize: 11, color: C.ink, margin: 0 });
  });

  pageNumber(s, 19, TOTAL);
}

// --- 20 Ausblick + Schlussfolie --------------------------------------------
{
  const s = pres.addSlide();
  darkBg(s);
  sectionTag(s, "SCHLUSS · 2/2");
  s.addText("Ausblick & take-away", {
    x: 0.4, y: 0.65, w: 9.2, h: 0.7,
    fontFace: FONT_H, fontSize: 30, bold: true, color: "FFFFFF", margin: 0,
  });

  const next = [
    "DEM-basierte Topografie + Multi-Variate-Regression mit ÖV-Anbindung",
    "Echtzeit-Mobilitätsdaten — SBB GTFS, ZVV-Reisezeiten",
    "Dynamisches Re-Scoring bei neuem POI (QGIS-Live-Demo)",
    "Erweiterung auf Winterthur, Basel — nationaler Vergleich",
  ];
  next.forEach((n, i) => {
    const y = 1.55 + i * 0.5;
    s.addShape("ellipse", { x: 0.55, y: y, w: 0.3, h: 0.3,
      fill: { color: C.hi }, line: { color: C.hi, width: 0 } });
    s.addText("→", { x: 0.55, y: y, w: 0.3, h: 0.3,
      fontFace: FONT_H, fontSize: 13, bold: true, color: C.accent,
      align: "center", valign: "middle", margin: 0 });
    s.addText(n, { x: 1.0, y: y, w: 8.5, h: 0.36,
      fontFace: FONT_B, fontSize: 14, color: "FFFFFF", margin: 0, valign: "middle" });
  });

  // closing
  s.addShape("rect", { x: 0.5, y: 4.0, w: 1.4, h: 0.05,
    fill: { color: C.hi }, line: { color: C.hi, width: 0 } });
  s.addText("Vielen Dank — Fragen & Diskussion", {
    x: 0.5, y: 4.2, w: 9.0, h: 0.6,
    fontFace: FONT_H, fontSize: 26, bold: true, color: "FFFFFF", margin: 0,
  });
  s.addText("Repository · github.com/<gruppe>/zh15min   ·   Live-Demo: docker compose up -d", {
    x: 0.5, y: 4.85, w: 9.0, h: 0.35,
    fontFace: FONT_B, fontSize: 12, color: "94A3B8", margin: 0,
  });

  smallFooter(s, "© OpenStreetMap-Mitwirkende · Stadt Zürich · BFS · swisstopo", true);
  pageNumber(s, 20, TOTAL, true);
}

// Write
pres.writeFile({ fileName: OUT_FILE }).then((f) => {
  console.log("Slides geschrieben:", f);
});

-- Initialisierung der PostGIS-Datenbank für das 15-Min-City-Projekt
-- Wird beim ersten Start des Postgres-Containers automatisch ausgeführt.

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS hstore;       -- für osm2pgsql tags
CREATE EXTENSION IF NOT EXISTS pg_trgm;      -- für Textsuche in OSM-Tags

-- Eigenes Schema für unsere Analyse-Outputs
CREATE SCHEMA IF NOT EXISTS zh15min;

-- osm2pgsql legt eigene Tabellen unter 'public' an (planet_osm_point, ...).
-- In zh15min/ legen wir abgeleitete Layer ab.

COMMENT ON SCHEMA zh15min IS 'Schema für abgeleitete 15-Min-City-Layer (Score, Hex-Grid, Versorgungslücken)';

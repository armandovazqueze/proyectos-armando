-- ============================================================
-- tracker-diario | schema.sql
-- Base de datos SQLite para el tracker diario personal
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- Tabla: activities
-- Catálogo de actividades disponibles para registrar en el día
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS activities (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_name    TEXT    NOT NULL,
    activity_category TEXT   NOT NULL,
    active           INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at       TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
);

-- ------------------------------------------------------------
-- Tabla: daily_checkins
-- Un registro por día con las respuestas del check-in
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_checkins (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    checkin_date        TEXT    NOT NULL UNIQUE,   -- formato YYYY-MM-DD
    created_at          TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    mood_score          INTEGER NOT NULL CHECK (mood_score BETWEEN 1 AND 10),
    energy_score        INTEGER NOT NULL CHECK (energy_score BETWEEN 1 AND 10),
    stress_score        INTEGER NOT NULL CHECK (stress_score BETWEEN 1 AND 10),
    -- 1 = Poco significativo, 2 = Normal, 3 = Muy significativo
    meaningfulness_level INTEGER NOT NULL CHECK (meaningfulness_level IN (1, 2, 3)),
    best_part_of_day    TEXT,
    energy_drainer      TEXT
);

-- ------------------------------------------------------------
-- Tabla: checkin_activities
-- Tabla puente: relaciona check-ins con múltiples actividades
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS checkin_activities (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    checkin_id  INTEGER NOT NULL REFERENCES daily_checkins(id) ON DELETE CASCADE,
    activity_id INTEGER NOT NULL REFERENCES activities(id) ON DELETE RESTRICT,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE (checkin_id, activity_id)  -- evita duplicados por día
);

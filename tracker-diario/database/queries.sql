-- ============================================================
-- tracker-diario | queries.sql
-- Consultas útiles para analizar el tracker diario
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- 1. Ver todos los check-ins ordenados por fecha
-- ------------------------------------------------------------
SELECT
    checkin_date,
    mood_score,
    energy_score,
    stress_score,
    CASE meaningfulness_level
        WHEN 1 THEN 'Poco'
        WHEN 2 THEN 'Normal'
        WHEN 3 THEN 'Mucho'
    END AS meaningfulness,
    best_part_of_day,
    energy_drainer
FROM daily_checkins
ORDER BY checkin_date DESC;

-- ------------------------------------------------------------
-- 2. Ver mood, energía, estrés y meaningfulness por día
-- ------------------------------------------------------------
SELECT
    checkin_date,
    mood_score,
    energy_score,
    stress_score,
    CASE meaningfulness_level
        WHEN 1 THEN 'Poco'
        WHEN 2 THEN 'Normal'
        WHEN 3 THEN 'Mucho'
    END AS meaningfulness
FROM daily_checkins
ORDER BY checkin_date;

-- ------------------------------------------------------------
-- 3. Promedio semanal de mood, energía y estrés
--    (agrupa por año + número de semana ISO)
-- ------------------------------------------------------------
SELECT
    strftime('%Y', checkin_date)                          AS year,
    strftime('%W', checkin_date)                          AS week,
    ROUND(AVG(mood_score),   1)                           AS avg_mood,
    ROUND(AVG(energy_score), 1)                           AS avg_energy,
    ROUND(AVG(stress_score), 1)                           AS avg_stress
FROM daily_checkins
GROUP BY year, week
ORDER BY year DESC, week DESC;

-- ------------------------------------------------------------
-- 4. Actividades más frecuentes (todas las semanas)
-- ------------------------------------------------------------
SELECT
    a.activity_name,
    a.activity_category,
    COUNT(*) AS times_done
FROM checkin_activities ca
JOIN activities a ON a.id = ca.activity_id
GROUP BY a.id
ORDER BY times_done DESC;

-- ------------------------------------------------------------
-- 5. Mood promedio por actividad
-- ------------------------------------------------------------
SELECT
    a.activity_name,
    a.activity_category,
    ROUND(AVG(dc.mood_score), 2) AS avg_mood,
    COUNT(*)                     AS times_done
FROM checkin_activities ca
JOIN activities    a  ON a.id  = ca.activity_id
JOIN daily_checkins dc ON dc.id = ca.checkin_id
GROUP BY a.id
ORDER BY avg_mood DESC;

-- ------------------------------------------------------------
-- 6. Meaningfulness promedio por actividad
-- ------------------------------------------------------------
SELECT
    a.activity_name,
    a.activity_category,
    ROUND(AVG(dc.meaningfulness_level), 2) AS avg_meaningfulness,
    COUNT(*)                               AS times_done
FROM checkin_activities ca
JOIN activities     a  ON a.id  = ca.activity_id
JOIN daily_checkins dc ON dc.id = ca.checkin_id
GROUP BY a.id
ORDER BY avg_meaningfulness DESC;

-- ------------------------------------------------------------
-- 7. Días con mayor estrés (top 5)
-- ------------------------------------------------------------
SELECT
    checkin_date,
    stress_score,
    mood_score,
    energy_score,
    energy_drainer
FROM daily_checkins
ORDER BY stress_score DESC
LIMIT 5;

-- ------------------------------------------------------------
-- 8. Días con mejor ánimo (top 5)
-- ------------------------------------------------------------
SELECT
    checkin_date,
    mood_score,
    energy_score,
    stress_score,
    best_part_of_day
FROM daily_checkins
ORDER BY mood_score DESC
LIMIT 5;

-- ------------------------------------------------------------
-- 9. Actividades que aparecen en días con meaningfulness = 3
--    (días muy significativos)
-- ------------------------------------------------------------
SELECT
    a.activity_name,
    a.activity_category,
    COUNT(*) AS apariciones_en_dias_nutritivos
FROM checkin_activities ca
JOIN activities     a  ON a.id  = ca.activity_id
JOIN daily_checkins dc ON dc.id = ca.checkin_id
WHERE dc.meaningfulness_level = 3
GROUP BY a.id
ORDER BY apariciones_en_dias_nutritivos DESC;

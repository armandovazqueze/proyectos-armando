-- ============================================================
-- tracker-diario | seed.sql
-- Datos de ejemplo: catálogo de actividades y check-ins
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- Catálogo de actividades
-- ------------------------------------------------------------

-- Movimiento
INSERT INTO activities (activity_name, activity_category) VALUES ('Caminar',    'Movimiento');
INSERT INTO activities (activity_name, activity_category) VALUES ('Bailar',     'Movimiento');
INSERT INTO activities (activity_name, activity_category) VALUES ('Bicicleta',  'Movimiento');
INSERT INTO activities (activity_name, activity_category) VALUES ('Ping pong',  'Movimiento');

-- Creativas
INSERT INTO activities (activity_name, activity_category) VALUES ('Música',          'Creativas');
INSERT INTO activities (activity_name, activity_category) VALUES ('Cantar',          'Creativas');
INSERT INTO activities (activity_name, activity_category) VALUES ('Crear contenido', 'Creativas');

-- Sociales
INSERT INTO activities (activity_name, activity_category) VALUES ('Llamada',        'Sociales');
INSERT INTO activities (activity_name, activity_category) VALUES ('Salida a cenar', 'Sociales');
INSERT INTO activities (activity_name, activity_category) VALUES ('Salida a comer', 'Sociales');
INSERT INTO activities (activity_name, activity_category) VALUES ('Salir a bailar', 'Sociales');
INSERT INTO activities (activity_name, activity_category) VALUES ('Karaoke',        'Sociales');

-- Aprendizaje / proyectos
INSERT INTO activities (activity_name, activity_category) VALUES ('Claude / IA',      'Aprendizaje');
INSERT INTO activities (activity_name, activity_category) VALUES ('SQL',              'Aprendizaje');
INSERT INTO activities (activity_name, activity_category) VALUES ('Python',           'Aprendizaje');
INSERT INTO activities (activity_name, activity_category) VALUES ('Proyecto personal','Aprendizaje');

-- ------------------------------------------------------------
-- Check-ins de ejemplo
-- ------------------------------------------------------------

INSERT INTO daily_checkins (
    checkin_date, mood_score, energy_score, stress_score,
    meaningfulness_level, best_part_of_day, energy_drainer
) VALUES (
    '2026-05-05', 8, 7, 3, 3,
    'Terminé el esquema de la base de datos y todo funcionó a la primera.',
    'Reunión que se extendió más de lo necesario.'
);

INSERT INTO daily_checkins (
    checkin_date, mood_score, energy_score, stress_score,
    meaningfulness_level, best_part_of_day, energy_drainer
) VALUES (
    '2026-05-06', 6, 5, 6, 2,
    'Salí a caminar en la tarde y me despejé.',
    'Muchas notificaciones y correos sin respuesta.'
);

INSERT INTO daily_checkins (
    checkin_date, mood_score, energy_score, stress_score,
    meaningfulness_level, best_part_of_day, energy_drainer
) VALUES (
    '2026-05-07', 9, 8, 2, 3,
    'Karaoke con amigos, nos reímos muchísimo.',
    'Tráfico de regreso a casa.'
);

INSERT INTO daily_checkins (
    checkin_date, mood_score, energy_score, stress_score,
    meaningfulness_level, best_part_of_day, energy_drainer
) VALUES (
    '2026-05-08', 5, 4, 7, 1,
    'Logré avanzar aunque fue un día difícil.',
    'Deadline apretado que llegó sin aviso.'
);

INSERT INTO daily_checkins (
    checkin_date, mood_score, energy_score, stress_score,
    meaningfulness_level, best_part_of_day, energy_drainer
) VALUES (
    '2026-05-09', 7, 7, 4, 2,
    'Aprendí algo nuevo sobre SQL y lo apliqué de inmediato.',
    'No dormí suficiente la noche anterior.'
);

-- ------------------------------------------------------------
-- Actividades asociadas a cada check-in
-- (los IDs de actividades corresponden al orden del INSERT arriba)
-- Movimiento: Caminar=1, Bailar=2, Bicicleta=3, Ping pong=4
-- Creativas:  Música=5, Cantar=6, Crear contenido=7
-- Sociales:   Llamada=8, Salida a cenar=9, Salida a comer=10,
--             Salir a bailar=11, Karaoke=12
-- Aprendizaje: Claude/IA=13, SQL=14, Python=15, Proyecto personal=16
-- ------------------------------------------------------------

-- 2026-05-05: Claude/IA + SQL + Proyecto personal
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (1, 13);
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (1, 14);
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (1, 16);

-- 2026-05-06: Caminar + Llamada
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (2, 1);
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (2, 8);

-- 2026-05-07: Cantar + Karaoke + Salir a bailar
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (3, 6);
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (3, 12);
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (3, 11);

-- 2026-05-08: Python + Proyecto personal
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (4, 15);
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (4, 16);

-- 2026-05-09: SQL + Claude/IA + Caminar
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (5, 14);
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (5, 13);
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (5, 1);

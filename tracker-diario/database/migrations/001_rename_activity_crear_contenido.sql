-- ============================================================
-- Migration 001: rename activity label
-- "Crear contenido" → "Espiritualidad"
--
-- Safe: updates only the activity_name text label.
-- checkin_activities stores integer activity_id, so all existing
-- check-in relationships are preserved without any ID change.
--
-- Run once on the live tracker.db:
--   sqlite3 tracker.db < database/migrations/001_rename_activity_crear_contenido.sql
-- ============================================================

UPDATE activities
SET    activity_name = 'Espiritualidad'
WHERE  activity_name = 'Crear contenido';

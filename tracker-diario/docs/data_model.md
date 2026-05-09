# Modelo de datos — tracker-diario

Este documento explica las tres tablas de la base de datos en lenguaje sencillo.

---

## Visión general

```
activities          daily_checkins
──────────          ──────────────
id ◄──────────────── activity_id
activity_name       id ◄──── checkin_id ──► checkin_activities
activity_category   checkin_date
active              mood_score
created_at          energy_score
                    stress_score
                    meaningfulness_level
                    best_part_of_day
                    energy_drainer
                    created_at
```

La tabla `checkin_activities` es el puente que une las otras dos: un check-in puede tener muchas actividades, y una actividad puede aparecer en muchos check-ins.

---

## Tabla: `activities`

Guarda el catálogo de actividades disponibles. Es una lista fija que rara vez cambia.

| Columna             | Tipo    | Descripción                                                  |
|---------------------|---------|--------------------------------------------------------------|
| `id`                | INTEGER | Identificador único, se asigna automáticamente               |
| `activity_name`     | TEXT    | Nombre de la actividad (ej. "Caminar", "Karaoke")            |
| `activity_category` | TEXT    | Categoría: Movimiento, Creativas, Sociales o Aprendizaje     |
| `active`            | INTEGER | 1 = disponible, 0 = desactivada (sin borrar del historial)   |
| `created_at`        | TEXT    | Fecha y hora en que se agregó al catálogo                    |

**Categorías disponibles:**

| Categoría    | Actividades                                                    |
|--------------|----------------------------------------------------------------|
| Movimiento   | Caminar, Bailar, Bicicleta, Ping pong                          |
| Creativas    | Música, Cantar, Crear contenido                                |
| Sociales     | Llamada, Salida a cenar, Salida a comer, Salir a bailar, Karaoke |
| Aprendizaje  | Claude / IA, SQL, Python, Proyecto personal                    |

---

## Tabla: `daily_checkins`

Un registro por día. Contiene todas las respuestas del check-in diario.

| Columna                | Tipo    | Descripción                                                     |
|------------------------|---------|-----------------------------------------------------------------|
| `id`                   | INTEGER | Identificador único, se asigna automáticamente                  |
| `checkin_date`         | TEXT    | Fecha del check-in en formato `YYYY-MM-DD`. Es única por día.   |
| `created_at`           | TEXT    | Fecha y hora exacta en que se guardó el registro                |
| `mood_score`           | INTEGER | Ánimo del día: del 1 (muy bajo) al 10 (excelente)               |
| `energy_score`         | INTEGER | Energía del día: del 1 (agotado) al 10 (lleno de energía)       |
| `stress_score`         | INTEGER | Estrés del día: del 1 (sin estrés) al 10 (muy estresado)        |
| `meaningfulness_level` | INTEGER | Qué tan significativo fue el día: 1 = Poco, 2 = Normal, 3 = Mucho |
| `best_part_of_day`     | TEXT    | Texto libre: lo mejor que pasó hoy                              |
| `energy_drainer`       | TEXT    | Texto libre: qué te quitó energía hoy                          |

**Reglas de validación (CHECK constraints):**
- `mood_score`, `energy_score` y `stress_score` solo aceptan valores entre 1 y 10.
- `meaningfulness_level` solo acepta 1, 2 o 3.
- No puede haber dos check-ins con la misma fecha (`UNIQUE` en `checkin_date`).

---

## Tabla: `checkin_activities`

Tabla puente que conecta un check-in con las actividades que se realizaron ese día. Como un día puede tener varias actividades, esta tabla guarda una fila por cada combinación.

| Columna       | Tipo    | Descripción                                                      |
|---------------|---------|------------------------------------------------------------------|
| `id`          | INTEGER | Identificador único, se asigna automáticamente                   |
| `checkin_id`  | INTEGER | Referencia al check-in del día (`daily_checkins.id`)             |
| `activity_id` | INTEGER | Referencia a la actividad realizada (`activities.id`)            |
| `created_at`  | TEXT    | Fecha y hora en que se registró la actividad                     |

**Reglas:**
- La combinación `(checkin_id, activity_id)` es única: no se puede registrar la misma actividad dos veces en el mismo día.
- Si se borra un check-in, sus actividades asociadas se borran automáticamente (`ON DELETE CASCADE`).
- No se puede borrar una actividad del catálogo si ya tiene registros históricos (`ON DELETE RESTRICT`).

---

## Ejemplo de un día completo

Supón que el 7 de mayo hiciste Karaoke, bailaste y cantaste, y fue un día muy significativo.

La base de datos guarda:

**`daily_checkins`**
```
id=3 | checkin_date='2026-05-07' | mood=9 | energy=8 | stress=2 | meaningfulness=3
     | best_part='Karaoke con amigos, nos reímos muchísimo.'
     | energy_drainer='Tráfico de regreso a casa.'
```

**`checkin_activities`**
```
checkin_id=3, activity_id=6  → Cantar
checkin_id=3, activity_id=11 → Salir a bailar
checkin_id=3, activity_id=12 → Karaoke
```

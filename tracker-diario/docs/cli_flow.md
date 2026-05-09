# Flujo del CLI — tracker-diario

Este documento explica cómo funciona `app/main.py` paso a paso.

---

## Cómo ejecutarlo

Desde la carpeta `tracker-diario/`:

```bash
python app/main.py
```

> Siempre ejecuta el script desde la raíz del proyecto (`tracker-diario/`),
> no desde dentro de la carpeta `app/`. El script busca `tracker.db` en
> el directorio padre de `app/`.

---

## Flujo completo

```
python app/main.py
        │
        ▼
  db.get_connection()
  Abre tracker.db con foreign_keys = ON
        │
        ├─► ¿Ya existe un check-in para hoy?
        │         │
        │    SÍ ──┘──► Avisa y sale (sin error)
        │
        ├─► fetch_activities()  — carga el catálogo de actividades
        │
        ▼
  Pregunta 1: ¿Cómo estuvo tu ánimo hoy? (1-10)
  Pregunta 2: ¿Cuánta energía tuviste? (1-10)
  Pregunta 3: ¿Qué tanto estrés sentiste? (1-10)
  Pregunta 4: ¿Qué tan significativo fue tu día? (1/2/3)
  Pregunta 5: ¿Qué actividades hiciste? (números separados por coma)
  Pregunta 6: ¿Qué fue lo mejor del día? (texto libre)
  Pregunta 7: ¿Qué te drenó energía? (texto libre)
        │
        ▼
  insert_checkin()          — guarda una fila en daily_checkins
  insert_checkin_activities() — guarda N filas en checkin_activities
  fetch_activity_names()    — recupera nombres para el resumen
        │
  conn.commit() ─── transacción confirmada
        │
        ▼
  print_summary() — muestra el resumen con barras visuales
        │
        ▼
       FIN
```

---

## Validaciones por pregunta

| Pregunta          | Regla de validación                              | Reintento |
|-------------------|--------------------------------------------------|-----------|
| Ánimo             | Entero entre 1 y 10                              | Sí        |
| Energía           | Entero entre 1 y 10                              | Sí        |
| Estrés            | Entero entre 1 y 10                              | Sí        |
| Significado       | Entero: 1, 2 o 3                                 | Sí        |
| Actividades       | Números separados por coma, todos en el catálogo | Sí        |
| Lo mejor del día  | Texto libre, sin validación                      | No        |
| Te drenó energía  | Texto libre, sin validación                      | No        |

Todas las preguntas numéricas repiten el prompt hasta recibir un valor válido.
Las preguntas de texto aceptan cualquier entrada (incluyendo vacío).

---

## Manejo de errores

| Situación                          | Comportamiento                                   |
|------------------------------------|--------------------------------------------------|
| Check-in ya existe para hoy        | Avisa y sale con código 0                        |
| Catálogo de actividades vacío      | Avisa y sale con código 1                        |
| El usuario presiona Ctrl+C         | Sale limpiamente con mensaje amigable            |
| tracker.db no existe               | Muestra instrucción para crear las tablas        |
| Error inesperado de base de datos  | Muestra el error y sale con código 1             |
| Transacción fallida                | Hace rollback automático, no guarda datos        |

---

## Estructura de archivos

```
app/
├── main.py        # Punto de entrada: orquesta el flujo completo
├── db.py          # Conexión y operaciones con SQLite
├── prompts.py     # Preguntas al usuario y visualización del resumen
└── validators.py  # Funciones puras de validación de inputs
```

### Responsabilidades por archivo

**`validators.py`**
- Sin efectos secundarios ni imports del proyecto.
- Tres funciones: `parse_score`, `parse_meaningfulness`, `parse_activity_ids`.
- Cada una retorna el valor parseado o `None` si hay error.

**`db.py`**
- Todas las funciones reciben una `conn` abierta (sin abrir/cerrar internamente).
- `get_connection()` es el único lugar donde se abre y cierra la conexión.
- Usa `executemany` para insertar múltiples actividades en una sola llamada.

**`prompts.py`**
- Importa `validators.py` para validar inputs dentro de los loops.
- Agrupa actividades por categoría en el orden definido en `CATEGORY_ORDER`.
- `print_summary` genera las barras de progreso con caracteres Unicode.

**`main.py`**
- Importa `db` y `prompts` solamente.
- Todo el flujo ocurre dentro de un único `with db.get_connection()`.
- Maneja `KeyboardInterrupt` y excepciones genéricas de forma separada.

---

## Ejemplo de ejecución real

```
┌──────────────────────────────────┐
│  Tracker Diario  ·  2026-05-10  │
└──────────────────────────────────┘

  Responde las preguntas a continuación.
  Presiona Ctrl+C en cualquier momento para cancelar.

  ¿Cómo estuvo tu ánimo hoy? (1-10): 8
  ¿Cuánta energía tuviste hoy? (1-10): 7
  ¿Qué tanto estrés sentiste hoy? (1-10): 3

  ¿Qué tan significativo o nutritivo se sintió tu día?
    1 = Poco
    2 = Normal
    3 = Mucho
  Tu respuesta (1/2/3): 3

  ¿Qué actividades hiciste hoy? (puedes elegir varias)
  Escribe los números separados por coma.  Ejemplo: 1,3,7

  Movimiento:
     1. Bicicleta
     2. Bailar
     3. Caminar
     4. Ping pong
  Creativas:
     5. Cantar
     6. Crear contenido
     7. Música
  Sociales:
     8. Karaoke
     9. Llamada
    10. Salida a cenar
    11. Salida a comer
    12. Salir a bailar
  Aprendizaje:
    13. Claude / IA
    14. Proyecto personal
    15. Python
    16. SQL

  Tus actividades: 3,13,16

  ¿Qué fue lo mejor del día?
  > Terminé el CLI del tracker y funcionó de primera.

  ¿Qué te drenó energía hoy?
  > La reunión de la mañana se extendió demasiado.

╔══════════════════════════════════════════╗
║  Check-in guardado  ·  2026-05-10  ║
╚══════════════════════════════════════════╝

  Ánimo       ████████░░  8/10
  Energía     ███████░░░  7/10
  Estrés      ███░░░░░░░  3/10
  Significado Mucho (3/3)

  Actividades:  Caminar  ·  Claude / IA  ·  SQL

  Lo mejor:     Terminé el CLI del tracker y funcionó de primera.
  Te drenó:     La reunión de la mañana se extendió demasiado.
```

---

## Ejemplo con error de validación

```
  ¿Cómo estuvo tu ánimo hoy? (1-10): once
  ✗ 'once' no es un número. Intenta de nuevo.
  ¿Cómo estuvo tu ánimo hoy? (1-10): 15
  ✗ El ánimo debe estar entre 1 y 10.
  ¿Cómo estuvo tu ánimo hoy? (1-10): 8
```

```
  Tus actividades: 1,99,3
  ✗ La actividad 99 no existe. Elige números de la lista.
  Tus actividades: 1,3
```

---

## Cómo consultar los datos guardados

```bash
sqlite3 tracker.db < database/queries.sql
```

O en sesión interactiva:

```bash
sqlite3 tracker.db
.headers on
.mode column
SELECT checkin_date, mood_score, energy_score, stress_score FROM daily_checkins;
```

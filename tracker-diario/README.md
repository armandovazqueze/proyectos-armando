# tracker-diario

Tracker diario personal basado en SQLite. Registra tu estado emocional, energía, estrés y actividades cada día para descubrir patrones en tu bienestar.

---

## ¿Qué hace este proyecto?

Cada día puedes guardar un check-in con:

- **Ánimo** (1–10)
- **Energía** (1–10)
- **Estrés** (1–10)
- **Qué tan significativo fue el día** (1 = Poco · 2 = Normal · 3 = Mucho)
- **Actividades realizadas** (de un catálogo: Movimiento, Creativas, Sociales, Aprendizaje)
- **Lo mejor del día**
- **Qué te drenó energía**

Con el tiempo puedes consultar promedios semanales, qué actividades se asocian con mejor ánimo, y mucho más.

---

## Estructura del proyecto

```
tracker-diario/
├── README.md
├── .gitignore
├── requirements.txt
├── app/
│   ├── main.py        # Punto de entrada del CLI
│   ├── db.py          # Conexión y operaciones con SQLite
│   ├── prompts.py     # Preguntas al usuario y visualización
│   └── validators.py  # Validación de inputs
├── database/
│   ├── schema.sql     # Definición de las tablas
│   ├── seed.sql       # Catálogo de actividades y check-ins de ejemplo
│   └── queries.sql    # Consultas útiles para analizar tus datos
└── docs/
    ├── data_model.md           # Explicación del modelo de datos
    ├── cli_flow.md             # Cómo funciona el CLI paso a paso
    └── future_telegram_flow.md # Plan para integrar Telegram en el futuro
```

---

## Cómo crear la base de datos SQLite

Necesitas tener SQLite instalado. Verifica con:

```bash
sqlite3 --version
```

Si no lo tienes, instálalo:

```bash
# macOS
brew install sqlite

# Ubuntu / Debian
sudo apt install sqlite3
```

---

## Cómo correr schema.sql (crear las tablas)

Desde la carpeta raíz del proyecto:

```bash
sqlite3 tracker.db < database/schema.sql
```

Esto crea el archivo `tracker.db` con las tres tablas vacías.

---

## Cómo cargar seed.sql (datos de ejemplo)

```bash
sqlite3 tracker.db < database/seed.sql
```

Esto inserta el catálogo completo de actividades y 5 check-ins de ejemplo con sus actividades asociadas.

---

## Cómo probar queries.sql

Puedes correr todas las consultas a la vez:

```bash
sqlite3 tracker.db < database/queries.sql
```

O abrir una sesión interactiva y copiar/pegar las consultas que quieras:

```bash
sqlite3 tracker.db
```

Dentro de la sesión activa te recomendamos activar los encabezados de columna:

```sql
.headers on
.mode column
```

---

## Cómo agregar tu propio check-in

Abre SQLite y usa esta plantilla (ajusta los valores):

```sql
-- 1. Insertar el check-in del día
INSERT INTO daily_checkins (
    checkin_date, mood_score, energy_score, stress_score,
    meaningfulness_level, best_part_of_day, energy_drainer
) VALUES (
    '2026-05-10', 8, 7, 3, 3,
    'Lo mejor de mi día aquí.',
    'Lo que me drenó aquí.'
);

-- 2. Consultar el id del check-in que acabas de crear
SELECT id FROM daily_checkins WHERE checkin_date = '2026-05-10';

-- 3. Asociar actividades (usa el id del paso anterior)
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (6, 1);  -- Caminar
INSERT INTO checkin_activities (checkin_id, activity_id) VALUES (6, 14); -- SQL
```

Para ver los IDs de todas las actividades disponibles:

```sql
SELECT id, activity_name, activity_category FROM activities ORDER BY activity_category, activity_name;
```

---

## CLI — Registrar check-ins desde terminal

### Requisitos

- Python 3.10 o superior (sin dependencias externas)
- `tracker.db` ya creada con el esquema y el catálogo de actividades

Verifica tu versión de Python:

```bash
python --version
```

### Cómo correr el CLI

Desde la carpeta raíz del proyecto (`tracker-diario/`):

```bash
python app/main.py
```

El programa te hará 7 preguntas, validará tus respuestas y guardará el check-in. Al final muestra un resumen visual.

### Ejemplo de sesión

```
┌──────────────────────────────────┐
│  Tracker Diario  ·  2026-05-10  │
└──────────────────────────────────┘

  ¿Cómo estuvo tu ánimo hoy? (1-10): 8
  ¿Cuánta energía tuviste hoy? (1-10): 7
  ¿Qué tanto estrés sentiste hoy? (1-10): 3

  ¿Qué tan significativo o nutritivo se sintió tu día?
    1 = Poco  |  2 = Normal  |  3 = Mucho
  Tu respuesta (1/2/3): 3

  ¿Qué actividades hiciste hoy? (puedes elegir varias)
  Escribe los números separados por coma.  Ejemplo: 1,3,7

  Movimiento:
     1. Bicicleta
     3. Caminar
     ...
  Aprendizaje:
    13. Claude / IA
    16. SQL

  Tus actividades: 3,13,16

  ¿Qué fue lo mejor del día?
  > Terminé el CLI del tracker y funcionó de primera.

  ¿Qué te drenó energía hoy?
  > La reunión de la mañana se extendió demasiado.

╔══════════════════════════════════════════╗
║  Check-in guardado  ·  2026-05-10       ║
╚══════════════════════════════════════════╝

  Ánimo       ████████░░  8/10
  Energía     ███████░░░  7/10
  Estrés      ███░░░░░░░  3/10
  Significado Mucho (3/3)

  Actividades:  Caminar  ·  Claude / IA  ·  SQL

  Lo mejor:     Terminé el CLI del tracker y funcionó de primera.
  Te drenó:     La reunión de la mañana se extendió demasiado.
```

### Qué pasa si ingresas un valor inválido

El CLI repite la pregunta con un mensaje de error claro:

```
  ¿Cómo estuvo tu ánimo hoy? (1-10): quince
  ✗ 'quince' no es un número. Intenta de nuevo.
  ¿Cómo estuvo tu ánimo hoy? (1-10): 15
  ✗ El ánimo debe estar entre 1 y 10.
  ¿Cómo estuvo tu ánimo hoy? (1-10): 8
```

### Cancelar en cualquier momento

Presiona `Ctrl+C` para salir sin guardar nada:

```
  Check-in cancelado. ¡Hasta mañana!
```

Consulta [`docs/cli_flow.md`](docs/cli_flow.md) para ver el flujo completo con diagramas y tabla de validaciones.

---

## Dashboard local

El dashboard permite explorar los datos del tracker desde el navegador sin necesidad de abrir la terminal de SQLite.

### Estructura del dashboard

```
dashboard/
├── app.py          # Punto de entrada de Streamlit; orquesta las secciones
├── data_loader.py  # Consultas SQL → DataFrames de pandas
├── charts.py       # Gráficas de Plotly (timeline, actividades)
└── filters.py      # Funciones puras de filtrado por fecha, significado y actividad
```

`app.py` no contiene lógica de negocio; delega la carga de datos a `data_loader.py`, el filtrado a `filters.py` y las gráficas a `charts.py`.

### Cómo se conecta a tracker.db

`data_loader.py` busca `tracker.db` en la carpeta raíz del proyecto usando la ruta relativa al archivo:

```
dashboard/data_loader.py → ../tracker.db
```

La ruta se resuelve automáticamente desde cualquier directorio desde el que corras Streamlit, siempre que uses la ruta completa al script.

### Instalar dependencias

Desde la carpeta raíz del proyecto (`tracker-diario/`):

```bash
pip install -r requirements.txt
```

### Correr el dashboard

```bash
streamlit run dashboard/app.py
```

Streamlit abre el navegador automáticamente en `http://localhost:8501`.

Si el navegador no abre solo, copia esa URL y pégala manualmente.

### Qué muestra el dashboard

| Sección | Contenido |
|---|---|
| Resumen general | Total de check-ins y promedios de ánimo, energía, estrés y significado |
| Timeline | Gráfica de líneas con la evolución temporal de las métricas |
| Actividades | Frecuencia, ánimo promedio, estrés promedio y significado promedio por actividad |
| Tabla detallada | Todos los check-ins con fecha, scores, actividades y textos libres |

### Filtros disponibles

- **Rango de fechas** — limita todas las secciones al período seleccionado
- **Significado del día** — filtra por Poco / Normal / Mucho
- **Actividad** — muestra solo los días en que se realizó esa actividad (aplica al resumen, timeline y tabla; no a las estadísticas de actividades)

---

## Bot de Telegram

El bot permite hacer el check-in diario conversacionalmente desde Telegram, pregunta por pregunta, sin abrir la terminal.

### Estructura del módulo

```
telegram_bot/
├── bot.py          # Punto de entrada; crea la Application y arranca el polling
├── handlers.py     # ConversationHandler: flujo completo de preguntas y respuestas
├── questions.py    # Textos de preguntas y constructores de teclados inline
├── scheduler.py    # APScheduler: recordatorio diario a la hora configurada
└── storage.py      # Puente con tracker.db (reutiliza app/db.py, sin SQL propio)
```

### Configurar variables de entorno

```bash
cp .env.example .env
```

Edita `.env` con tus valores reales:

```
TELEGRAM_BOT_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
DAILY_REMINDER_TIME=21:00
TIMEZONE=America/Mexico_City
```

### Cómo obtener tu TELEGRAM_BOT_TOKEN

1. Abre Telegram y busca **@BotFather**
2. Envía `/newbot` y sigue las instrucciones
3. BotFather te dará un token con el formato `1234567890:AAF...`
4. Copia ese token en `TELEGRAM_BOT_TOKEN` en tu `.env`

### Cómo obtener tu TELEGRAM_CHAT_ID

1. Instala las dependencias (ver abajo)
2. Pon tu `TELEGRAM_BOT_TOKEN` en `.env` (el `TELEGRAM_CHAT_ID` puede quedar vacío por ahora)
3. Corre el bot: `python telegram_bot/bot.py`
4. Abre tu bot en Telegram y envía `/start`
5. El bot te responde con tu Chat ID: cópialo y ponlo en `TELEGRAM_CHAT_ID` en tu `.env`
6. Reinicia el bot con `Ctrl+C` y `python telegram_bot/bot.py`

### Instalar dependencias

```bash
pip install -r requirements.txt
```

### Correr el bot

Desde la carpeta raíz del proyecto (`tracker-diario/`):

```bash
python telegram_bot/bot.py
```

Deja esta terminal abierta. El bot hace polling y el scheduler corre en el mismo proceso.

### Probar /checkin

1. Con el bot corriendo, abre Telegram y busca tu bot por su nombre
2. Envía `/checkin`
3. Responde cada pregunta usando los botones inline o texto libre
4. Al final recibirás un resumen con el check-in guardado

Flujo de preguntas:

```
/checkin
  → Ánimo (1–10)           [botones]
  → Energía (1–10)         [botones]
  → Estrés (1–10)          [botones]
  → Significado (1/2/3)    [botones]
  → Actividades            [multi-select + botón Listo]
  → Lo mejor del día       [texto libre, - para omitir]
  → Qué te drenó energía   [texto libre, - para omitir]
  → ✅ Check-in guardado
```

Envía `/cancel` en cualquier momento para abortar el check-in en progreso.

### Verificar que los datos se guardaron en tracker.db

```bash
sqlite3 tracker.db "SELECT checkin_date, mood_score, energy_score, stress_score FROM daily_checkins ORDER BY checkin_date DESC LIMIT 5;"
```

O desde el dashboard de Streamlit:

```bash
streamlit run dashboard/app.py
```

El dashboard lee la misma `tracker.db` — los check-ins hechos por Telegram aparecen ahí inmediatamente.

### El recordatorio diario

A la hora configurada en `DAILY_REMINDER_TIME` (por defecto `21:00`), el bot te envía un mensaje automático. Cuando llegue, usa `/checkin` para hacer el check-in del día.

---

## Cómo subir esto a GitHub

```bash
# Desde la carpeta tracker-diario/
git init
git add .
git commit -m "feat: primera versión del tracker diario con esquema SQLite"

# Crea el repositorio en GitHub y luego:
git remote add origin https://github.com/tu-usuario/tracker-diario.git
git branch -M main
git push -u origin main
```

> El archivo `.gitignore` ya excluye `*.db` para que la base de datos local no se suba al repositorio.

---

## Próximos pasos

- Correlaciones entre actividades y bienestar en el dashboard
- Analytics avanzados: promedios rodantes, detección de patrones
- Integración con n8n o webhooks para disparar el check-in desde flujos externos
- Migración opcional a base de datos en la nube cuando sea necesario

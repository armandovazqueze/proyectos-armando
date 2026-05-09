# Plan futuro: integración con Telegram

Este documento describe la siguiente fase del tracker diario: enviar y recibir el check-in directamente desde Telegram, sin necesidad de abrir la terminal.

> **Estado actual:** la base de datos está lista y versionada. Telegram aún no está conectado.

---

## ¿Por qué Telegram?

Telegram permite crear bots que envían mensajes automáticos y reciben respuestas del usuario desde el celular. Es gratuito, rápido y tiene una API bien documentada. La idea es que el check-in llegue como un mensaje en el chat y tú respondas desde donde estés.

---

## Flujo previsto

```
[Servidor / script Python]
        │
        │  Cada día a una hora fija (ej. 9:00 pm)
        ▼
[Bot de Telegram] ──► envía preguntas al usuario una por una
        │
        │  El usuario responde desde su celular
        ▼
[Script Python]  ──► recibe las respuestas
        │
        │  Valida y formatea los datos
        ▼
[SQLite tracker.db] ──► guarda el check-in en daily_checkins
                    ──► guarda las actividades en checkin_activities
```

---

## Pasos de implementación (propuesta)

### 1. Crear el bot en Telegram

- Abrir Telegram y buscar `@BotFather`.
- Crear un bot nuevo con `/newbot`.
- Guardar el token de acceso que entrega BotFather.

### 2. Escribir el script del bot

El bot usará la librería `python-telegram-bot` (o `pyTelegramBotAPI`).

Flujo de conversación:

```
Bot:     "¿Cómo estuvo tu ánimo hoy? (1-10)"
Usuario: "8"
Bot:     "¿Cuánta energía tuviste? (1-10)"
Usuario: "6"
Bot:     "¿Cuánto estrés sentiste? (1-10)"
Usuario: "4"
Bot:     "¿Qué tan significativo fue tu día?"
         "1 = Poco  |  2 = Normal  |  3 = Mucho"
Usuario: "3"
Bot:     "¿Qué actividades hiciste? Escribe los números separados por coma."
         "1-Caminar 2-Bailar 3-Bicicleta 4-Ping pong"
         "5-Música  6-Cantar 7-Crear contenido ..."
Usuario: "1, 6, 12"
Bot:     "¿Qué fue lo mejor del día?"
Usuario: "Terminé un proyecto que tenía pendiente."
Bot:     "¿Qué te drenó energía?"
Usuario: "Las notificaciones constantes."
Bot:     "¡Check-in guardado! Aquí está tu resumen del día..."
```

### 3. Conectar el bot a SQLite

El script Python abrirá `tracker.db` y ejecutará los mismos `INSERT` que hoy hacemos a mano:

```python
import sqlite3

conn = sqlite3.connect("tracker.db")
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO daily_checkins (
        checkin_date, mood_score, energy_score, stress_score,
        meaningfulness_level, best_part_of_day, energy_drainer
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
""", (fecha, animo, energia, estres, significativo, mejor, drener))

checkin_id = cursor.lastrowid

for activity_id in actividades_seleccionadas:
    cursor.execute("""
        INSERT INTO checkin_activities (checkin_id, activity_id)
        VALUES (?, ?)
    """, (checkin_id, activity_id))

conn.commit()
conn.close()
```

### 4. Programar el envío automático

En Linux/Mac se puede usar `cron` para que el bot envíe el check-in cada noche:

```bash
# Ejecutar el bot a las 9:00 pm de lunes a domingo
0 21 * * * /usr/bin/python3 /ruta/al/bot.py
```

---

## Análisis de correlaciones (fase posterior)

Una vez que haya datos de varias semanas, se podrán explorar preguntas como:

- ¿En qué días con qué actividades el ánimo fue más alto?
- ¿Las actividades sociales se asocian con más energía al día siguiente?
- ¿El estrés sube cuando no hay actividad física en la semana?
- ¿Cuál es mi combinación de actividades para los días más significativos?

Estas preguntas se pueden responder con las consultas de `queries.sql` o, más adelante, con Python + pandas para visualizaciones.

---

## Tecnologías necesarias para esta fase

| Componente      | Herramienta                         |
|-----------------|-------------------------------------|
| Bot de Telegram | `python-telegram-bot` o `telebot`   |
| Base de datos   | SQLite (ya lista)                   |
| Lenguaje        | Python 3.10+                        |
| Scheduler       | `cron` (Linux/Mac) o `schedule` (Python) |
| Servidor        | Raspberry Pi, VPS, o tu propia computadora |

---

## Lo que NO cambia

El esquema de la base de datos (`schema.sql`) está diseñado para soportar este flujo desde ahora. No será necesario modificar las tablas cuando se integre Telegram: solo se agrega el script del bot encima de la misma base de datos.

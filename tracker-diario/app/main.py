"""
tracker-diario — CLI entry point.

Run from the tracker-diario/ directory:
    python app/main.py
"""

import sys
from datetime import date

import db
import prompts


def run():
    today = date.today().isoformat()
    prompts.print_header(f"Tracker Diario  ·  {today}")
    print("  Responde las preguntas a continuación.")
    print("  Presiona Ctrl+C en cualquier momento para cancelar.\n")

    try:
        with db.get_connection() as conn:

            if db.checkin_exists(conn, today):
                print(f"  Ya existe un check-in para hoy ({today}).")
                print("  Si necesitas corregirlo, edítalo directamente en tracker.db.\n")
                sys.exit(0)

            activities = db.fetch_activities(conn)
            if not activities:
                print("  No hay actividades en el catálogo.")
                print("  Carga el catálogo con:")
                print("      sqlite3 tracker.db < database/seed.sql\n")
                sys.exit(1)

            # --- Preguntas ---
            mood       = prompts.ask_score("¿Cómo estuvo tu ánimo hoy?",       "El ánimo")
            energy     = prompts.ask_score("¿Cuánta energía tuviste hoy?",      "La energía")
            stress     = prompts.ask_score("¿Qué tanto estrés sentiste hoy?",   "El estrés")
            meaningful = prompts.ask_meaningfulness()
            act_ids    = prompts.ask_activities(activities)
            best_part  = prompts.ask_text("¿Qué fue lo mejor del día?")
            drainer    = prompts.ask_text("¿Qué te drenó energía hoy?")

            # --- Guardar en la base de datos ---
            checkin_id = db.insert_checkin(conn, {
                "checkin_date":         today,
                "mood_score":           mood,
                "energy_score":         energy,
                "stress_score":         stress,
                "meaningfulness_level": meaningful,
                "best_part_of_day":     best_part,
                "energy_drainer":       drainer,
            })
            db.insert_checkin_activities(conn, checkin_id, act_ids)
            act_names = db.fetch_activity_names(conn, act_ids)

        # --- Resumen final (la transacción ya cerró) ---
        prompts.print_summary(
            today, mood, energy, stress, meaningful,
            act_names, best_part, drainer
        )

    except KeyboardInterrupt:
        print("\n\n  Check-in cancelado. ¡Hasta mañana!\n")
        sys.exit(0)

    except Exception as exc:
        print(f"\n  Error inesperado: {exc}")
        print("  Verifica que tracker.db existe y tiene las tablas.")
        print("  Comando: sqlite3 tracker.db < database/schema.sql\n")
        sys.exit(1)


if __name__ == "__main__":
    run()

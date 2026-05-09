"""
User-facing prompts and display helpers.
All input loops retry until the user provides a valid value.
"""

from validators import parse_score, parse_meaningfulness, parse_activity_ids

MEANINGFULNESS_LABELS = {1: "Poco", 2: "Normal", 3: "Mucho"}

# Display order for activity categories
CATEGORY_ORDER = ["Movimiento", "Creativas", "Sociales", "Aprendizaje"]


def _bar(score: int, max_val: int = 10, width: int = 10) -> str:
    filled = round(score / max_val * width)
    return "█" * filled + "░" * (width - filled)


def print_header(text: str):
    pad = "─" * (len(text) + 4)
    print(f"\n┌{pad}┐")
    print(f"│  {text}  │")
    print(f"└{pad}┘\n")


def ask_score(question: str, label: str) -> int:
    while True:
        raw = input(f"  {question} (1-10): ").strip()
        value = parse_score(raw, label)
        if value is not None:
            return value


def ask_meaningfulness() -> int:
    print("\n  ¿Qué tan significativo o nutritivo se sintió tu día?")
    print("    1 = Poco")
    print("    2 = Normal")
    print("    3 = Mucho")
    while True:
        raw = input("  Tu respuesta (1/2/3): ").strip()
        value = parse_meaningfulness(raw)
        if value is not None:
            return value


def ask_activities(activities: list) -> list:
    print("\n  ¿Qué actividades hiciste hoy? (puedes elegir varias)")
    print("  Escribe los números separados por coma.  Ejemplo: 1,3,7\n")

    by_category: dict = {}
    for row in activities:
        by_category.setdefault(row["activity_category"], []).append(row)

    valid_ids: set = set()
    for category in CATEGORY_ORDER:
        if category not in by_category:
            continue
        print(f"  {category}:")
        for row in by_category[category]:
            print(f"    {row['id']:>2}. {row['activity_name']}")
            valid_ids.add(row["id"])

    while True:
        raw = input("\n  Tus actividades: ").strip()
        ids = parse_activity_ids(raw, valid_ids)
        if ids is not None:
            return ids


def ask_text(question: str) -> str:
    return input(f"\n  {question}\n  > ").strip()


def print_summary(
    date: str,
    mood: int,
    energy: int,
    stress: int,
    meaningfulness: int,
    activity_names: list,
    best_part: str,
    energy_drainer: str,
):
    title = f"Check-in guardado  ·  {date}"
    pad = "═" * (len(title) + 4)
    print(f"\n╔{pad}╗")
    print(f"║  {title}  ║")
    print(f"╚{pad}╝\n")

    print(f"  Ánimo       {_bar(mood)}  {mood}/10")
    print(f"  Energía     {_bar(energy)}  {energy}/10")
    print(f"  Estrés      {_bar(stress)}  {stress}/10")
    print(f"  Significado {MEANINGFULNESS_LABELS[meaningfulness]} ({meaningfulness}/3)\n")

    acts = "  ·  ".join(activity_names) if activity_names else "—"
    print(f"  Actividades:  {acts}\n")

    if best_part:
        print(f"  Lo mejor:     {best_part}")
    if energy_drainer:
        print(f"  Te drenó:     {energy_drainer}")
    print()

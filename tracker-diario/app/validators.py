"""
Input validation helpers.
Each function returns the parsed value on success, or None on failure
(and prints a user-friendly error message in Spanish).
"""


def parse_score(raw: str, label: str) -> int | None:
    try:
        value = int(raw.strip())
    except ValueError:
        print(f"  ✗ '{raw.strip()}' no es un número. Intenta de nuevo.")
        return None
    if not 1 <= value <= 10:
        print(f"  ✗ {label} debe estar entre 1 y 10.")
        return None
    return value


def parse_meaningfulness(raw: str) -> int | None:
    try:
        value = int(raw.strip())
    except ValueError:
        print("  ✗ Ingresa 1, 2 o 3.")
        return None
    if value not in (1, 2, 3):
        print("  ✗ El valor debe ser 1, 2 o 3.")
        return None
    return value


def parse_activity_ids(raw: str, valid_ids: set) -> list | None:
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if not parts:
        print("  ✗ Debes elegir al menos una actividad.")
        return None
    seen: set = set()
    result: list = []
    for part in parts:
        try:
            aid = int(part)
        except ValueError:
            print(f"  ✗ '{part}' no es un número válido.")
            return None
        if aid not in valid_ids:
            print(f"  ✗ La actividad {aid} no existe. Elige números de la lista.")
            return None
        if aid not in seen:
            seen.add(aid)
            result.append(aid)
    return result

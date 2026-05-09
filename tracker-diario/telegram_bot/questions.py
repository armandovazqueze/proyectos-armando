"""
Question texts and InlineKeyboard builders for the check-in conversation.
All keyboard builders return pure data — no I/O, no DB access.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ── Question texts (HTML-safe; no user input embedded) ────────────────────────

MOOD_Q = "¿Cómo estuvo tu ánimo hoy? (1–10)"
ENERGY_Q = "¿Cuánta energía tuviste hoy? (1–10)"
STRESS_Q = "¿Qué tanto estrés sentiste hoy? (1–10)"
MEANING_Q = "¿Qué tan significativo fue tu día?"
ACTIVITIES_Q = (
    "¿Qué actividades hiciste hoy?\n"
    "Selecciona las que aplican y presiona <b>✅ Listo</b> cuando termines."
)
BEST_PART_Q = "¿Qué fue lo mejor del día?\n<i>(escribe - para omitir)</i>"
DRAINER_Q = "¿Qué te drenó energía hoy?\n<i>(escribe - para omitir)</i>"

# ── Keyboard builders ─────────────────────────────────────────────────────────

def score_keyboard() -> InlineKeyboardMarkup:
    """Two rows of five buttons: 1–5 and 6–10."""
    row1 = [InlineKeyboardButton(str(i), callback_data=f"score_{i}") for i in range(1, 6)]
    row2 = [InlineKeyboardButton(str(i), callback_data=f"score_{i}") for i in range(6, 11)]
    return InlineKeyboardMarkup([row1, row2])


def meaning_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton("1 · Poco",   callback_data="meaning_1"),
        InlineKeyboardButton("2 · Normal", callback_data="meaning_2"),
        InlineKeyboardButton("3 · Mucho",  callback_data="meaning_3"),
    ]
    return InlineKeyboardMarkup([buttons])


def activities_keyboard(activities: list[dict], selected_ids: list[int]) -> InlineKeyboardMarkup:
    """
    Group activities by category in rows of two.
    Selected activities show a ✅ prefix.
    Last row is the confirm button.
    """
    categories: dict[str, list[dict]] = {}
    for act in activities:
        categories.setdefault(act["activity_category"], []).append(act)

    rows: list[list[InlineKeyboardButton]] = []
    for acts in categories.values():
        pair: list[InlineKeyboardButton] = []
        for act in acts:
            prefix = "✅ " if act["id"] in selected_ids else ""
            btn = InlineKeyboardButton(
                f"{prefix}{act['activity_name']}",
                callback_data=f"act_toggle_{act['id']}",
            )
            pair.append(btn)
            if len(pair) == 2:
                rows.append(pair)
                pair = []
        if pair:
            rows.append(pair)

    rows.append([InlineKeyboardButton("✅ Listo", callback_data="act_done")])
    return InlineKeyboardMarkup(rows)


# ── Summary formatter ─────────────────────────────────────────────────────────

_MEANING_LABEL = {1: "Poco", 2: "Normal", 3: "Mucho"}


def build_summary(data: dict, activity_names: list[str]) -> str:
    """
    Build the confirmation message shown after a successful save.
    Uses HTML parse mode; user-typed text is NOT wrapped in HTML tags
    so special chars are safe.
    """
    acts = " · ".join(activity_names) if activity_names else "—"
    best  = data.get("best_part_of_day") or "—"
    drain = data.get("energy_drainer")   or "—"
    mlabel = _MEANING_LABEL.get(data["meaningfulness_level"], "?")
    return (
        f"<b>✅ Check-in guardado</b> · {data['checkin_date']}\n\n"
        f"  Ánimo:       {data['mood_score']}/10\n"
        f"  Energía:     {data['energy_score']}/10\n"
        f"  Estrés:      {data['stress_score']}/10\n"
        f"  Significado: {mlabel} ({data['meaningfulness_level']}/3)\n\n"
        f"  Actividades: {acts}\n\n"
        f"  Lo mejor:  {best}\n"
        f"  Te drenó:  {drain}"
    )

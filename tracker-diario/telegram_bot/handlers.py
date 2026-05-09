"""
Telegram handlers for the daily check-in conversation.

Conversation flow:
  /checkin → MOOD → ENERGY → STRESS → MEANINGFULNESS
           → ACTIVITIES (multi-select) → BEST_PART → ENERGY_DRAINER → save → END

State is stored in context.user_data throughout the conversation.
The DB write happens only after the final answer is received.
"""
import logging
from datetime import date

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from telegram_bot.questions import (
    ACTIVITIES_Q,
    BEST_PART_Q,
    DRAINER_Q,
    ENERGY_Q,
    MEANING_Q,
    MOOD_Q,
    STRESS_Q,
    activities_keyboard,
    build_summary,
    meaning_keyboard,
    score_keyboard,
)
from telegram_bot.storage import (
    checkin_exists_today,
    fetch_activities_catalog,
    save_completed_checkin,
)

log = logging.getLogger(__name__)

# ── Conversation state constants ─────────────────────────────────────────────

MOOD, ENERGY, STRESS, MEANINGFULNESS, ACTIVITIES, BEST_PART, ENERGY_DRAINER = range(7)

# ── /start — always available, even outside a conversation ───────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"¡Hola! Soy tu tracker diario 🌱\n\n"
        f"Tu <b>Chat ID</b> es: <code>{chat_id}</code>\n\n"
        f"Cópialo y ponlo en <code>TELEGRAM_CHAT_ID</code> en tu <code>.env</code>.\n\n"
        f"Comandos disponibles:\n"
        f"  /checkin — hacer el check-in del día\n"
        f"  /cancel  — cancelar un check-in en progreso",
        parse_mode=ParseMode.HTML,
    )

# ── Entry point ───────────────────────────────────────────────────────────────

async def cmd_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    today = date.today().isoformat()

    if checkin_exists_today(today):
        await update.message.reply_text(
            f"Ya guardaste un check-in para hoy ({today}) ✅\n"
            "Vuelve mañana o edita la BD directamente si necesitas corregirlo.\n\n"
            "Usa /cancel si quedó uno abierto por error."
        )
        return ConversationHandler.END

    context.user_data.clear()
    context.user_data.update({
        "checkin_date": today,
        "selected_activity_ids": [],
        "all_activities": [],
    })

    await update.message.reply_text(MOOD_Q, reply_markup=score_keyboard())
    return MOOD

# ── Step: mood ────────────────────────────────────────────────────────────────

async def receive_mood(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["mood_score"] = int(query.data.split("_")[1])
    await query.edit_message_text(ENERGY_Q, reply_markup=score_keyboard())
    return ENERGY

# ── Step: energy ──────────────────────────────────────────────────────────────

async def receive_energy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["energy_score"] = int(query.data.split("_")[1])
    await query.edit_message_text(STRESS_Q, reply_markup=score_keyboard())
    return STRESS

# ── Step: stress ──────────────────────────────────────────────────────────────

async def receive_stress(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["stress_score"] = int(query.data.split("_")[1])
    await query.edit_message_text(MEANING_Q, reply_markup=meaning_keyboard())
    return MEANINGFULNESS

# ── Step: meaningfulness ──────────────────────────────────────────────────────

async def receive_meaningfulness(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data["meaningfulness_level"] = int(query.data.split("_")[1])

    activities = fetch_activities_catalog()
    context.user_data["all_activities"] = activities

    await query.edit_message_text(
        ACTIVITIES_Q,
        reply_markup=activities_keyboard(activities, selected_ids=[]),
        parse_mode=ParseMode.HTML,
    )
    return ACTIVITIES

# ── Step: activities (multi-select loop) ─────────────────────────────────────

async def toggle_activity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    act_id = int(query.data.split("_")[2])  # act_toggle_<id>
    selected: list[int] = context.user_data["selected_activity_ids"]

    if act_id in selected:
        selected.remove(act_id)
    else:
        selected.append(act_id)

    await query.edit_message_reply_markup(
        reply_markup=activities_keyboard(context.user_data["all_activities"], selected)
    )
    return ACTIVITIES


async def done_activities(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    selected = context.user_data["selected_activity_ids"]
    all_acts = context.user_data["all_activities"]
    names = [a["activity_name"] for a in all_acts if a["id"] in selected]
    acts_text = " · ".join(names) if names else "ninguna"

    await query.edit_message_text(
        f"Actividades: {acts_text} ✅\n\n{BEST_PART_Q}",
        parse_mode=ParseMode.HTML,
    )
    return BEST_PART

# ── Step: best part of day ────────────────────────────────────────────────────

async def receive_best_part(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    context.user_data["best_part_of_day"] = None if text == "-" else text
    await update.message.reply_text(DRAINER_Q, parse_mode=ParseMode.HTML)
    return ENERGY_DRAINER

# ── Step: energy drainer → save ───────────────────────────────────────────────

async def receive_energy_drainer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    context.user_data["energy_drainer"] = None if text == "-" else text

    data = context.user_data.copy()
    all_acts = data.pop("all_activities", [])
    selected_ids = data.get("selected_activity_ids", [])
    activity_names = [a["activity_name"] for a in all_acts if a["id"] in selected_ids]

    try:
        save_completed_checkin(data)
        await update.message.reply_text(
            build_summary(data, activity_names),
            parse_mode=ParseMode.HTML,
        )
    except Exception:
        log.exception("Failed to save check-in for user %s", update.effective_user.id)
        await update.message.reply_text(
            "No se pudo guardar el check-in. Revisa que tracker.db existe.\n"
            "Usa /checkin para intentar de nuevo."
        )

    context.user_data.clear()
    return ConversationHandler.END

# ── Cancel ────────────────────────────────────────────────────────────────────

async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Check-in cancelado. ¡Hasta mañana! 👋")
    return ConversationHandler.END

# ── Assemble the ConversationHandler ─────────────────────────────────────────

def build_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("checkin", cmd_checkin)],
        states={
            MOOD: [
                CallbackQueryHandler(receive_mood, pattern=r"^score_\d+$"),
            ],
            ENERGY: [
                CallbackQueryHandler(receive_energy, pattern=r"^score_\d+$"),
            ],
            STRESS: [
                CallbackQueryHandler(receive_stress, pattern=r"^score_\d+$"),
            ],
            MEANINGFULNESS: [
                CallbackQueryHandler(receive_meaningfulness, pattern=r"^meaning_\d$"),
            ],
            ACTIVITIES: [
                CallbackQueryHandler(toggle_activity, pattern=r"^act_toggle_\d+$"),
                CallbackQueryHandler(done_activities, pattern=r"^act_done$"),
            ],
            BEST_PART: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_best_part),
            ],
            ENERGY_DRAINER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_energy_drainer),
            ],
        },
        fallbacks=[CommandHandler("cancel", cmd_cancel)],
        per_user=True,
        per_chat=True,
        per_message=False,  # track state per user/chat, not per message
    )

"""
Daily reminder scheduler using APScheduler.

The core function `trigger_daily_reminder` automatically starts the
check-in questionnaire flow at the scheduled time.  It is intentionally
decoupled from the scheduler so it can be called from a webhook, n8n,
or the /test_scheduled_checkin command without scheduler involvement.
"""
import logging
import os
from datetime import date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application

from telegram_bot.handlers import MOOD
from telegram_bot.questions import MOOD_Q, score_keyboard
from telegram_bot.storage import checkin_exists_today

log = logging.getLogger(__name__)


async def trigger_daily_reminder(application: Application, chat_id: str) -> None:
    """
    Start the daily check-in questionnaire automatically.

    - If a check-in already exists for today, sends a 'done' notice and returns.
    - Otherwise, primes the ConversationHandler state and sends the first question.

    Callable from: scheduler, /test_scheduled_checkin, webhook, or n8n.
    """
    today = date.today().isoformat()
    chat_id_int = int(chat_id)
    bot = application.bot

    if checkin_exists_today(today):
        await bot.send_message(
            chat_id=chat_id_int,
            text=(
                f"Ya guardaste un check-in para hoy ({today}) ✅\n"
                "Vuelve mañana o edita la BD directamente si necesitas corregirlo."
            ),
        )
        log.info("Scheduled trigger: check-in already exists for %s", today)
        return

    # private chat: chat_id == user_id
    user_id = chat_id_int

    # Pre-load user_data so the ConversationHandler steps find it.
    # application.user_data is a defaultdict(dict), so this is always safe.
    application.user_data[user_id].update({
        "checkin_date": today,
        "selected_activity_ids": [],
        "all_activities": [],
    })

    # Advance the ConversationHandler into MOOD state BEFORE sending the
    # message so there is no race window where the user could tap too early.
    conv_handler = application.bot_data.get("conv_handler")
    if conv_handler is not None:
        # Key is (chat_id, user_id) when per_chat=True and per_user=True.
        conv_handler._conversations[(chat_id_int, user_id)] = MOOD

    await bot.send_message(
        chat_id=chat_id_int,
        text=MOOD_Q,
        reply_markup=score_keyboard(),
    )
    log.info("Scheduled check-in started for chat_id=%s", chat_id)


def setup_scheduler(application: Application) -> AsyncIOScheduler:
    """
    Configure the APScheduler instance.
    Call scheduler.start() after the asyncio event loop is running.
    The Application.post_init hook is the right place to do that.
    """
    time_str = os.getenv("DAILY_REMINDER_TIME", "21:00")
    timezone  = os.getenv("TIMEZONE", "America/Mexico_City")
    chat_id   = os.getenv("TELEGRAM_CHAT_ID", "")

    try:
        hour, minute = map(int, time_str.split(":"))
    except ValueError:
        log.warning("DAILY_REMINDER_TIME %r is not valid HH:MM — defaulting to 21:00", time_str)
        hour, minute = 21, 0

    scheduler = AsyncIOScheduler(timezone=timezone)
    scheduler.add_job(
        trigger_daily_reminder,
        trigger="cron",
        hour=hour,
        minute=minute,
        kwargs={"application": application, "chat_id": chat_id},
        id="daily_reminder",
        replace_existing=True,
    )
    log.info(
        "Scheduler configured: daily reminder at %02d:%02d (%s)",
        hour, minute, timezone,
    )
    return scheduler

"""
Daily reminder scheduler using APScheduler.

The core function is `trigger_daily_reminder` — it is intentionally
decoupled from the scheduler so it can later be called from a webhook
or n8n without any scheduler involvement.
"""
import logging
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot

log = logging.getLogger(__name__)


async def trigger_daily_reminder(bot: Bot, chat_id: str) -> None:
    """
    Send the daily check-in prompt.
    Callable from: scheduler, webhook, n8n, or any async context.
    """
    await bot.send_message(
        chat_id=chat_id,
        text="¡Hora del check-in diario! 🌙\n\nUsa /checkin para empezar.",
    )
    log.info("Daily reminder sent to chat_id=%s", chat_id)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
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
        kwargs={"bot": bot, "chat_id": chat_id},
        id="daily_reminder",
        replace_existing=True,
    )
    log.info(
        "Scheduler configured: daily reminder at %02d:%02d (%s)",
        hour, minute, timezone,
    )
    return scheduler

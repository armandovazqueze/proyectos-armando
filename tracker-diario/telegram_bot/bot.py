"""
Entry point for the Telegram bot.

Run from tracker-diario/:
    python telegram_bot/bot.py

The scheduler (APScheduler) and the Telegram polling share the same
asyncio event loop. The scheduler is started in the post_init hook so
it is guaranteed to run inside the already-running event loop.
"""
import logging
import os
import sys
import warnings
from pathlib import Path

# Ensure project root is on sys.path so 'from app.db import ...' and
# 'from telegram_bot.*' both resolve correctly regardless of CWD.
_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv  # noqa: E402
from telegram.ext import Application, CommandHandler  # noqa: E402
from telegram.warnings import PTBUserWarning  # noqa: E402

# Per-message tracking warning is expected for sequential ConversationHandlers.
warnings.filterwarnings("ignore", message=".*per_message.*", category=PTBUserWarning)

from telegram_bot.handlers import build_conversation_handler, cmd_start  # noqa: E402
from telegram_bot.scheduler import setup_scheduler  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


async def _on_startup(app: Application) -> None:
    scheduler = setup_scheduler(app.bot)
    scheduler.start()
    app.bot_data["scheduler"] = scheduler
    log.info("Scheduler started.")


async def _on_shutdown(app: Application) -> None:
    scheduler = app.bot_data.get("scheduler")
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        log.info("Scheduler stopped.")


def main() -> None:
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        sys.exit(
            "TELEGRAM_BOT_TOKEN is not set.\n"
            "Copy .env.example to .env and fill in your token."
        )

    app = (
        Application.builder()
        .token(token)
        .post_init(_on_startup)
        .post_shutdown(_on_shutdown)
        .build()
    )

    # /start is registered before the ConversationHandler so it always
    # responds even when a check-in conversation is active.
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(build_conversation_handler())

    log.info("Bot starting — polling for updates (drop_pending=True)...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()

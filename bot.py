import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import Config
from database import init_db
from services.logger import logger

# Handlers
from handlers.start import start_handler
from handlers.help import help_handler
from handlers.admin import ban_user, unban_user, mute_user, unmute_user, purge_messages
from handlers.moderation import warn_user, clear_warnings, auto_moderation_handler
from handlers.welcome import welcome_handler
from handlers.verification import verification_callback
from handlers.rules import get_rules, set_rules
from handlers.notes import save_note, get_note
from handlers.filters import add_filter, check_filters
from handlers.reports import report_handler
from handlers.settings import settings_handler

async def main() -> None:
    Config.validate()
    
    logger.info("Initializing database...")
    await init_db()

    logger.info("Building application...")
    app = ApplicationBuilder().token(Config.BOT_TOKEN).build()

    # Core Handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("rules", get_rules))
    app.add_handler(CommandHandler("setrules", set_rules))
    app.add_handler(CommandHandler("report", report_handler))
    app.add_handler(CommandHandler("settings", settings_handler))

    # Admin Handlers
    app.add_handler(CommandHandler("ban", ban_user))
    app.add_handler(CommandHandler("unban", unban_user))
    app.add_handler(CommandHandler("mute", mute_user))
    app.add_handler(CommandHandler("unmute", unmute_user))
    app.add_handler(CommandHandler("purge", purge_messages))
    app.add_handler(CommandHandler("warn", warn_user))
    app.add_handler(CommandHandler("clearwarns", clear_warnings))

    # Reusable Data Handlers
    app.add_handler(CommandHandler("save", save_note))
    app.add_handler(CommandHandler("get", get_note))
    app.add_handler(CommandHandler("filter", add_filter))

    # Callbacks & Observers
    app.add_handler(CallbackQueryHandler(help_handler, pattern="^help_main$"))
    app.add_handler(CallbackQueryHandler(verification_callback, pattern="^verify_"))
    
    # Event Watchers
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_moderation_handler), group=1)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_filters), group=2)

    logger.info("Starting Telegram Bot Polling...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    # Keep bot running
    stop_event = asyncio.Event()
    await stop_event.wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot execution terminated.")

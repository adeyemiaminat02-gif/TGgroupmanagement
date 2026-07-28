import logging
from telegram.ext import ContextTypes
from config import Config

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=getattr(logging, Config.LOG_LEVEL, logging.INFO)
)
logger = logging.getLogger("TGGroupManagementBot")

async def log_event(context: ContextTypes.DEFAULT_TYPE, message: str) -> None:
    logger.info(message)
    if Config.LOG_GROUP_ID != 0:
        try:
            await context.bot.send_message(chat_id=Config.LOG_GROUP_ID, text=message)
        except Exception as e:
            logger.error(f"Failed to send log to log group: {e}")

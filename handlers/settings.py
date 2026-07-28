from telegram import Update
from telegram.ext import ContextTypes
from services.permissions import admin_only

@admin_only
async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("⚙️ Group settings panel initialized.")

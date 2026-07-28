from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Add to Group", url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=true")],
        [InlineKeyboardButton("Help & Commands", callback_data="help_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = (
        f"👋 Hello! I am **@{Config.BOT_USERNAME}**.\n\n"
        "I am a fast, production-grade group management bot designed to keep your Telegram groups safe, "
        "clean, and organized.\n\n"
        " Add me to your group and promote me to **Administrator** to get started!"
    )
    await update.effective_message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

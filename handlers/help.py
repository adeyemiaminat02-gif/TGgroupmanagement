from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "📖 **Command Reference Guide**\n\n"
        "**Admin Commands:**\n"
        "• `/ban [user_id/reply]` - Ban a user\n"
        "• `/unban [user_id]` - Unban a user\n"
        "• `/mute [user_id/reply]` - Mute a user\n"
        "• `/unmute [user_id/reply]` - Unmute a user\n"
        "• `/kick [user_id/reply]` - Kick a user\n"
        "• `/warn [user_id/reply]` - Warn a user\n"
        "• `/clearwarns [user_id/reply]` - Reset user warnings\n"
        "• `/purge` - Delete messages up to the replied message\n"
        "• `/pin` / `/unpin` - Manage pinned messages\n"
        "• `/setrules [text]` - Configure group rules\n"
        "• `/settings` - Manage bot features\n\n"
        "**User Commands:**\n"
        "• `/rules` - Display group rules\n"
        "• `/report` - Report a message to admins\n"
        "• `/id` - Get user & chat IDs\n"
        "• `/save [name]` / `/get [name]` - Notes management\n"
    )
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown")
    else:
        await update.effective_message.reply_text(text, parse_mode="Markdown")

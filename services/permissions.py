from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int | None = None) -> bool:
    if not update.effective_chat or update.effective_chat.type == "private":
        return False
    
    target_id = user_id or (update.effective_user.id if update.effective_user else 0)
    if not target_id:
        return False

    try:
        member = await context.bot.get_chat_member(update.effective_chat.id, target_id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if not update.effective_chat or update.effective_chat.type == "private":
            await update.effective_message.reply_text("This command can only be used in groups.")
            return
        
        if not await is_admin(update, context):
            await update.effective_message.reply_text("⚠️ This command requires admin permissions.")
            return

        return await func(update, context, *args, **kwargs)
    return wrapper

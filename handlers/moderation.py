from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select, delete
from database import async_session, UserWarning, GroupSettings
from services.permissions import admin_only, is_admin
from services.spam_detector import SpamDetector
from services.utils import extract_user_and_reason
from services.logger import log_event

async def auto_moderation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message or not update.effective_message.text or not update.effective_chat:
        return
    if update.effective_chat.type == "private":
        return
    if await is_admin(update, context):
        return

    text = update.effective_message.text
    is_spam, reason = SpamDetector.check_spam(text)

    if is_spam:
        try:
            await update.effective_message.delete()
        except Exception:
            pass

        msg = f"⚠️ Auto-Mod: Removed message from {update.effective_user.mention_html()}.\nReason: {reason}"
        sent = await context.bot.send_message(update.effective_chat.id, msg, parse_mode="HTML")
        context.job_queue.run_once(lambda ctx: ctx.bot.delete_message(update.effective_chat.id, sent.message_id), 10)
        await log_event(context, f"🛡 Auto-Mod deleted spam from user `{update.effective_user.id}` in `{update.effective_chat.id}`.")

@admin_only
async def warn_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id, reason = extract_user_and_reason(update, context.args)
    if not user_id:
        await update.effective_message.reply_text("❌ Specify a valid user to warn.")
        return

    chat_id = update.effective_chat.id

    async with async_session() as session:
        # Get group warn settings
        stmt_settings = select(GroupSettings).where(GroupSettings.chat_id == chat_id)
        res_settings = await session.execute(stmt_settings)
        settings = res_settings.scalar_one_or_none()
        max_warns = settings.max_warnings if settings else 3

        # Add warning
        new_warn = UserWarning(chat_id=chat_id, user_id=user_id, reason=reason)
        session.add(new_warn)
        await session.commit()

        # Count total warnings
        stmt_count = select(UserWarning).where(UserWarning.chat_id == chat_id, UserWarning.user_id == user_id)
        res_count = await session.execute(stmt_count)
        warn_count = len(res_count.scalars().all())

        if warn_count >= max_warns:
            await context.bot.ban_chat_member(chat_id, user_id)
            await session.execute(delete(UserWarning).where(UserWarning.chat_id == chat_id, UserWarning.user_id == user_id))
            await session.commit()
            await update.effective_message.reply_text(f"🚫 User `{user_id}` reached maximum warnings ({warn_count}/{max_warns}) and was banned.", parse_mode="Markdown")
        else:
            await update.effective_message.reply_text(f"⚠️ User `{user_id}` warned ({warn_count}/{max_warns}).\nReason: {reason}", parse_mode="Markdown")

@admin_only
async def clear_warnings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id, _ = extract_user_and_reason(update, context.args)
    if not user_id:
        await update.effective_message.reply_text("❌ Specify a user.")
        return

    async with async_session() as session:
        await session.execute(delete(UserWarning).where(UserWarning.chat_id == update.effective_chat.id, UserWarning.user_id == user_id))
        await session.commit()

    await update.effective_message.reply_text(f"✅ Cleared warnings for user `{user_id}`.", parse_mode="Markdown")

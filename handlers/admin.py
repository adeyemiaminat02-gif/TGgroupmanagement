from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes
from services.permissions import admin_only
from services.utils import extract_user_and_reason
from services.logger import log_event

@admin_only
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id, reason = extract_user_and_reason(update, context.args)
    if not user_id:
        await update.effective_message.reply_text("❌ Please reply to a user or specify a User ID.")
        return

    await context.bot.ban_chat_member(update.effective_chat.id, user_id)
    await update.effective_message.reply_text(f"🚫 User `{user_id}` has been banned.\nReason: {reason}", parse_mode="Markdown")
    await log_event(context, f"🚫 **Ban**: User `{user_id}` banned in `{update.effective_chat.title}` by `{update.effective_user.id}`.")

@admin_only
async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id, _ = extract_user_and_reason(update, context.args)
    if not user_id:
        await update.effective_message.reply_text("❌ Please specify a User ID to unban.")
        return

    await context.bot.unban_chat_member(update.effective_chat.id, user_id, only_if_banned=True)
    await update.effective_message.reply_text(f"✅ User `{user_id}` unbanned.", parse_mode="Markdown")

@admin_only
async def mute_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id, reason = extract_user_and_reason(update, context.args)
    if not user_id:
        await update.effective_message.reply_text("❌ Please reply to a user or specify a User ID.")
        return

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user_id,
        permissions=ChatPermissions(can_send_messages=False)
    )
    await update.effective_message.reply_text(f"🔇 User `{user_id}` muted.\nReason: {reason}", parse_mode="Markdown")

@admin_only
async def unmute_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id, _ = extract_user_and_reason(update, context.args)
    if not user_id:
        await update.effective_message.reply_text("❌ Please reply to a user or specify a User ID.")
        return

    await context.bot.restrict_chat_member(
        update.effective_chat.id,
        user_id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
    )
    await update.effective_message.reply_text(f"🔊 User `{user_id}` unmuted.", parse_mode="Markdown")

@admin_only
async def purge_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message.reply_to_message:
        await update.effective_message.reply_text("❌ Reply to the starting message you want to purge from.")
        return

    start_id = update.effective_message.reply_to_message.message_id
    current_id = update.effective_message.message_id
    chat_id = update.effective_chat.id

    message_ids = list(range(start_id, current_id + 1))
    
    # Delete in batches of 100 (Telegram API limit)
    for i in range(0, len(message_ids), 100):
        batch = message_ids[i:i + 100]
        try:
            await context.bot.delete_messages(chat_id=chat_id, message_ids=batch)
        except Exception:
            pass

    status_msg = await context.bot.send_message(chat_id, f"🧹 Purged {len(message_ids)} messages.")
    context.job_queue.run_once(lambda ctx: ctx.bot.delete_message(chat_id, status_msg.message_id), 5)

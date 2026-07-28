from telegram import Update
from telegram.ext import ContextTypes

async def report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message.reply_to_message:
        await update.effective_message.reply_text("❌ Reply to the message you wish to report.")
        return

    reported_msg = update.effective_message.reply_to_message
    admins = await context.bot.get_chat_administrators(update.effective_chat.id)

    text = f"🚨 **User Report**\n\nReported by: {update.effective_user.mention_html()}\nTarget: {reported_msg.from_user.mention_html()}"

    for admin in admins:
        if not admin.user.is_bot:
            try:
                await context.bot.send_message(admin.user.id, text, parse_mode="HTML")
            except Exception:
                pass

    await update.effective_message.reply_text("✅ Report forwarded to group administrators.")

from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select
from database import async_session, GroupSettings
from services.permissions import admin_only

async def get_rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    async with async_session() as session:
        stmt = select(GroupSettings).where(GroupSettings.chat_id == chat_id)
        res = await session.execute(stmt)
        settings = res.scalar_one_or_none()

    if settings and settings.rules_text:
        await update.effective_message.reply_text(f"📜 **Group Rules:**\n\n{settings.rules_text}", parse_mode="Markdown")
    else:
        await update.effective_message.reply_text("No rules configured for this group yet.")

@admin_only
async def set_rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.effective_message.reply_text("Usage: `/setrules [Rules text]`", parse_mode="Markdown")
        return

    rules = " ".join(context.args)
    chat_id = update.effective_chat.id

    async with async_session() as session:
        stmt = select(GroupSettings).where(GroupSettings.chat_id == chat_id)
        res = await session.execute(stmt)
        settings = res.scalar_one_or_none()

        if not settings:
            settings = GroupSettings(chat_id=chat_id, rules_text=rules)
            session.add(settings)
        else:
            settings.rules_text = rules

        await session.commit()

    await update.effective_message.reply_text("✅ Group rules updated successfully!")

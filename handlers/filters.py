from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select, delete
from database import async_session, Filter
from services.permissions import admin_only

@admin_only
async def add_filter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.effective_message.reply_text("Usage: `/filter [keyword] [reply_text]`", parse_mode="Markdown")
        return

    keyword = context.args[0].lower()
    reply_text = " ".join(context.args[1:])
    chat_id = update.effective_chat.id

    async with async_session() as session:
        new_filter = Filter(chat_id=chat_id, keyword=keyword, reply_text=reply_text)
        session.add(new_filter)
        await session.commit()

    await update.effective_message.reply_text(f"✅ Filter created for keyword: `{keyword}`", parse_mode="Markdown")

async def check_filters(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message or not update.effective_message.text:
        return

    text = update.effective_message.text.lower()
    chat_id = update.effective_chat.id

    async with async_session() as session:
        stmt = select(Filter).where(Filter.chat_id == chat_id)
        res = await session.execute(stmt)
        filters = res.scalars().all()

        for f in filters:
            if f.keyword in text:
                await update.effective_message.reply_text(f.reply_text)
                break

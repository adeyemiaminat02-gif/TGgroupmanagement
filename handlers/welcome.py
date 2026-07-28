from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select
from database import async_session, GroupSettings

async def welcome_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    
    async with async_session() as session:
        stmt = select(GroupSettings).where(GroupSettings.chat_id == chat_id)
        res = await session.execute(stmt)
        settings = res.scalar_one_or_none()

    if settings and not settings.welcome_enabled:
        return

    welcome_template = settings.welcome_text if settings else "Welcome {mention} to {chat}!"
    clean_welcome = settings.clean_welcome if settings else True

    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        
        msg_text = welcome_template.format(
            mention=member.mention_html(),
            first=member.first_name,
            chat=update.effective_chat.title
        )
        
        sent = await context.bot.send_message(chat_id, msg_text, parse_mode="HTML")
        
        if clean_welcome:
            context.job_queue.run_once(
                lambda ctx: ctx.bot.delete_message(chat_id, sent.message_id),
                30
            )

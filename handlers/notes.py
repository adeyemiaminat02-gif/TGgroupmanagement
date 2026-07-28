from telegram import Update
from telegram.ext import ContextTypes
from sqlalchemy import select, delete
from database import async_session, Note
from services.permissions import admin_only

@admin_only
async def save_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.effective_message.reply_text("Usage: `/save [note_name]` (as reply or with text)", parse_mode="Markdown")
        return

    name = context.args[0].lower()
    chat_id = update.effective_chat.id
    reply = update.effective_message.reply_to_message

    file_id, media_type, content = None, "text", None

    if reply:
        if reply.photo:
            file_id, media_type = reply.photo[-1].file_id, "photo"
            content = reply.caption
        elif reply.document:
            file_id, media_type = reply.document.file_id, "document"
            content = reply.caption
        elif reply.sticker:
            file_id, media_type = reply.sticker.file_id, "sticker"
        else:
            content = reply.text
    else:
        content = " ".join(context.args[1:])

    async with async_session() as session:
        # Delete existing note with same name if any
        await session.execute(delete(Note).where(Note.chat_id == chat_id, Note.name == name))
        new_note = Note(chat_id=chat_id, name=name, file_id=file_id, media_type=media_type, content=content)
        session.add(new_note)
        await session.commit()

    await update.effective_message.reply_text(f"📌 Saved note `#`", parse_mode="Markdown")

async def get_note(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        return
    name = context.args[0].lower()
    chat_id = update.effective_chat.id

    async with async_session() as session:
        stmt = select(Note).where(Note.chat_id == chat_id, Note.name == name)
        res = await session.execute(stmt)
        note = res.scalar_one_or_none()

    if not note:
        return

    if note.media_type == "photo":
        await update.effective_message.reply_photo(photo=note.file_id, caption=note.content)
    elif note.media_type == "document":
        await update.effective_message.reply_document(document=note.file_id, caption=note.content)
    elif note.media_type == "sticker":
        await update.effective_message.reply_sticker(sticker=note.file_id)
    else:
        await update.effective_message.reply_text(note.content)

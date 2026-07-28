from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def send_verification_challenge(chat_id: int, user_id: int, first_name: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[
        InlineKeyboardButton("✅ Verify Here", callback_data=f"verify_{user_id}")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = await context.bot.send_message(
        chat_id=chat_id,
        text=f"👋 Welcome {first_name}! Please click the button below within 120s to verify you are human.",
        reply_markup=reply_markup
    )
    
    # Track timeout job
    context.job_queue.run_once(
        verification_timeout_callback,
        120,
        data={"chat_id": chat_id, "user_id": user_id, "message_id": msg.message_id},
        name=f"verify_{chat_id}_{user_id}"
    )

async def verification_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    target_user_id = int(query.data.split("_")[1])

    if query.from_user.id != target_user_id:
        await query.answer("❌ This verification button is not for you.", show_alert=True)
        return

    # Cancel pending timeout job
    jobs = context.job_queue.get_jobs_by_name(f"verify_{update.effective_chat.id}_{target_user_id}")
    for job in jobs:
        job.schedule_removal()

    await query.answer("✅ Verification successful! Welcome!")
    await query.message.delete()

async def verification_timeout_callback(context: ContextTypes.DEFAULT_TYPE) -> None:
    job_data = context.job.data
    chat_id = job_data["chat_id"]
    user_id = job_data["user_id"]
    
    try:
        await context.bot.kick_chat_member(chat_id, user_id)
        await context.bot.unban_chat_member(chat_id, user_id) # Kick only
        await context.bot.delete_message(chat_id, job_data["message_id"])
    except Exception:
        pass

from telegram import Update

def extract_user_and_reason(update: Update, args: list[str]) -> tuple[int | None, str]:
    """Extract target user ID and reason from command reply or text arguments."""
    reason = "No reason provided."
    user_id = None

    if update.effective_message.reply_to_message:
        user_id = update.effective_message.reply_to_message.from_user.id
        if args:
            reason = " ".join(args)
    elif args:
        try:
            user_id = int(args[0])
            if len(args) > 1:
                reason = " ".join(args[1:])
        except ValueError:
            pass

    return user_id, reason

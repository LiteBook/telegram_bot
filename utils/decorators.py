# utils/decorators.py
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

async def admin_only(func):
    """এই ডেকোরেটর নিশ্চিত করে যে শুধুমাত্র গ্রুপের অ্যাডমিনরাই কমান্ডটি ব্যবহার করতে পারবে।"""
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat

        if chat.type == 'private':
            return await func(update, context, *args, **kwargs)
        
        try:
            chat_admins = await context.bot.get_chat_administrators(chat.id)
            admin_ids = {admin.user.id for admin in chat_admins}
            
            if user.id in admin_ids:
                return await func(update, context, *args, **kwargs)
            else:
                await update.message.reply_text("⛔️ দুঃখিত, এই কমান্ডটি শুধুমাত্র অ্যাডমিনদের জন্য।")
        except Exception as e:
            print(f"Error checking admin status: {e}")
            await update.message.reply_text("অ্যাডমিন স্ট্যাটাস চেক করতে সমস্যা হচ্ছে।")
    return wrapped

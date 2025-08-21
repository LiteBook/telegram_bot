# main.py
import logging
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ChatMemberHandler, filters
)
import config
import database as db
from handlers import basic, moderation, ai_chat, utility_fun

# লগিং কনফিগার
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def main() -> None:
    """বট স্টার্ট করে।"""
    db.init_db()
    
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    
    # --- Basic Handlers ---
    application.add_handler(CommandHandler("start", lambda u, c: u.message.reply_text("হ্যালো! আমি আপনার গ্রুপ ম্যানেজার বট। /help লিখে আমার কমান্ডগুলো দেখুন।")))
    application.add_handler(CommandHandler("help", basic.help_command))
    application.add_handler(CommandHandler("rules", basic.rules_command))
    application.add_handler(CommandHandler("info", basic.info_command))
    application.add_handler(ChatMemberHandler(basic.welcome_member, ChatMemberHandler.CHAT_MEMBER))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, basic.goodbye_member))
    
    # --- Moderation Handlers ---
    application.add_handler(CommandHandler("ban", moderation.ban_command))
    application.add_handler(CommandHandler("setwelcome", moderation.set_welcome_command))
    # Add other moderation commands here (/kick, /mute, /setrules etc.)
    
    # --- Utility & Fun Handlers ---
    application.add_handler(CommandHandler("weather", utility_fun.weather_command))
    application.add_handler(CommandHandler("joke", utility_fun.joke_command))
    
    # --- AI Handlers ---
    application.add_handler(CommandHandler("ask", ai_chat.ask_command))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & (filters.Entity("mention") | filters.REPLY), 
        ai_chat.direct_reply_handler
    ))

    # --- General Message Handlers (should be last) ---
    # খারাপ শব্দ ফিল্টার এবং মেসেজ কাউন্টার
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, moderation.bad_word_filter), group=1)
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, basic.message_counter), group=2)
    
    application.add_error_handler(lambda u, c: logger.warning('Update "%s" caused error "%s"', u, c.error))

    print("বট চলছে...")
    application.run_polling()

if __name__ == '__main__':
    main()

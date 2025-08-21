# handlers/moderation.py
from telegram import Update
from telegram.ext import ContextTypes
from utils.decorators import admin_only
import database as db

BAD_WORDS = {"gali", "badword", "abuse"} # আপনার প্রয়োজন মতো শব্দ যোগ করুন

async def bad_word_filter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """খারাপ শব্দ ফিল্টার করে এবং ওয়ার্নিং দেয়।"""
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    if any(word in text for word in BAD_WORDS):
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        await update.message.delete()
        
        warning_count = db.add_warning(user.id, chat_id)
        
        await update.message.reply_text(
            f"🚫 {user.mention_html()}, খারাপ শব্দ ব্যবহার করা নিষেধ।\n"
            f"আপনার ওয়ার্নিং: {warning_count}/3",
            parse_mode='HTML'
        )

        if warning_count >= 3:
            try:
                await context.bot.ban_chat_member(chat_id, user.id)
                await update.message.reply_text(f"🚫 {user.mention_html()} কে ৩ বার ওয়ার্নিং দেওয়ার কারণে ব্যান করা হয়েছে।", parse_mode='HTML')
            except Exception as e:
                await update.message.reply_text(f"ব্যান করতে সমস্যা হয়েছে: {e}")

@admin_only
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """একজন ইউজারকে ব্যান করে।"""
    if not update.message.reply_to_message:
        await update.message.reply_text("ব্যান করার জন্য কোনো মেসেজে রিপ্লাই দিন।")
        return
    
    user_to_ban = update.message.reply_to_message.from_user
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user_to_ban.id)
        await update.message.reply_text(f"✅ {user_to_ban.first_name} কে ব্যান করা হয়েছে।")
    except Exception as e:
        await update.message.reply_text(f"❌ ব্যান করতে সমস্যা হয়েছে: {e}")

@admin_only
async def set_welcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """কাস্টম ওয়েলকাম মেসেজ সেট করে।"""
    message = ' '.join(context.args)
    if not message:
        await update.message.reply_text("ব্যবহার: /setwelcome Welcome {user} to {group}!")
        return
    
    db.set_group_setting(update.effective_chat.id, 'welcome_message', message)
    await update.message.reply_text("✅ নতুন ওয়েলকাম মেসেজ সেট করা হয়েছে।")

# handlers/basic.py
from telegram import Update
from telegram.ext import ContextTypes
import database as db
from datetime import datetime

async def welcome_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """নতুন মেম্বার জয়েন করলে স্বাগত জানায় এবং ডাটাবেসে লগ করে।"""
    new_members = update.message.new_chat_members
    chat_id = update.effective_chat.id
    
    welcome_message_template = db.get_group_setting(chat_id, 'welcome_message')
    
    for member in new_members:
        if not member.is_bot:
            db.log_user_join(member.id, chat_id) # ডাটাবেসে লগ
            user_mention = member.mention_html()
            message = welcome_message_template.format(user=user_mention, group=update.effective_chat.title)
            await update.message.reply_text(message, parse_mode='HTML')

async def goodbye_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """কেউ গ্রুপ লিভ করলে বিদায় জানায়।"""
    left_member = update.message.left_chat_member
    if left_member:
        await update.message.reply_text(f"বিদায়, {left_member.first_name}! আবার দেখা হবে।")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help কমান্ডের মাধ্যমে সব কমান্ডের তালিকা দেখায়।"""
    help_text = """
    🤖 **All-in-One Bot Commands** 🤖

    **Basic**
    /help - এই সাহায্য বার্তা দেখুন
    /rules - গ্রুপের নিয়মাবলী
    /info - আপনার তথ্য দেখুন

    **Moderation (Admin Only)**
    /ban `[reply]` - ইউজারকে ব্যান করুন
    /kick `[reply]` - ইউজারকে কিক করুন
    /setwelcome `[message]` - ওয়েলকাম মেসেজ সেট করুন
    /setrules `[message]` - নিয়মাবলী সেট করুন

    **Utility & Fun**
    /weather `[city]` - শহরের আবহাওয়া
    /joke - একটি কৌতুক শুনুন

    **AI Features**
    /ask `[question]` - AI কে প্রশ্ন করুন
    `@bot_username` - বটের সাথে কথা বলুন
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """গ্রুপের নিয়মাবলী পাঠায়।"""
    rules = db.get_group_setting(update.effective_chat.id, 'rules')
    await update.message.reply_text(f"📜 **গ্রুপের নিয়মাবলী:**\n\n{rules}", parse_mode='Markdown')

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ইউজারের তথ্য দেখায়।"""
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    user_data = db.get_user_info(user.id, chat_id)
    join_date_str = "N/A"
    message_count = "N/A"
    if user_data:
        join_timestamp, msg_count = user_data
        if join_timestamp:
            join_date_str = datetime.fromtimestamp(join_timestamp).strftime('%d %b %Y')
        message_count = msg_count

    info_text = (
        f"👤 **User Info**\n\n"
        f"**Name:** {user.full_name}\n"
        f"**Username:** @{user.username}\n"
        f"**ID:** `{user.id}`\n"
        f"**Joined:** {join_date_str}\n"
        f"**Messages:** {message_count}"
    )
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def message_counter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """সব মেসেজ লগ করে।"""
    if update.message and not update.effective_user.is_bot:
        db.log_message(update.effective_user.id, update.effective_chat.id)

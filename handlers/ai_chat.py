# handlers/ai_chat.py
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes
from config import OPENROUTER_API_BASE, OPENROUTER_HEADERS

async def get_ai_response(prompt: str) -> str:
    """OpenRouter API ব্যবহার করে AI থেকে উত্তর নিয়ে আসে।"""
    payload = {
        "model": "mistralai/mistral-7b-instruct:free", # ফ্রি মডেল ব্যবহার করা হচ্ছে
        "messages": [{"role": "user", "content": prompt}],
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{OPENROUTER_API_BASE}/chat/completions", headers=OPENROUTER_HEADERS, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                else:
                    return f"AI Error: {await response.text()}"
    except Exception as e:
        return f"An exception occurred: {e}"

async def ask_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/ask কমান্ড হ্যান্ডেল করে।"""
    question = ' '.join(context.args)
    if not question:
        await update.message.reply_text("🤔 অনুগ্রহ করে আপনার প্রশ্নটি লিখুন। যেমন: /ask মহাবিশ্বের রহস্য কী?")
        return
        
    await update.message.reply_chat_action('typing')
    response = await get_ai_response(question)
    await update.message.reply_text(response, parse_mode='Markdown')

async def direct_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """বটকে mention করলে বা তার মেসেজে reply দিলে AI উত্তর দেবে।"""
    message_text = update.message.text
    bot_username = context.bot.username

    if (f"@{bot_username}" in message_text) or (update.message.reply_to_message and update.message.reply_to_message.from_user.username == bot_username):
        prompt = message_text.replace(f"@{bot_username}", "").strip()
        if not prompt: return

        await update.message.reply_chat_action('typing')
        response = await get_ai_response(f"A user said to you: '{prompt}'. Respond in a friendly, helpful, and human-like way in Bengali.")
        await update.message.reply_text(response)

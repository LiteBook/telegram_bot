# handlers/utility_fun.py
import aiohttp
from telegram import Update
from telegram.ext import ContextTypes
from config import WEATHER_API_KEY

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """শহরের আবহাওয়া দেখায়।"""
    city = ' '.join(context.args)
    if not city:
        await update.message.reply_text("ব্যবহার: /weather [city_name]")
        return

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    weather_info = (
                        f"🏙️ **Weather in {data['name']}**\n\n"
                        f"🌡️ Temperature: {data['main']['temp']}°C\n"
                        f"🤔 Condition: {data['weather'][0]['description'].capitalize()}\n"
                        f"💧 Humidity: {data['main']['humidity']}%\n"
                        f"💨 Wind Speed: {data['wind']['speed']} m/s"
                    )
                    await update.message.reply_text(weather_info, parse_mode='Markdown')
                else:
                    await update.message.reply_text("শহরটি খুঁজে পাওয়া যায়নি।")
    except Exception as e:
        await update.message.reply_text(f"আবহাওয়া জানতে সমস্যা হচ্ছে: {e}")

async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """একটি কৌতুক পাঠায়।"""
    url = "https://v2.jokeapi.dev/joke/Any?type=single"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if not data['error']:
                    await update.message.reply_text(data['joke'])
                else:
                    await update.message.reply_text("দুঃখিত, এখন কোনো কৌতুক পাচ্ছি না।")
    except Exception as e:
        await update.message.reply_text(f"কিছু একটা সমস্যা হয়েছে: {e}")

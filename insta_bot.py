import os
import threading
import yt_dlp
import asyncio
import subprocess
import sys
import time
import uuid # 🔍 NAYA: Inline mode ke liye unique ID banane ke liye
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultVideo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, InlineQueryHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
INSTA_LINK = "https://instagram.com/rahul_kumar_raj_592"

ADMIN_ID = -1003901141197 
OWNER_ID = 5868140731

app = Flask(__name__)

@app.route('/')
def home():
    return "Ninja Bot is Running perfectly! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# 🧠 SMART MEMORY & STORAGE
active_users = set()
user_languages = {} 
user_cooldowns = {} 

COOLDOWN_TIME = 60 

# 🌍 DICTIONARY
LANG = {
    "en": {
        "welcome": "🚀 <b>Insta Ninja Downloader v2.0</b> 🚀\n\nHello! I can download any Instagram Reel in high quality. ⚡\n\n🎯 <b>Just send me the reel link!</b>\n\n👇 <b>Follow the Developer:</b>",
        "invalid": "⚠️ <b>Friend, please send a valid Instagram link!</b>",
        "processing": "⚙️ <b>Extracting video from server...</b>",
        "sending": "📤 <b>Sending to Telegram... 🚀</b>",
        "success": "🎬 <b>Download Successful!</b> ✅\n\n⚡ <i>Powered by Rahul Kumar Raj</i>",
        "error": "❌ <b>Error:</b> Instagram blocked the request or the reel is private.",
        "button_follow": "💖 Follow Rahul Kumar Raj 💖",
        "cooldown": "⏳ <b>Spam Protection:</b> Please wait {time} seconds before sending another link!" 
    },
    "hi": {
        "welcome": "🚀 <b>Insta Ninja Downloader v2.0</b> 🚀\n\nनमस्ते! मैं किसी भी Instagram Reel को हाई क्वालिटी में डाउनलोड कर सकता हूँ। ⚡\n\n🎯 <b>बस मुझे रील का लिंक भेजें!</b>\n\n👇 <b>Developer को सपोर्ट करने के लिए फॉलो करें:</b>",
        "invalid": "⚠️ <b>दोस्त, कृपया सही Instagram लिंक भेजें!</b>",
        "processing": "⚙️ <b>सर्वर से वीडियो निकाला जा रहा है...</b>",
        "sending": "📤 <b>टेलीग्राम पर भेजा जा रहा है... 🚀</b>",
        "success": "🎬 <b>Download Successful!</b> ✅\n\n⚡ <i>Powered by Rahul Kumar Raj</i>",
        "error": "❌ <b>Error:</b> Instagram ने रिक्वेस्ट रोक दी है या रील प्राइवेट है।",
        "button_follow": "💖 Follow Rahul Kumar Raj 💖",
        "cooldown": "⏳ <b>स्पैम अलर्ट:</b> कृपया अगला लिंक भेजने से पहले {time} सेकंड प्रतीक्षा करें!" 
    }
}

# 📥 NORMAL DOWNLOAD LOGIC
def download_reel_sync(url, file_path):
    ydl_opts = {
        'outtmpl': file_path,
        'format': 'best',
        'quiet': True,
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# 🔍 INLINE MODE LOGIC (Bina download kiye direct link nikalna)
def extract_direct_link_sync(url):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

# 🔄 AUTO-UPDATE
async def update_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        return
    status_msg = await update.message.reply_text("⚙️ <b>yt-dlp का नया वर्ज़न ढूँढा जा रहा है...</b>", parse_mode='HTML')
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], check=True)
        await status_msg.edit_text("✅ <b>अपडेट सक्सेसफुल!</b> 🚀\nरीस्टार्ट हो रहा हूँ...", parse_mode='HTML')
        await asyncio.sleep(2)
        os._exit(0)
    except Exception as e:
        await status_msg.edit_text(f"❌ <b>अपडेट फेल हो गया:</b> {e}", parse_mode='HTML')

# 🚀 START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    if user_id not in active_users:
        active_users.add(user_id)
        try:
            alert_msg = f"🚨 <b>New User Alert!</b>\n👤 Naam: {user_name}\n🆔 ID: <code>{user_id}</code>\n🚀 Naya banda bot par aaya hai!"
            await context.bot.send_message(chat_id=ADMIN_ID, text=alert_msg, parse_mode='HTML')
        except Exception:
            pass

    keyboard = [
        [InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_hi"),
         InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌍 <b>Please select your language / अपनी भाषा चुनें:</b>", parse_mode='HTML', reply_markup=reply_markup)

# 🔘 LANGUAGE BUTTON
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data

    if data == "lang_hi":
        user_languages[user_id] = "hi"
        lang = "hi"
    elif data == "lang_en":
        user_languages[user_id] = "en"
        lang = "en"
    
    keyboard = [[InlineKeyboardButton(LANG[lang]["button_follow"], url=INSTA_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(LANG[lang]["welcome"], parse_mode='HTML', reply_markup=reply_markup)

# 💬 NORMAL CHAT HANDLER
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    url = update.message.text
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    lang = user_languages.get(user_id, "hi")

    # Anti-Spam Cooldown
    if user_id != OWNER_ID: 
        current_time = time.time()
        if user_id in user_cooldowns:
            time_passed = current_time - user_cooldowns[user_id]
            if time_passed < COOLDOWN_TIME:
                remaining_time = int(COOLDOWN_TIME - time_passed)
                cooldown_msg = LANG[lang]["cooldown"].replace("{time}", str(remaining_time))
                await update.message.reply_text(cooldown_msg, parse_mode='HTML')
                return 
        user_cooldowns[user_id] = current_time

    if user_id != OWNER_ID and "instagram.com" in url:
        try:
            spy_msg = f"🕵️‍♂️ <b>Spy Log!</b>\n👤 Naam: {user_name}\n🔗 <b>Link:</b> {url}"
            await context.bot.send_message(chat_id=ADMIN_ID, text=spy_msg, parse_mode='HTML', disable_web_page_preview=True)
        except Exception:
            pass

    if "instagram.com" not in url:
        await update.message.reply_text(LANG[lang]["invalid"], parse_mode='HTML')
        return

    status_msg = await update.message.reply_text(LANG[lang]["processing"], parse_mode='HTML')
    await context.bot.send_chat_action(chat_id=chat_id, action='upload_video')

    file_path = f"reel_{chat_id}.mp4"
    max_retries = 3
    download_success = False

    for attempt in range(max_retries):
        try:
            await asyncio.to_thread(download_reel_sync, url, file_path)
            if os.path.exists(file_path):
                download_success = True
                break
        except Exception:
            await asyncio.sleep(2)

    if not download_success:
        await status_msg.edit_text(LANG[lang]["error"], parse_mode='HTML')
        return

    try:
        await status_msg.edit_text(LANG[lang]["sending"], parse_mode='HTML')
        keyboard = [[InlineKeyboardButton(LANG[lang]["button_follow"], url=INSTA_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open(file_path, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                caption=LANG[lang]["success"],
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        await status_msg.delete()

    except Exception:
        await status_msg.edit_text(LANG[lang]["error"], parse_mode='HTML')
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# 👇 INLINE QUERY HANDLER (Kahin se bhi video bhejne ke liye)
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query

    if not query or "instagram.com" not in query:
        return

    try:
        # Direct URL nikalo bina download kiye
        info = await asyncio.to_thread(extract_direct_link_sync, query)
        
        if not info or 'url' not in info:
            return

        video_url = info['url']
        # Agar thumbnail nahi mila to default Instagram ka logo dikhayega
        thumb_url = info.get('thumbnail', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/132px-Instagram_logo_2016.svg.png')
        
        keyboard = [[InlineKeyboardButton("🔥 Created by Rahul Kumar Raj 🔥", url=INSTA_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        result = [
            InlineQueryResultVideo(
                id=str(uuid.uuid4()),
                video_url=video_url,
                mime_type="video/mp4",
                thumb_url=thumb_url,
                title="🎬 Send Instagram Reel",
                description="Click here to send video!",
                caption="⚡ <i>Powered by Insta Ninja</i>",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        ]
        
        await update.inline_query.answer(result, cache_time=10)

    except Exception as e:
        print(f"Inline Error: {e}")

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: BOT_TOKEN missing!")
        return

    threading.Thread(target=run_web, daemon=True).start()
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("update", update_bot))
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # 🎯 Naya Inline Handler Add Kiya
    application.add_handler(InlineQueryHandler(inline_query))
    
    print("🚀 Bot is LIVE with Inline Mode & Anti-Spam!")
    application.run_polling()

if __name__ == '__main__':
    main()

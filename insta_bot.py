import os
import threading
import yt_dlp
import asyncio
import subprocess
import sys
import time
import uuid 
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
total_downloads = 0 
COOLDOWN_TIME = 60 

# 🌍 DICTIONARY
LANG = {
    "en": {
        "welcome": "🚀 <b>Insta Ninja Downloader v2.0</b> 🚀\n\nHello! I can download any Instagram Reel, Photo, Story & Highlight in high quality. ⚡\n\n🎯 <b>Just send me the link!</b>\n\n👇 <b>Follow the Developer:</b>",
        "invalid": "⚠️ <b>Friend, please send a valid Instagram link!</b>",
        "processing": "⚙️ <b>Extracting media from server...</b>",
        "sending": "📤 <b>Sending to Telegram... 🚀</b>",
        "success": "🎬 <b>Download Successful!</b> ✅\n\n⚡ <i>Powered by Rahul Kumar Raj</i>",
        "error": "❌ <b>Error:</b> Instagram blocked the request, or cookies are missing for this private story.",
        "button_follow": "💖 Follow Rahul Kumar Raj 💖",
        "cooldown": "⏳ <b>Spam Protection:</b> Please wait {time} seconds!" 
    },
    "hi": {
        "welcome": "🚀 <b>Insta Ninja Downloader v2.0</b> 🚀\n\nनमस्ते! मैं किसी भी Instagram Reel, Photo, Story या Highlight को हाई क्वालिटी में डाउनलोड कर सकता हूँ। ⚡\n\n🎯 <b>बस मुझे लिंक भेजें!</b>\n\n👇 <b>Developer को फॉलो करें:</b>",
        "invalid": "⚠️ <b>दोस्त, कृपया सही Instagram लिंक भेजें!</b>",
        "processing": "⚙️ <b>सर्वर से मीडिया निकाला जा रहा है...</b>",
        "sending": "📤 <b>टेलीग्राम पर भेजा जा रहा है... 🚀</b>",
        "success": "🎬 <b>Download Successful!</b> ✅\n\n⚡ <i>Powered by Rahul Kumar Raj</i>",
        "error": "❌ <b>Error:</b> Instagram ने रिक्वेस्ट रोक दी है, या इस स्टोरी के लिए कुकीज़ की आवश्यकता है।",
        "button_follow": "💖 Follow Rahul Kumar Raj 💖",
        "cooldown": "⏳ <b>स्पैम अलर्ट:</b> कृपया {time} सेकंड प्रतीक्षा करें!" 
    }
}

# 📥 ADVANCED DOWNLOAD LOGIC (Reels, Photos, Stories, Highlights)
def download_insta_media_sync(url, chat_id):
    ydl_opts = {
        'outtmpl': f"dl_{chat_id}_%(id)s.%(ext)s",
        'format': 'best',
        'quiet': True,
        'noplaylist': False, # Highlight के सभी वीडियो डाउनलोड करने के लिए 
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
    }
    
    # ऑटोमैटिक कुकीज़ डिटेक्शन 
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = 'cookies.txt'
        
    downloaded_files = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        if 'entries' in info:
            for entry in info['entries']:
                if entry:
                    downloaded_files.append(ydl.prepare_filename(entry))
        else:
            downloaded_files.append(ydl.prepare_filename(info))
            
    return downloaded_files

# 🔍 INLINE MODE LOGIC 
def extract_direct_link_sync(url):
    ydl_opts = {'format': 'best', 'quiet': True, 'noplaylist': True}
    if os.path.exists("cookies.txt"):
        ydl_opts['cookiefile'] = 'cookies.txt'
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

# 🔄 AUTO-UPDATE
async def update_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    status_msg = await update.message.reply_text("⚙️ <b>अपडेट...</b>", parse_mode='HTML')
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], check=True)
        await status_msg.edit_text("✅ <b>अपडेट सक्सेसफुल!</b> 🚀", parse_mode='HTML')
        await asyncio.sleep(2)
        os._exit(0)
    except Exception: pass

# 📊 ADMIN STATS
async def get_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    stats_msg = (
        "📊 <b>Admin Live Dashboard</b> 📊\n\n"
        f"👥 <b>टोटल यूज़र्स:</b> {len(active_users)}\n"
        f"📥 <b>टोटल डाउनलोड्स:</b> {total_downloads}\n\n"
        "🟢 <b>सर्वर स्टेटस:</b> 100% Online 🚀"
    )
    await update.message.reply_text(stats_msg, parse_mode='HTML')

# 📢 ADMIN BROADCAST
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    message_to_send = update.message.text.replace("/broadcast", "").strip()
    if not message_to_send:
        await update.message.reply_text("⚠️ <b>प्लीज़ कमांड के साथ मैसेज टाइप करें!</b>", parse_mode='HTML')
        return
    if not active_users: return
    await update.message.reply_text(f"🚀 <b>ब्रॉडकास्ट शुरू...</b>", parse_mode='HTML')
    s_count = 0
    f_count = 0
    for uid in list(active_users):
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 <b>Admin Update</b> 📢\n\n{message_to_send}", parse_mode='HTML')
            s_count += 1
            await asyncio.sleep(0.1) 
        except Exception: f_count += 1
    await update.message.reply_text(f"✅ <b>कम्पलीट!</b>\n🟢 सक्सेस: {s_count}\n🔴 फेल: {f_count}", parse_mode='HTML')

# 🚀 START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_users:
        active_users.add(user_id)
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🚨 <b>New User!</b>\n👤 Naam: {update.effective_user.first_name}\n🆔: <code>{user_id}</code>", parse_mode='HTML')
        except Exception: pass
    keyboard = [[InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_hi"), InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]]
    await update.message.reply_text("🌍 <b>Please select your language:</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# 🔘 LANGUAGE BUTTON
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    lang = "hi" if query.data == "lang_hi" else "en"
    user_languages[user_id] = lang
    keyboard = [[InlineKeyboardButton(LANG[lang]["button_follow"], url=INSTA_LINK)]]
    await query.edit_message_text(LANG[lang]["welcome"], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# 💬 NORMAL CHAT HANDLER
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    raw_url = update.message.text
    user_id = update.effective_user.id
    global total_downloads 

    if user_id not in active_users: active_users.add(user_id)
    lang = user_languages.get(user_id, "hi")

    if user_id != OWNER_ID: 
        current_time = time.time()
        if user_id in user_cooldowns and (current_time - user_cooldowns[user_id]) < COOLDOWN_TIME:
            rem = int(COOLDOWN_TIME - (current_time - user_cooldowns[user_id]))
            await update.message.reply_text(LANG[lang]["cooldown"].replace("{time}", str(rem)), parse_mode='HTML')
            return 
        user_cooldowns[user_id] = current_time

    # Stories और Highlights के URL क्लीनिंग लॉजिक को फिक्स किया गया है
    if "/s/" in raw_url or "/stories/" in raw_url:
        clean_url = raw_url
    else:
        clean_url = raw_url.split("?")[0] if "instagram.com" in raw_url else raw_url

    if "instagram.com" not in clean_url:
        await update.message.reply_text(LANG[lang]["invalid"], parse_mode='HTML')
        return

    status_msg = await update.message.reply_text(LANG[lang]["processing"], parse_mode='HTML')
    await context.bot.send_chat_action(chat_id=chat_id, action='upload_document')

    downloaded_files = []
    for attempt in range(3):
        try:
            downloaded_files = await asyncio.to_thread(download_insta_media_sync, clean_url, chat_id)
            if downloaded_files: break
        except Exception: await asyncio.sleep(2)

    if not downloaded_files:
        await status_msg.edit_text(LANG[lang]["error"], parse_mode='HTML')
        return

    try:
        await status_msg.edit_text(LANG[lang]["sending"], parse_mode='HTML')
        keyboard = [[InlineKeyboardButton(LANG[lang]["button_follow"], url=INSTA_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        for file_path in downloaded_files:
            if os.path.exists(file_path):
                ext = file_path.split('.')[-1].lower()
                with open(file_path, 'rb') as media_file:
                    if ext in ['jpg', 'jpeg', 'png', 'webp']:
                        await context.bot.send_photo(chat_id=chat_id, photo=media_file, caption=LANG[lang]["success"], parse_mode='HTML', reply_markup=reply_markup)
                    else:
                        await context.bot.send_video(chat_id=chat_id, video=media_file, caption=LANG[lang]["success"], parse_mode='HTML', reply_markup=reply_markup)
                os.remove(file_path)
                
        await status_msg.delete()
        total_downloads += 1
    except Exception:
        await status_msg.edit_text(LANG[lang]["error"], parse_mode='HTML')
    finally:
        for file_path in downloaded_files:
            if os.path.exists(file_path): os.remove(file_path)

# 👇 INLINE QUERY HANDLER 
async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query or "instagram.com" not in query: return
    clean_query = query.split("?")[0]
    user_id = update.inline_query.from_user.id
    if user_id not in active_users: active_users.add(user_id)
    try:
        info = await asyncio.to_thread(extract_direct_link_sync, clean_query)
        if not info or 'url' not in info: return
        video_url = info['url']
        thumb_url = info.get('thumbnail', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/132px-Instagram_logo_2016.svg.png')
        keyboard = [[InlineKeyboardButton("🔥 Created by Rahul Kumar Raj 🔥", url=INSTA_LINK)]]
        result = [InlineQueryResultVideo(id=str(uuid.uuid4()), video_url=video_url, mime_type="video/mp4", thumb_url=thumb_url, title="🎬 Send Media", description="Click to send!", caption="⚡ <i>Powered by Insta Ninja</i>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))]
        await update.inline_query.answer(result, cache_time=10)
        global total_downloads
        total_downloads += 1
    except Exception: pass

def main():
    if not TELEGRAM_BOT_TOKEN: return
    threading.Thread(target=run_web, daemon=True).start()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("update", update_bot))
    application.add_handler(CommandHandler("stats", get_stats)) 
    application.add_handler(CommandHandler("broadcast", broadcast)) 
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(InlineQueryHandler(inline_query))
    print("🚀 Bot is LIVE with Full Media Support!")
    application.run_polling()

if __name__ == '__main__':
    main()

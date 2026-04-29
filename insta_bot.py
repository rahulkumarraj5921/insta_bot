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
pending_links = {} 
total_downloads = 0 

COOLDOWN_TIME = 60 

LANG = {
    "en": {
        "welcome": "🚀 <b>Insta Ninja Downloader v2.0</b> 🚀\n\nHello! I can download any Instagram Reel in high quality. ⚡\n\n🎯 <b>Just send me the reel link!</b>\n\n👇 <b>Follow the Developer:</b>",
        "invalid": "⚠️ <b>Friend, please send a valid Instagram link!</b>",
        "processing": "⚙️ <b>Extracting video from server...</b>",
        "sending": "📤 <b>Sending to Telegram... 🚀</b>",
        "success": "🎬 <b>Download Successful!</b> ✅\n\n⚡ <i>Powered by Rahul Kumar Raj</i>",
        "error": "❌ <b>Error:</b> Instagram blocked the request or the reel is private.",
        "button_follow": "💖 Follow Rahul Kumar Raj 💖",
        "cooldown": "⏳ <b>Spam Protection:</b> Please wait {time} seconds before sending another link!",
        "choose_quality": "🎬 <b>Link Found!</b>\n👇 Please choose video quality:"
    },
    "hi": {
        "welcome": "🚀 <b>Insta Ninja Downloader v2.0</b> 🚀\n\nनमस्ते! मैं किसी भी Instagram Reel को हाई क्वालिटी में डाउनलोड कर सकता हूँ। ⚡\n\n🎯 <b>बस मुझे रील का लिंक भेजें!</b>\n\n👇 <b>Developer को सपोर्ट करने के लिए फॉलो करें:</b>",
        "invalid": "⚠️ <b>दोस्त, कृपया सही Instagram लिंक भेजें!</b>",
        "processing": "⚙️ <b>सर्वर से वीडियो निकाला जा रहा है...</b>",
        "sending": "📤 <b>टेलीग्राम पर भेजा जा रहा है... 🚀</b>",
        "success": "🎬 <b>Download Successful!</b> ✅\n\n⚡ <i>Powered by Rahul Kumar Raj</i>",
        "error": "❌ <b>Error:</b> Instagram ने रिक्वेस्ट रोक दी है या रील प्राइवेट है।",
        "button_follow": "💖 Follow Rahul Kumar Raj 💖",
        "cooldown": "⏳ <b>स्पैम अलर्ट:</b> कृपया अगला लिंक भेजने से पहले {time} सेकंड प्रतीक्षा करें!",
        "choose_quality": "🎬 <b>लिंक मिल गया!</b>\n👇 कृपया वीडियो क्वालिटी चुनें:"
    }
}

# 📥 DOWNLOAD LOGIC
def download_reel_sync(url, file_path, quality_format="best"):
    ydl_opts = {
        'outtmpl': file_path,
        'format': quality_format, 
        'quiet': True,
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def extract_direct_link_sync(url):
    ydl_opts = {'format': 'best', 'quiet': True, 'noplaylist': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

async def update_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    status_msg = await update.message.reply_text("⚙️ <b>अपडेट ढूँढा जा रहा है...</b>", parse_mode='HTML')
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"], check=True)
        await status_msg.edit_text("✅ <b>अपडेट सक्सेसफुल!</b> 🚀", parse_mode='HTML')
        await asyncio.sleep(2)
        os._exit(0)
    except Exception:
        pass

async def get_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    stats_msg = (
        "📊 <b>Admin Live Dashboard</b> 📊\n\n"
        f"👥 <b>टोटल यूज़र्स:</b> {len(active_users)}\n"
        f"📥 <b>टोटल डाउनलोड्स:</b> {total_downloads}\n\n"
        "🟢 <b>सर्वर स्टेटस:</b> 100% Online 🚀"
    )
    await update.message.reply_text(stats_msg, parse_mode='HTML')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_users:
        active_users.add(user_id)
        try:
            alert_msg = f"🚨 <b>New User!</b>\n👤 {update.effective_user.first_name}\n🆔 <code>{user_id}</code>"
            await context.bot.send_message(chat_id=ADMIN_ID, text=alert_msg, parse_mode='HTML')
        except: pass

    keyboard = [[InlineKeyboardButton("🇮🇳 Hindi", callback_data="lang_hi"), InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]]
    await update.message.reply_text("🌍 <b>Please select your language:</b>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

# 💬 LINK AANE PAR 4 QUALITY BUTTONS DIKHANA
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.effective_user.id
    lang = user_languages.get(user_id, "hi")

    if user_id != OWNER_ID: 
        current_time = time.time()
        if user_id in user_cooldowns and (current_time - user_cooldowns[user_id]) < COOLDOWN_TIME:
            await update.message.reply_text(LANG[lang]["cooldown"].replace("{time}", str(int(COOLDOWN_TIME - (current_time - user_cooldowns[user_id])))), parse_mode='HTML')
            return 
        user_cooldowns[user_id] = current_time

    if "instagram.com" not in url:
        await update.message.reply_text(LANG[lang]["invalid"], parse_mode='HTML')
        return

    pending_links[user_id] = url

    # 👇 NAYA: 720p Button Add Kar Diya Gaya Hai
    keyboard = [
        [InlineKeyboardButton("💾 480p (Data Saver)", callback_data="qual_low")],
        [InlineKeyboardButton("📺 720p (Standard HD)", callback_data="qual_720")],
        [InlineKeyboardButton("🎥 1080p (Full HD)", callback_data="qual_hd")],
        [InlineKeyboardButton("💎 4K (Original File)", callback_data="qual_4k")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(LANG[lang]["choose_quality"], parse_mode='HTML', reply_markup=reply_markup)

# 🔘 BUTTON CLICK HANDLER
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data
    lang = user_languages.get(user_id, "hi")

    if data in ["lang_hi", "lang_en"]:
        lang = "hi" if data == "lang_hi" else "en"
        user_languages[user_id] = lang
        keyboard = [[InlineKeyboardButton(LANG[lang]["button_follow"], url=INSTA_LINK)]]
        await query.edit_message_text(LANG[lang]["welcome"], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("qual_"):
        url = pending_links.get(user_id)
        if not url:
            await query.edit_message_text("⚠️ Link expired! Please send the link again.")
            return

        await query.edit_message_text(LANG[lang]["processing"], parse_mode='HTML')
        
        # 👇 NAYA: 720p ka logic set kiya gaya
        if data == "qual_low":
            quality_fmt = "worst"
            as_document = False
        elif data == "qual_720":
            quality_fmt = "best[height<=720]/best" # Agar 720p na mile to error na de, jo best ho wo dede
            as_document = False
        elif data == "qual_hd":
            quality_fmt = "best"
            as_document = False
        elif data == "qual_4k":
            quality_fmt = "best"
            as_document = True

        chat_id = update.effective_chat.id
        file_path = f"reel_{chat_id}.mp4"
        download_success = False

        for attempt in range(3):
            try:
                await asyncio.to_thread(download_reel_sync, url, file_path, quality_fmt)
                if os.path.exists(file_path):
                    download_success = True
                    break
            except:
                await asyncio.sleep(2)

        if not download_success:
            await query.edit_message_text(LANG[lang]["error"], parse_mode='HTML')
            return

        try:
            await query.edit_message_text(LANG[lang]["sending"], parse_mode='HTML')
            keyboard = [[InlineKeyboardButton(LANG[lang]["button_follow"], url=INSTA_LINK)]]
            
            with open(file_path, 'rb') as video_file:
                if as_document:
                    await context.bot.send_document(chat_id=chat_id, document=video_file, caption=LANG[lang]["success"], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
                else:
                    await context.bot.send_video(chat_id=chat_id, video=video_file, caption=LANG[lang]["success"], parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
            
            await query.message.delete()
            global total_downloads
            total_downloads += 1
            del pending_links[user_id] 

        except Exception:
            await query.edit_message_text(LANG[lang]["error"], parse_mode='HTML')
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query or "instagram.com" not in query: return
    try:
        info = await asyncio.to_thread(extract_direct_link_sync, query)
        if not info or 'url' not in info: return
        video_url = info['url']
        thumb_url = info.get('thumbnail', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/132px-Instagram_logo_2016.svg.png')
        keyboard = [[InlineKeyboardButton("🔥 Created by Rahul Kumar Raj 🔥", url=INSTA_LINK)]]
        result = [InlineQueryResultVideo(id=str(uuid.uuid4()), video_url=video_url, mime_type="video/mp4", thumb_url=thumb_url, title="🎬 Send Instagram Reel", description="Click here to send video!", caption="⚡ <i>Powered by Insta Ninja</i>", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))]
        await update.inline_query.answer(result, cache_time=10)
        global total_downloads
        total_downloads += 1
    except: pass

def main():
    if not TELEGRAM_BOT_TOKEN: return
    threading.Thread(target=run_web, daemon=True).start()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("update", update_bot))
    application.add_handler(CommandHandler("stats", get_stats)) 
    application.add_handler(CallbackQueryHandler(button_click))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(InlineQueryHandler(inline_query))
    print("🚀 Bot is LIVE with 4 Quality Buttons!")
    application.run_polling()

if __name__ == '__main__':
    main()


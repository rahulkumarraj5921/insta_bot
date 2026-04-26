import os
import threading
import requests
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ⚠️ Render Settings se Token aayega
TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
INSTA_LINK = "https://instagram.com/rahul_kumar_raj_592"

# 🌐 WEB SERVER (Render ko active rakhne ke liye)
app = Flask(__name__)

@app.route('/')
def home():
    return "Ninja Bot is Running on Lifetime Free API! 🚀"

def run_web():
    # Render default port 8080 use karta hai
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# 🤖 BOT LOGIC
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🚀 **Insta Ninja Downloader (Lifetime Free)** 🚀\n\n"
        "नमस्ते! मैं बिना किसी लिमिट के Instagram Reels डाउनलोड कर सकता हूँ। ⚡\n\n"
        "🎯 *बस मुझे रील का लिंक भेजें!*\n\n"
        "👇 **Developer को सपोर्ट करने के लिए फॉलो करें:**"
    )
    keyboard = [[InlineKeyboardButton("💖 Follow Rahul Kumar Raj 💖", url=INSTA_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    url = update.message.text

    if "instagram.com" not in url:
        await update.message.reply_text("⚠️ दोस्त, कृपया सही Instagram लिंक भेजें!")
        return

    status_msg = await update.message.reply_text("🔍 **वीडियो प्रोसेस किया जा रहा है...**")
    await context.bot.send_chat_action(chat_id=chat_id, action='upload_video')

    try:
        # 🪄 COBALT API (No API Key Needed - Lifetime Free)
        api_url = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "vQuality": "720"
        }

        # API Request
        response = requests.post(api_url, json=payload, headers=headers)
        data = response.json()

        # Extract Video URL
        video_url = data.get("url")

        if not video_url:
            await status_msg.edit_text("❌ अभी सर्वर बिज़ी है या लिंक प्राइवेट है। कृपया कुछ देर बाद प्रयास करें।")
            return

        await status_msg.edit_text("📥 **सर्वर से वीडियो डाउनलोड हो रहा है...**")

        # Download file to Render server
        file_path = f"reel_{chat_id}.mp4"
        video_response = requests.get(video_url)
        with open(file_path, 'wb') as f:
            f.write(video_response.content)

        await status_msg.edit_text("📤 **टेलीग्राम पर भेजा जा रहा है... 🚀**")

        # Send to User
        keyboard = [[InlineKeyboardButton("🔥 Follow Rahul on Instagram 🔥", url=INSTA_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open(file_path, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                supports_streaming=True,
                caption="🎬 **Download Successful!** ✅\n\n⚡ *Powered by Ninja Free API*",
                reply_markup=reply_markup
            )
        
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ **Error:** अभी API रिस्पॉन्स नहीं दे रही है।")
        print(f"Error: {e}")

    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Error: BOT_TOKEN nahi mila!")
        return

    # Start Web Server in separate thread
    threading.Thread(target=run_web, daemon=True).start()
    
    # Start Bot
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Ninja Bot is Running 24/7 (Lifetime Free Mode)!")
    application.run_polling()

if __name__ == '__main__':
    main()

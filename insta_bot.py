import os
import threading
import yt_dlp
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
INSTA_LINK = "https://instagram.com/rahul_kumar_raj_592"

app = Flask(__name__)

@app.route('/')
def home():
    return "Ninja Bot: Direct Download Mode ON! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🚀 **Insta Ninja Downloader (Direct Mode)** 🚀\n\n"
        "बिना किसी API Key के, सीधे सर्वर से डाउनलोड! ⚡\n\n"
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

    status_msg = await update.message.reply_text("⚙️ **डायरेक्ट सर्वर से वीडियो निकाला जा रहा है...**")
    await context.bot.send_chat_action(chat_id=chat_id, action='upload_video')

    file_path = f"reel_{chat_id}.mp4"

    try:
        # 🪄 YT-DLP MAGIC (No API Needed)
        ydl_opts = {
            'outtmpl': file_path,
            'format': 'best',
            'quiet': True,
            'noplaylist': True,
            'no_warnings': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(file_path):
            raise Exception("वीडियो फाइल नहीं बन पाई।")

        await status_msg.edit_text("📤 **टेलीग्राम पर भेजा जा रहा है... 🚀**")

        keyboard = [[InlineKeyboardButton("🔥 Follow Rahul on Instagram 🔥", url=INSTA_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open(file_path, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                caption="🎬 **Download Successful!** ✅\n\n⚡ *Powered by Direct Ninja Engine*",
                reply_markup=reply_markup
            )
        
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text("❌ **Error:** Instagram ने रिक्वेस्ट रोक दी या रील प्राइवेट है।")
        print(f"Direct Error: {e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("⚠️ Error: BOT_TOKEN nahi mila!")
        return

    threading.Thread(target=run_web, daemon=True).start()
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Ninja Bot (Direct Mode) is Running!")
    application.run_polling()

if __name__ == '__main__':
    main()


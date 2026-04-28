import os
import threading
import yt_dlp
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
INSTA_LINK = "https://instagram.com/rahul_kumar_raj_592"

# VIP Channel ID (Yahan alerts aayenge)
ADMIN_ID = -1003901141197 
# Aapka Personal Telegram ID (Taki aapki khud ki link download karne par spy alert na aaye)
OWNER_ID = 5868140731

app = Flask(__name__)

@app.route('/')
def home():
    return "Ninja Bot is Running perfectly!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# 🧠 SMART MEMORY: Taki baar-baar alert na aaye
active_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    # Agar user naya hai tabhi channel me alert jayega
    if user_id not in active_users:
        active_users.add(user_id)
        try:
            alert_msg = f"🚨 <b>New User Alert!</b>\n👤 Naam: {user_name}\n🆔 ID: <code>{user_id}</code>\n🚀 Kisi naye bande ne bot chalu kiya hai!"
            await context.bot.send_message(chat_id=ADMIN_ID, text=alert_msg, parse_mode='HTML')
        except Exception as e:
            print("Channel alert error:", e)

    welcome_text = (
        "🚀 <b>Insta Ninja Downloader (Direct Mode)</b> 🚀\n\n"
        "Namaste! Main bina kisi API Key ke, seedhe server se reel download kar sakta hoon. ⚡\n\n"
        "🎯 <i>Bas mujhe reel ka link bhejein!</i>\n\n"
        "👇 <b>Developer ko support karne ke liye follow karein:</b>"
    )
    keyboard = [[InlineKeyboardButton("💖 Follow Rahul Kumar Raj 💖", url=INSTA_LINK)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    url = update.message.text
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    # Agar koi bina /start dabaye seedha link bhejta hai
    if user_id not in active_users:
        active_users.add(user_id)
        try:
            alert_msg = f"🚨 <b>New User Alert!</b>\n👤 Naam: {user_name}\n🆔 ID: <code>{user_id}</code>\n🚀 Naya user seedha reel download kar raha hai!"
            await context.bot.send_message(chat_id=ADMIN_ID, text=alert_msg, parse_mode='HTML')
        except Exception:
            pass

    # 👇👇 NAYA SPY MODE CODE YAHAN ADD KIYA HAI 👇👇
    # Agar link me instagram hai aur bhejne wala aap khud nahi hain, toh channel me spy alert jayega
    if user_id != OWNER_ID and "instagram.com" in url:
        try:
            spy_msg = f"🕵️‍♂️ <b>Spy Log!</b>\n👤 Naam: {user_name}\n🔗 <b>Link:</b> {url}"
            # disable_web_page_preview=True se link ka bada thumbnail channel me nahi dikhega
            await context.bot.send_message(chat_id=ADMIN_ID, text=spy_msg, parse_mode='HTML', disable_web_page_preview=True)
        except Exception:
            pass
    # 👆👆 NAYA SPY MODE CODE YAHAN KHATAM HUA 👆👆

    if "instagram.com" not in url:
        await update.message.reply_text("⚠️ दोस्त, कृपया सही Instagram लिंक भेजें!")
        return

    status_msg = await update.message.reply_text("⚙️ <b>डायरेक्ट सर्वर से वीडियो निकाला जा रहा है...</b>", parse_mode='HTML')
    await context.bot.send_chat_action(chat_id=chat_id, action='upload_video')

    file_path = f"reel_{chat_id}.mp4"

    try:
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
            raise Exception("Video file nahi ban payi.")

        await status_msg.edit_text("📤 <b>टेलीग्राम पर भेजा जा रहा है... 🚀</b>", parse_mode='HTML')

        keyboard = [[InlineKeyboardButton("🔥 Follow Rahul on Instagram 🔥", url=INSTA_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open(file_path, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                caption="🎬 <b>Download Successful!</b> ✅\n\n⚡ <i>Powered by Direct Ninja Engine</i>",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text("❌ <b>Error:</b> Instagram ने रिक्वेस्ट रोक दी या रील प्राइवेट है।", parse_mode='HTML')
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
    
    print("🚀 Ninja Bot is Running with Smart Alerts & Spy Mode!")
    application.run_polling()

if __name__ == '__main__':
    main()

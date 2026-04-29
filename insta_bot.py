import os
import threading
import yt_dlp
import asyncio  # ⏳ नया: बॉट को बिना हैंग किए 2 सेकंड रुकने के लिए
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
INSTA_LINK = "https://instagram.com/rahul_kumar_raj_592"

# VIP Channel ID (Yahan alerts aayenge)
ADMIN_ID = -1003901141197 
# Aapka Personal Telegram ID
OWNER_ID = 5868140731

app = Flask(__name__)

@app.route('/')
def home():
    return "Ninja Bot is Running perfectly! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# 🧠 SMART MEMORY: Baar-baar alert rokne ke liye
active_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name

    if user_id not in active_users:
        active_users.add(user_id)
        try:
            alert_msg = f"🚨 <b>New User Alert!</b>\n👤 Naam: {user_name}\n🆔 ID: <code>{user_id}</code>\n🚀 Naya banda bot par aaya hai!"
            await context.bot.send_message(chat_id=ADMIN_ID, text=alert_msg, parse_mode='HTML')
        except Exception as e:
            print(f"Alert error: {e}")

    welcome_text = (
        "🚀 <b>Insta Ninja Downloader v2.0</b> 🚀\n\n"
        "Namaste! Main kisi bhi Instagram Reel ko high quality mein download kar sakta hoon. ⚡\n\n"
        "🎯 <b>Bas mujhe reel ka link bhejein!</b>\n\n"
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

    # Spy Alert: Jab koi link bhejta hai
    if user_id != OWNER_ID and "instagram.com" in url:
        try:
            spy_msg = f"🕵️‍♂️ <b>Spy Log!</b>\n👤 Naam: {user_name}\n🔗 <b>Link:</b> {url}"
            await context.bot.send_message(chat_id=ADMIN_ID, text=spy_msg, parse_mode='HTML', disable_web_page_preview=True)
        except Exception:
            pass

    if "instagram.com" not in url:
        await update.message.reply_text("⚠️ <b>Dost, kripya sahi Instagram link bhejein!</b>", parse_mode='HTML')
        return

    status_msg = await update.message.reply_text("⚙️ <b>Server se video nikala ja raha hai...</b>", parse_mode='HTML')
    await context.bot.send_chat_action(chat_id=chat_id, action='upload_video')

    file_path = f"reel_{chat_id}.mp4"

    # 👇👇 NAYA AUTO-RETRY LOGIC YAHAN SE SHURU 👇👇
    max_retries = 3
    download_success = False

    for attempt in range(max_retries):
        try:
            ydl_opts = {
                'outtmpl': file_path,
                'format': 'best',
                'quiet': True,
                'noplaylist': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if os.path.exists(file_path):
                download_success = True
                break # Agar video mil gaya, to loop se bahar aa jao

        except Exception as e:
            print(f"Attempt {attempt + 1} Failed: {e}")
            await asyncio.sleep(2) # 2 second ruk kar dubara try karega bina bot hang kiye

    # Agar 3 baar koshish ke baad bhi fail ho jaye
    if not download_success:
        await status_msg.edit_text("❌ <b>Error:</b> Instagram ne request rok di hai. Kripya thodi der baad dubara try karein.", parse_mode='HTML')
        return
    # 👆👆 AUTO-RETRY LOGIC YAHAN KHATAM 👆👆

    # 👇👇 TELEGRAM PAR BHEJNE KA CODE 👇👇
    try:
        await status_msg.edit_text("📤 <b>Telegram par bheja ja raha hai... 🚀</b>", parse_mode='HTML')

        keyboard = [[InlineKeyboardButton("🔥 Follow Rahul on Instagram 🔥", url=INSTA_LINK)]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        with open(file_path, 'rb') as video_file:
            await context.bot.send_video(
                chat_id=chat_id,
                video=video_file,
                caption="🎬 <b>Download Successful!</b> ✅\n\n⚡ <i>Powered by Rahul Kumar Raj</i>",
                parse_mode='HTML',
                reply_markup=reply_markup
            )
        
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text("❌ <b>Error:</b> Video bhejne me problem aayi.", parse_mode='HTML')
        print(f"Telegram Upload Error: {e}")

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

def main():
    if not TELEGRAM_BOT_TOKEN:
        print("Error: BOT_TOKEN missing!")
        return

    threading.Thread(target=run_web, daemon=True).start()
    
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Bot is LIVE with HTML Tags, Spy Mode & Auto-Retry!")
    application.run_polling()

if __name__ == '__main__':
    main()

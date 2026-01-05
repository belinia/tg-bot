import os
import logging
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters

# Logları sadece terminalde görelim
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8530466633:AAERcBjFnvENn0tAZnhE6A6lbBMk2KYOj2w"

# --- MEDYA MOTORU ---
def download_media(url, mode="audio"):
    ffmpeg_path = "./ffmpeg/ffmpeg" if os.path.exists("./ffmpeg/ffmpeg") else "ffmpeg"
    
    if mode == "audio":
        opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'ffmpeg_location': ffmpeg_path,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        }
    else:
        opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if mode == "audio":
            filename = filename.rsplit('.', 1)[0] + ".mp3"
        return filename, info.get('title', 'Medya')

# --- ANA FONKSİYONLAR ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "💎 **Beliyna Downloader**\n\n"
        "Herhangi bir platformdan link gönderin, sizin için hazırlayayım.\n\n"
        "🔹 **Desteklenenler:** YouTube, Instagram, TikTok, Twitter ve daha fazlası."
    )
    await update.message.reply_text(welcome, parse_mode="Markdown")

async def link_isleyici(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"):
        return # Sadece linkleri yakala

    # Seçim Butonları
    keyboard = [
        [
            InlineKeyboardButton("🎵 Ses (MP3)", callback_data=f"mp3|{url}"),
            InlineKeyboardButton("🎬 Video (MP4)", callback_data=f"mp4|{url}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📥 **Medya algılandı.** Hangi formatta indirmek istersiniz?",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def buton_tiklama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data, url = query.data.split("|")
    mode = "audio" if data == "mp3" else "video"
    
    await query.edit_message_text("⚙️ **İşlem başlatıldı, lütfen bekleyin...**", parse_mode="Markdown")

    try:
        path, title = download_media(url, mode=mode)
        
        if mode == "audio":
            await query.message.reply_audio(audio=open(path, "rb"), title=title, caption=f"✅ {title}")
        else:
            await query.message.reply_video(video=open(path, "rb"), caption=f"✅ {title}")
        
        if os.path.exists(path):
            os.remove(path)
        await query.message.delete()

    except Exception as e:
        await query.message.reply_text("❌ Medya indirilirken bir hata oluştu. Linkin geçerli olduğundan emin olun.")

# --- BAŞLATICI ---
if __name__ == '__main__':
    if not os.path.exists("downloads"):
        os.makedirs("downloads")

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), link_isleyici))
    app.add_handler(CallbackQueryHandler(buton_tiklama))
    
    app.run_polling()

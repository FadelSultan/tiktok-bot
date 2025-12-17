import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# التوكن من متغيرات البيئة
BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = """
مرحباً! 👋

أنا بوت تحميل فيديوهات TikTok 🎬

📌 طريقة الاستخدام:
1. افتح TikTok
2. اختر الفيديو
3. اضغط "مشاركة" ثم "نسخ الرابط"
4. أرسل الرابط هنا

وبس! 🚀
    """
    await update.message.reply_text(welcome)

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    
    if "tiktok.com" not in url:
        await update.message.reply_text("❌ هذا ليس رابط TikTok!\nأرسل رابط صحيح")
        return
    
    msg = await update.message.reply_text("⏳ جاري التحميل... انتظر")
    
    try:
        os.makedirs('downloads', exist_ok=True)
        
        ydl_opts = {
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'format': 'best',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            video_title = info.get('title', 'TikTok Video')
        
        await msg.edit_text("📤 جاري الإرسال...")
        
        with open(video_path, 'rb') as video:
            await update.message.reply_video(
                video=video,
                caption=f"✅ {video_title}"
            )
        
        await msg.delete()
        os.remove(video_path)
        
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ!\n\nالسبب: {str(e)}")

def main():
    print("🤖 البوت يعمل...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_tiktok))
    
    print("✅ البوت جاهز!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

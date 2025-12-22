import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from database import init_db, add_user, add_download, get_stats, ban_user, unban_user, is_banned, get_all_users, get_top_users

# التوكن و Admin ID
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# المنصات المدعومة
SUPPORTED_PLATFORMS = {
    'tiktok.com': 'TikTok',
    'instagram.com': 'Instagram',
    'youtube.com': 'YouTube',
    'youtu.be': 'YouTube',
    'twitter.com': 'Twitter',
    'x.com': 'Twitter',
    'facebook.com': 'Facebook',
    'fb.watch': 'Facebook'
}

def detect_platform(url):
    for domain, name in SUPPORTED_PLATFORMS.items():
        if domain in url:
            return name
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
    if is_banned(user.id):
        await update.message.reply_text("⛔ أنت محظور من استخدام البوت")
        return
    
    keyboard = [
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="stats")],
        [InlineKeyboardButton("❓ المساعدة", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome = f"""
مرحباً {user.first_name}! 👋

أنا بوت تحميل الفيديوهات 🎬

📱 **المنصات المدعومة:**
• TikTok
• Instagram  
• YouTube
• Twitter/X
• Facebook

📌 **طريقة الاستخدام:**
أرسل رابط الفيديو مباشرة

🎵 **لتحميل صوت فقط:**
أرسل: `/mp3 الرابط`
    """
    await update.message.reply_text(welcome, reply_markup=reply_markup, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
📖 **دليل الاستخدام:**

🎬 **تحميل فيديو:**
فقط أرسل الرابط

🎵 **تحميل صوت MP3:**
`/mp3 الرابط`

📊 **الإحصائيات:**
`/stats`

━━━━━━━━━━━━━━━
👑 **أوامر الأدمن:**
`/admin` - لوحة التحكم
`/broadcast` - رسالة جماعية
`/ban` - حظر مستخدم
`/unban` - فك الحظر
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = get_stats()
    
    platform_text = ""
    for platform, count in stats['platform_stats']:
        platform_text += f"  • {platform}: {count}\n"
    
    stats_text = f"""
📊 **إحصائيات البوت:**

👥 **المستخدمين:**
  • الإجمالي: {stats['total_users']}
  • نشطين اليوم: {stats['active_today']}

📥 **التحميلات:**
  • الإجمالي: {stats['total_downloads']}
  • اليوم: {stats['downloads_today']}

📱 **حسب المنصة:**
{platform_text if platform_text else '  لا توجد تحميلات بعد'}
    """
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ هذا الأمر للأدمن فقط")
        return
    
    stats = get_stats()
    top_users = get_top_users(5)
    
    top_text = ""
    for i, (uid, name, count) in enumerate(top_users, 1):
        top_text += f"  {i}. {name}: {count} تحميل\n"
    
    admin_text = f"""
👑 **لوحة تحكم الأدمن:**

📊 **إحصائيات سريعة:**
  • المستخدمين: {stats['total_users']}
  • التحميلات: {stats['total_downloads']}

🏆 **أكثر المستخدمين نشاطاً:**
{top_text if top_text else '  لا يوجد'}

⚙️ **الأوامر:**
• `/broadcast رسالة` - إرسال للجميع
• `/ban user_id` - حظر
• `/unban user_id` - فك حظر
• `/users` - قائمة المستخدمين
    """
    await update.message.reply_text(admin_text, parse_mode='Markdown')

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ هذا الأمر للأدمن فقط")
        return
    
    if not context.args:
        await update.message.reply_text("❌ استخدم: `/broadcast رسالتك`", parse_mode='Markdown')
        return
    
    message = ' '.join(context.args)
    users = get_all_users()
    
    success = 0
    failed = 0
    
    status_msg = await update.message.reply_text(f"📤 جاري الإرسال لـ {len(users)} مستخدم...")
    
    for user_id in users:
        try:
            await context.bot.send_message(user_id, f"📢 **رسالة من الإدارة:**\n\n{message}", parse_mode='Markdown')
            success += 1
        except:
            failed += 1
    
    await status_msg.edit_text(f"✅ تم الإرسال!\n\n📊 نجح: {success}\n❌ فشل: {failed}")

async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ هذا الأمر للأدمن فقط")
        return
    
    if not context.args:
        await update.message.reply_text("❌ استخدم: `/ban user_id`", parse_mode='Markdown')
        return
    
    try:
        user_id = int(context.args[0])
        ban_user(user_id)
        await update.message.reply_text(f"✅ تم حظر المستخدم: `{user_id}`", parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ ID غير صحيح")

async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ هذا الأمر للأدمن فقط")
        return
    
    if not context.args:
        await update.message.reply_text("❌ استخدم: `/unban user_id`", parse_mode='Markdown')
        return
    
    try:
        user_id = int(context.args[0])
        unban_user(user_id)
        await update.message.reply_text(f"✅ تم فك حظر المستخدم: `{user_id}`", parse_mode='Markdown')
    except:
        await update.message.reply_text("❌ ID غير صحيح")

async def download_mp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
    if is_banned(user.id):
        await update.message.reply_text("⛔ أنت محظور من استخدام البوت")
        return
    
    if not context.args:
        await update.message.reply_text("❌ استخدم: `/mp3 الرابط`", parse_mode='Markdown')
        return
    
    url = context.args[0]
    platform = detect_platform(url)
    
    if not platform:
        await update.message.reply_text("❌ رابط غير مدعوم!")
        return
    
    msg = await update.message.reply_text(f"🎵 جاري تحميل الصوت من {platform}...")
    
    try:
        os.makedirs('downloads', exist_ok=True)
        
        ydl_opts = {
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_path = f"downloads/{info['id']}.mp3"
            title = info.get('title', 'Audio')
        
        await msg.edit_text("📤 جاري الإرسال...")
        
        with open(audio_path, 'rb') as audio:
            await update.message.reply_audio(
                audio=audio,
                title=title,
                caption=f"🎵 {title}\n\n📱 المصدر: {platform}"
            )
        
        add_download(user.id, platform, 'audio')
        await msg.delete()
        os.remove(audio_path)
        
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ!\n\n`{str(e)}`", parse_mode='Markdown')

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    
    if is_banned(user.id):
        await update.message.reply_text("⛔ أنت محظور من استخدام البوت")
        return
    
    url = update.message.text.strip()
    platform = detect_platform(url)
    
    if not platform:
        await update.message.reply_text(
            "❌ رابط غير مدعوم!\n\n"
            "📱 المنصات المدعومة:\n"
            "• TikTok\n• Instagram\n• YouTube\n• Twitter\n• Facebook"
        )
        return
    
    msg = await update.message.reply_text(f"⏳ جاري التحميل من {platform}...")
    
    try:
        os.makedirs('downloads', exist_ok=True)
        
        ydl_opts = {
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'format': 'best[filesize<50M]/best',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            title = info.get('title', 'Video')
        
        await msg.edit_text("📤 جاري الإرسال...")
        
        with open(video_path, 'rb') as video:
            await update.message.reply_video(
                video=video,
                caption=f"✅ {title}\n\n📱 المصدر: {platform}"
            )
        
        add_download(user.id, platform, 'video')
        await msg.delete()
        os.remove(video_path)
        
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ!\n\n`{str(e)}`", parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "stats":
        stats = get_stats()
        stats_text = f"📊 المستخدمين: {stats['total_users']}\n📥 التحميلات: {stats['total_downloads']}"
        await query.message.reply_text(stats_text)
    
    elif query.data == "help":
        await help_command(update, context)

def main():
    print("🤖 جاري تشغيل البوت...")
    
    # تهيئة قاعدة البيانات
    init_db()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # الأوامر الأساسية
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("mp3", download_mp3))
    
    # أوامر الأدمن
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("ban", ban_command))
    app.add_handler(CommandHandler("unban", unban_command))
    
    # معالجة الأزرار
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # معالجة الروابط
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    
    print("✅ البوت جاهز!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()

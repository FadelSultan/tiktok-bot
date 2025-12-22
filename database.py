import sqlite3
from datetime import datetime, timedelta

def init_db():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    
    # جدول المستخدمين
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            join_date TEXT,
            is_banned INTEGER DEFAULT 0,
            downloads_count INTEGER DEFAULT 0,
            last_active TEXT
        )
    ''')
    
    # جدول التحميلات
    c.execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            platform TEXT,
            download_type TEXT,
            download_date TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    
    c.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
    if not c.fetchone():
        c.execute('''
            INSERT INTO users (user_id, username, first_name, join_date, last_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, datetime.now().isoformat(), datetime.now().isoformat()))
    else:
        c.execute('UPDATE users SET last_active = ? WHERE user_id = ?', 
                  (datetime.now().isoformat(), user_id))
    
    conn.commit()
    conn.close()

def add_download(user_id, platform, download_type):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO downloads (user_id, platform, download_type, download_date)
        VALUES (?, ?, ?, ?)
    ''', (user_id, platform, download_type, datetime.now().isoformat()))
    
    c.execute('UPDATE users SET downloads_count = downloads_count + 1 WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    
    # إجمالي المستخدمين
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    
    # المستخدمين النشطين اليوم
    today = datetime.now().date().isoformat()
    c.execute('SELECT COUNT(*) FROM users WHERE last_active LIKE ?', (f'{today}%',))
    active_today = c.fetchone()[0]
    
    # إجمالي التحميلات
    c.execute('SELECT COUNT(*) FROM downloads')
    total_downloads = c.fetchone()[0]
    
    # تحميلات اليوم
    c.execute('SELECT COUNT(*) FROM downloads WHERE download_date LIKE ?', (f'{today}%',))
    downloads_today = c.fetchone()[0]
    
    # تحميلات حسب المنصة
    c.execute('SELECT platform, COUNT(*) FROM downloads GROUP BY platform')
    platform_stats = c.fetchall()
    
    conn.close()
    
    return {
        'total_users': total_users,
        'active_today': active_today,
        'total_downloads': total_downloads,
        'downloads_today': downloads_today,
        'platform_stats': platform_stats
    }

def ban_user(user_id):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def unban_user(user_id):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def is_banned(user_id):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('SELECT is_banned FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result and result[0] == 1

def get_all_users():
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('SELECT user_id FROM users WHERE is_banned = 0')
    users = [row[0] for row in c.fetchall()]
    conn.close()
    return users

def get_top_users(limit=10):
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('''
        SELECT user_id, first_name, downloads_count 
        FROM users 
        ORDER BY downloads_count DESC 
        LIMIT ?
    ''', (limit,))
    top = c.fetchall()
    conn.close()
    return top

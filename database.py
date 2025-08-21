# database.py
import sqlite3
import os
import time
from config import DB_FILE

def init_db():
    """ডাটাবেস এবং প্রয়োজনীয় টেবিল তৈরি করে।"""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # গ্রুপ-ভিত্তিক সেটিংস (কাস্টম ওয়েলকাম, রুলস ইত্যাদি)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS group_settings (
            chat_id INTEGER PRIMARY KEY,
            welcome_message TEXT DEFAULT 'Welcome {user} to the group!',
            rules TEXT DEFAULT '1. No spamming.\n2. Be respectful.'
        )
    ''')

    # ইউজারদের ওয়ার্নিং ট্র্যাক করার জন্য
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warnings (
            user_id INTEGER,
            chat_id INTEGER,
            count INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, chat_id)
        )
    ''')
    
    # ইউজারদের পরিসংখ্যান ট্র্যাক করার জন্য
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            user_id INTEGER,
            chat_id INTEGER,
            message_count INTEGER DEFAULT 0,
            join_date INTEGER,
            PRIMARY KEY (user_id, chat_id)
        )
    ''')

    conn.commit()
    conn.close()

# --- Warning Functions ---
def add_warning(user_id, chat_id):
    """একজন ইউজারের ওয়ার্নিং সংখ্যা বাড়ায়।"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO warnings (user_id, chat_id, count) VALUES (?, ?, 0)",
        (user_id, chat_id)
    )
    cursor.execute(
        "UPDATE warnings SET count = count + 1 WHERE user_id = ? AND chat_id = ?",
        (user_id, chat_id)
    )
    cursor.execute("SELECT count FROM warnings WHERE user_id = ? AND chat_id = ?", (user_id, chat_id))
    new_count = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return new_count

# --- Settings Functions ---
def get_group_setting(chat_id, setting_name):
    """গ্রুপের নির্দিষ্ট সেটিং নিয়ে আসে।"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO group_settings (chat_id) VALUES (?)", (chat_id,))
    cursor.execute(f"SELECT {setting_name} FROM group_settings WHERE chat_id = ?", (chat_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def set_group_setting(chat_id, setting_name, value):
    """গ্রুপের জন্য একটি সেটিং সেট করে।"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO group_settings (chat_id) VALUES (?)", (chat_id,))
    cursor.execute(f"UPDATE group_settings SET {setting_name} = ? WHERE chat_id = ?", (value, chat_id))
    conn.commit()
    conn.close()

# --- Stats Functions ---
def log_user_join(user_id, chat_id):
    """ইউজার জয়েন করলে ডাটাবেসে লগ করে।"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    join_timestamp = int(time.time())
    cursor.execute(
        "INSERT OR IGNORE INTO user_stats (user_id, chat_id, join_date, message_count) VALUES (?, ?, ?, 0)",
        (user_id, chat_id, join_timestamp)
    )
    conn.commit()
    conn.close()

def log_message(user_id, chat_id):
    """প্রতিটি মেসেজের জন্য কাউন্ট বাড়ায়।"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # যদি ইউজার আগে থেকে না থাকে, তাহলে যোগ করি (বট যোগ হওয়ার আগে যারা ছিল)
    cursor.execute("INSERT OR IGNORE INTO user_stats (user_id, chat_id, message_count) VALUES (?, ?, 0)", (user_id, chat_id))
    cursor.execute(
        "UPDATE user_stats SET message_count = message_count + 1 WHERE user_id = ? AND chat_id = ?",
        (user_id, chat_id)
    )
    conn.commit()
    conn.close()

def get_user_info(user_id, chat_id):
    """ইউজারের তথ্য (join date, message count) রিটার্ন করে।"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT join_date, message_count FROM user_stats WHERE user_id = ? AND chat_id = ?", (user_id, chat_id))
    result = cursor.fetchone()
    conn.close()
    return result

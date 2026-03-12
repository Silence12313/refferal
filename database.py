import sqlite3
from datetime import datetime
import io

from config import BOT_USERNAME

conn = sqlite3.connect(
    "bot.db",
    check_same_thread=False,
    timeout=30
)

cursor = conn.cursor()

cursor.execute("PRAGMA journal_mode=WAL")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,
username TEXT,
first_name TEXT,
joined_at TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS referrals(
id INTEGER PRIMARY KEY AUTOINCREMENT,
referrer_id INTEGER,
invited_id INTEGER UNIQUE,
confirmed INTEGER DEFAULT 0,
created_at TEXT
)
""")

conn.commit()


def add_user(user_id, username, first_name):

    cursor.execute(
        "SELECT id FROM users WHERE id=?",
        (user_id,)
    )

    if cursor.fetchone():
        return False

    cursor.execute(
        "INSERT INTO users VALUES(?,?,?,?)",
        (
            user_id,
            username,
            first_name,
            datetime.now().isoformat()
        )
    )

    conn.commit()

    return True


def add_referral(referrer_id, invited_id):

    cursor.execute(
        "INSERT OR IGNORE INTO referrals(referrer_id, invited_id, created_at) VALUES(?,?,?)",
        (
            referrer_id,
            invited_id,
            datetime.now().isoformat()
        )
    )

    conn.commit()


def confirm_referral(invited_id):

    cursor.execute(
        "UPDATE referrals SET confirmed=1 WHERE invited_id=?",
        (invited_id,)
    )

    conn.commit()


def referral_owner(invited_id):

    cursor.execute(
        "SELECT referrer_id FROM referrals WHERE invited_id=?",
        (invited_id,)
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    return None


def count_referrals(referrer_id):

    cursor.execute(
        "SELECT COUNT(*) FROM referrals WHERE referrer_id=? AND confirmed=1",
        (referrer_id,)
    )

    return cursor.fetchone()[0]


def referral_link(user_id):

    return f"https://t.me/{BOT_USERNAME}?start={user_id}"


def get_all_users():

    cursor.execute("SELECT * FROM users")

    return cursor.fetchall()


def export_users():

    users = get_all_users()

    text = ""

    for u in users:
        text += f"{u[0]} | {u[1]} | {u[2]} | {u[3]}\n"

    file = io.BytesIO(text.encode())
    file.name = "users.txt"

    return file

import sqlite3
from datetime import datetime

conn = sqlite3.connect("bot.db", check_same_thread=False)
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


def count_referrals(referrer_id):

    cursor.execute(
        "SELECT COUNT(*) FROM referrals WHERE referrer_id=? AND confirmed=1",
        (referrer_id,)
    )

    return cursor.fetchone()[0]


def get_all_users():

    cursor.execute("SELECT * FROM users")

    return cursor.fetchall()


def get_referral_report():

    cursor.execute("""
    SELECT
    r.referrer_id,
    u1.username,
    r.invited_id,
    u2.username,
    r.confirmed
    FROM referrals r
    LEFT JOIN users u1 ON u1.id = r.referrer_id
    LEFT JOIN users u2 ON u2.id = r.invited_id
    """)

    return cursor.fetchall()

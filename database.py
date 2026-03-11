import sqlite3

conn = sqlite3.connect("bot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("PRAGMA journal_mode=WAL")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,
username TEXT,
first_name TEXT,
referrer INTEGER,
referrals INTEGER DEFAULT 0,
rewarded INTEGER DEFAULT 0
)
""")

conn.commit()


def add_user(user_id, username, first_name, referrer=None):

    cursor.execute("SELECT id FROM users WHERE id=?", (user_id,))
    if cursor.fetchone():
        return False

    cursor.execute(
        "INSERT INTO users VALUES(?,?,?,?,0,0)",
        (user_id, username, first_name, referrer)
    )

    conn.commit()

    return True


def add_referral(user_id):

    cursor.execute(
        "UPDATE users SET referrals = referrals + 1 WHERE id=?",
        (user_id,)
    )

    conn.commit()


def get_referrals(user_id):

    cursor.execute(
        "SELECT referrals FROM users WHERE id=?",
        (user_id,)
    )

    r = cursor.fetchone()

    return r[0] if r else 0


def is_rewarded(user_id):

    cursor.execute(
        "SELECT rewarded FROM users WHERE id=?",
        (user_id,)
    )

    r = cursor.fetchone()

    return r[0] if r else 0


def mark_rewarded(user_id):

    cursor.execute(
        "UPDATE users SET rewarded=1 WHERE id=?",
        (user_id,)
    )

    conn.commit()


def get_all():

    cursor.execute("SELECT * FROM users")

    return cursor.fetchall()
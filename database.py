import sqlite3

conn = sqlite3.connect("bot.db")
cursor = conn.cursor()

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
        "INSERT INTO users(id, username, first_name, referrer) VALUES(?,?,?,?)",
        (user_id, username, first_name, referrer)
    )

    if referrer:
        cursor.execute(
            "UPDATE users SET referrals = referrals + 1 WHERE id=?",
            (referrer,)
        )

    conn.commit()
    return True


def get_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
    return cursor.fetchone()


def get_referrals(user_id):
    cursor.execute("SELECT referrals FROM users WHERE id=?", (user_id,))
    res = cursor.fetchone()
    return res[0] if res else 0


def mark_rewarded(user_id):
    cursor.execute("UPDATE users SET rewarded=1 WHERE id=?", (user_id,))
    conn.commit()


def all_users():
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

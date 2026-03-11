import sqlite3

conn = sqlite3.connect("users.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id TEXT,
platform TEXT,
username TEXT,
first_name TEXT,
referrer TEXT,
referrals INTEGER DEFAULT 0,
rewarded INTEGER DEFAULT 0
)
""")

conn.commit()


def add_user(user_id, platform, username, first, ref):

    cursor.execute(
        "SELECT * FROM users WHERE user_id=? AND platform=?",
        (user_id, platform)
    )

    if cursor.fetchone():
        return False

    cursor.execute(
        "INSERT INTO users(user_id,platform,username,first_name,referrer) VALUES(?,?,?,?,?)",
        (user_id, platform, username, first, ref)
    )

    conn.commit()
    return True
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from config import *
from keyboards import menu
from database import *
import pandas as pd

bot = Bot(token=TELEGRAM_TOKEN, parse_mode="Markdown")
dp = Dispatcher(bot)

app = FastAPI()


async def check_subscription(user_id):

    try:
        member = await bot.get_chat_member(CHANNEL, user_id)
        return member.status != "left"
    except:
        return False


@dp.message_handler(commands=["start"])
async def start(message: types.Message):

    args = message.get_args()

    ref = None
    if args:
        ref = args

    new = add_user(
        message.from_user.id,
        "telegram",
        message.from_user.username,
        message.from_user.first_name,
        ref
    )

    if new and ref:

        if await check_subscription(message.from_user.id):

            cursor.execute(
                "UPDATE users SET referrals = referrals + 1 WHERE user_id=?",
                (ref,)
            )

            conn.commit()

            cursor.execute(
                "SELECT referrals FROM users WHERE user_id=?",
                (ref,)
            )

            count = cursor.fetchone()[0]

            await bot.send_message(
                ref,
                f"🎉 Новый реферал!\n\n{count}/3"
            )

            if count >= 3:

                cursor.execute(
                    "SELECT rewarded FROM users WHERE user_id=?",
                    (ref,)
                )

                if cursor.fetchone()[0] == 0:

                    await bot.send_message(
                        ref,
                        """
Поздравляем!

Вы победили в нашем конкурсе!

База эфиров:
https://www.youtube.com/playlist?list=PL2DjtAFoLP6w3ztMXg4eLzBPUj3iaFvPm

Консультация:
https://onstudy.org/konsultatsiya-art/
"""
                    )

                    cursor.execute(
                        "UPDATE users SET rewarded=1 WHERE user_id=?",
                        (ref,)
                    )

                    conn.commit()

    text = f"""
Рады видеть вас, {message.from_user.first_name}!

Если вам нравится наш канал [Your art muse](https://t.me/your_art_muse), рекомендуйте его друзьям!

Пригласите 3-х друзей и получите бонус 🔥
"""

    await message.answer(text, reply_markup=menu())


@dp.callback_query_handler(lambda c: c.data == "ref")
async def ref(call: types.CallbackQuery):

    username = (await bot.me).username

    link = f"https://t.me/{username}?start={call.from_user.id}"

    await call.message.answer(
        f"Ваша реферальная ссылка:\n\n{link}"
    )


@dp.callback_query_handler(lambda c: c.data == "how")
async def how(call: types.CallbackQuery):

    await call.message.answer("""
Что нужно сделать:

1️⃣ Подписаться на канал  
2️⃣ Получить ссылку  
3️⃣ Пригласить 3 друзей  
4️⃣ Получить эфиры
""")


@dp.message_handler(commands=["export"])
async def export(message: types.Message):

    if message.from_user.id != ADMIN_ID:
        return

    df = pd.read_sql_query(
        "SELECT * FROM users",
        conn
    )

    df.to_excel("users.xlsx")

    await message.answer_document(
        open("users.xlsx","rb")
    )


@app.post("/telegram")
async def telegram_webhook(req: Request):

    data = await req.json()

    update = Update(**data)

    await dp.process_update(update)

    return {"ok": True}
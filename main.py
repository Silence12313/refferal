import asyncio
import pandas as pd

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode

from config import *
from database import *

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher()

WELCOME_TEXT = """
Рады видеть вас, {name}!

Если вам нравится наш канал [Your art muse](https://t.me/your_art_muse), не стесняйтесь рекомендовать его друзьям!

*Пригласите 3-х своих друзей и получите в подарок наш супер-бонус!*

База из 5 эфиров с разборами искусства 🔥
Это более 9 часов анализа реальных работ художников.
"""


def main_keyboard():

    kb = InlineKeyboardBuilder()

    kb.button(
        text="Получить ссылку",
        callback_data="get_link"
    )

    kb.button(
        text="Как получить ПРИЗ?",
        callback_data="how"
    )

    kb.button(
        text="Подписаться на канал",
        url="https://t.me/your_art_muse"
    )

    kb.adjust(1)

    return kb.as_markup()


def referral_link(user_id):
    return f"https://t.me/{BOT_USERNAME}?start={user_id}"


async def check_subscription(user_id):

    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)

        return member.status in ["member", "administrator", "creator"]

    except:
        return False


@dp.message(CommandStart())
async def start(message: Message):

    args = message.text.split()

    referrer = None

    if len(args) > 1:
        referrer = int(args[1])

    is_new = add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        referrer
    )

    if is_new and referrer:

        count = get_referrals(referrer)

        await bot.send_message(
            referrer,
            f"🎉 У вас новый реферал!\nВсего: {count}/3"
        )

        if count >= REFERRALS_REQUIRED:

            user = get_user(referrer)

            if not user[5]:

                mark_rewarded(referrer)

                await bot.send_message(
                    referrer,
                    """
Поздравляем!

Вы победили в нашем конкурсе и получаете наш супер-бонус!

База из 5 эфиров разборов:
https://www.youtube.com/playlist?list=PL2DjtAFoLP6w3ztMXg4eLzBPUj3iaFvPm

Бесплатная консультация:
https://onstudy.org/konsultatsiya-art/
"""
                )

    text = WELCOME_TEXT.format(name=message.from_user.first_name)

    await message.answer(text, reply_markup=main_keyboard())


@dp.callback_query(F.data == "get_link")
async def link_handler(callback: CallbackQuery):

    link = referral_link(callback.from_user.id)

    await callback.message.answer(
        f"Ваша реферальная ссылка:\n{link}"
    )


@dp.callback_query(F.data == "how")
async def how_handler(callback: CallbackQuery):

    text = """
Что вам нужно сделать, чтобы получить эфиры:

- подпишитесь на канал https://t.me/your_art_muse
- нажмите кнопку «получить ссылку»
- отправьте ссылку друзьям
- пригласите 3-х друзей
- получите доступ к базе эфиров
"""

    await callback.message.answer(text)


@dp.message(Command("export"))
async def export_excel(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        return

    users = all_users()

    df = pd.DataFrame(
        users,
        columns=[
            "user_id",
            "username",
            "first_name",
            "referrer",
            "referrals",
            "rewarded"
        ]
    )

    file = "users.xlsx"

    df.to_excel(file, index=False)

    await message.answer_document(open(file, "rb"))


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

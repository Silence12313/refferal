import pandas as pd

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import *
from database import *
from keyboards import main_keyboard


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.MARKDOWN
    )
)

dp = Dispatcher()


def referral_link(user_id):
    return f"https://t.me/{BOT_USERNAME}?start={user_id}"


async def check_subscription(user_id):

    try:

        member = await bot.get_chat_member(
            CHANNEL_ID,
            user_id
        )

        return member.status in [
            "member",
            "administrator",
            "creator"
        ]

    except:

        return False


@dp.message(CommandStart())
async def start(message: Message):

    args = message.text.split()

    ref = None

    if len(args) > 1:

        try:

            ref = int(args[1])

            if ref == message.from_user.id:
                ref = None

        except:

            ref = None

    new_user = add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name,
        ref
    )

    if new_user and ref:

        if await check_subscription(message.from_user.id):

            add_referral(ref)

            count = get_referrals(ref)

            await bot.send_message(
                ref,
                f"🎉 У вас новый реферал\nВсего: {count}/3"
            )

            if count >= REF_REQUIRED:

                if not is_rewarded(ref):

                    mark_rewarded(ref)

                    await bot.send_message(
                        ref,
                        """
Поздравляем!

https://www.youtube.com/playlist?list=PL2DjtAFoLP6w3ztMXg4eLzBPUj3iaFvPm
"""
                    )

    text = f"""
Рады видеть вас, {message.from_user.first_name}!

Если вам нравится наш канал [Your art muse](https://t.me/your_art_muse), рекомендуйте его друзьям!

Пригласите 3-х друзей и получите бонус.
"""

    await message.answer(text, reply_markup=main_keyboard())


@dp.callback_query(F.data == "get_link")
async def get_link(callback: CallbackQuery):

    link = referral_link(callback.from_user.id)

    await callback.message.answer(
        "Ваша реферальная ссылка:\n" + link,
        parse_mode=None
    )


@dp.callback_query(F.data == "how")
async def how(callback: CallbackQuery):

    await callback.message.answer(
        """
Что нужно сделать:

1. Подписаться на канал
2. Получить ссылку
3. Пригласить 3 друзей
"""
    )


@dp.message(Command("export"))
async def export_excel(message: Message):

    if message.from_user.id not in ADMIN_IDS:
        await message.answer("Нет доступа")
        return

    data = get_referral_report()

    df = pd.DataFrame(
        data,
        columns=[
            "referrer_id",
            "referrer_username",
            "invited_id",
            "invited_username",
            "confirmed"
        ]
    )

    file = "referrals.xlsx"

    df.to_excel(file, index=False)

    await message.answer_document(open(file, "rb"))

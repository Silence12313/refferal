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
            chat_id=CHANNEL_ID,
            user_id=user_id
        )

        if member.status in ["member", "administrator", "creator"]:
            return True

        return False

    except Exception as e:

        print("SUBSCRIPTION CHECK ERROR:", e)

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


    add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.first_name
    )


    if ref:

        add_referral(ref, message.from_user.id)


    text = f"""
Рады видеть вас, {message.from_user.first_name}!

Если вам нравится наш канал [Your art muse](https://t.me/your_art_muse), не стесняйтесь рекомендовать его друзьям!

Пригласите 3 друзей и получите бонус!
"""

    await message.answer(text, reply_markup=main_keyboard())


@dp.callback_query(F.data == "get_link")
async def get_link(callback: CallbackQuery):

    await callback.answer()

    user_id = callback.from_user.id

    if not await check_subscription(user_id):

        await callback.message.answer(
            "Сначала подпишитесь на канал."
        )

        return

    confirm_referral(user_id)

    ref_owner = referral_owner(user_id)

    if ref_owner:

        count = count_referrals(ref_owner)

        await bot.send_message(
            ref_owner,
            f"🎉 У вас новый реферал!\nВсего: {count}/{REF_REQUIRED}"
        )

    link = referral_link(user_id)

    await callback.message.answer(
        "Ваша реферальная ссылка:\n" + link,
        parse_mode=None
    )


        if count >= REF_REQUIRED:

            await bot.send_message(
                ref_owner,
                """
Поздравляем!

Вы победили в нашем конкурсе!

База эфиров:
https://www.youtube.com/playlist?list=PL2DjtAFoLP6w3ztMXg4eLzBPUj3iaFvPm
"""
            )


    link = referral_link(user_id)

    await callback.message.answer(
        "Ваша реферальная ссылка:\n" + link,
        parse_mode=None
    )


@dp.callback_query(F.data == "how")
async def how(callback: CallbackQuery):

    await callback.message.answer(
        """
Что вам нужно сделать, чтобы получить эфиры:

1. Подпишитесь на канал
2. Нажмите «Получить ссылку»
3. Отправьте ссылку друзьям
4. Пригласите 3 человек
"""
    )


@dp.message(Command("export"))
async def export_excel(message: Message):

    if message.from_user.id not in ADMIN_IDS:

        await message.answer("Нет доступа")

        return


    data = referral_report()

    if not data:

        await message.answer("База пустая")

        return


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

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, CHANNEL_ID, CHANNEL_LINK, BOT_USERNAME, REF_REQUIRED
from keyboards import main_keyboard
from database import add_user, confirm_referral, referral_owner, count_referrals, referral_link, export_users


bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
)

dp = Dispatcher()


async def check_subscription(user_id):

    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)

        if member.status in ["member", "administrator", "creator"]:
            return True

        return False

    except:
        return False


@dp.message(Command("start"))
async def start(message: Message):

    args = message.text.split()

    ref = None

    if len(args) > 1:
        ref = args[1]

    add_user(
        message.from_user.id,
        message.from_user.first_name,
        message.from_user.username,
        ref
    )

    text = f"""
Рады видеть вас, {message.from_user.first_name}!

Если вам нравится наш канал [Your art muse]({CHANNEL_LINK}), не стесняйтесь рекомендовать его друзьям!

*Пригласите 3-х своих друзей и получите в подарок наш супер-бонус!*

База из 5 эфиров с разборами искусства 🔥
"""

    await message.answer(text, reply_markup=main_keyboard())


@dp.callback_query(F.data == "get_link")
async def get_link(callback: CallbackQuery):

    await callback.answer()

    user_id = callback.from_user.id

    if not await check_subscription(user_id):

        await callback.message.answer("Сначала подпишитесь на канал.")
        return

    confirm_referral(user_id)

    owner = referral_owner(user_id)

    if owner:

        count = count_referrals(owner)

        await bot.send_message(
            owner,
            f"🎉 Новый реферал!\nВсего: {count}/{REF_REQUIRED}"
        )

        if count >= REF_REQUIRED:

            await bot.send_message(
                owner,
                """
Поздравляем!

Вы победили в нашем конкурсе и получаете наш супер-бонус!

База из 5 эфиров:
https://www.youtube.com/playlist?list=PL2DjtAFoLP6w3ztMXg4eLzBPUj3iaFvPm

Бесплатная консультация:
https://onstudy.org/konsultatsiya-art/
"""
            )

    link = referral_link(user_id)

    await callback.message.answer(
        f"Ваша реферальная ссылка:\n{link}"
    )


@dp.callback_query(F.data == "how")
async def how(callback: CallbackQuery):

    await callback.answer()

    text = f"""
Что вам нужно сделать, чтобы получить эфиры:

- подпишитесь на канал [Your art muse]({CHANNEL_LINK})
- нажмите кнопку «получить ссылку»
- отправьте ссылку друзьям
- пригласите {REF_REQUIRED} друзей
- получите доступ к эфиру
"""

    await callback.message.answer(text)


@dp.message(Command("export"))
async def export(message: Message):

    file = export_users()

    await message.answer_document(file)

from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import CHANNEL_LINK


def main_keyboard():

    kb = InlineKeyboardBuilder()

    kb.button(text="Получить ссылку", callback_data="get_link")
    kb.button(text="Как получить ПРИЗ?", callback_data="how")
    kb.button(text="Подписаться на канал", url=CHANNEL_LINK)

    kb.adjust(1)

    return kb.as_markup()

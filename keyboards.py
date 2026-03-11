from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def menu():

    kb = InlineKeyboardMarkup()

    kb.add(
        InlineKeyboardButton(
            "🔗 Получить ссылку",
            callback_data="ref"
        )
    )

    kb.add(
        InlineKeyboardButton(
            "❓ Как получить ПРИЗ?",
            callback_data="how"
        )
    )

    kb.add(
        InlineKeyboardButton(
            "📢 Подписаться",
            url="https://t.me/your_art_muse"
        )
    )

    return kb
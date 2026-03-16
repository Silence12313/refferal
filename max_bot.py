from fastapi import APIRouter, Request

from config import CHANNEL_LINK, REF_REQUIRED
from database import (
    add_user,
    add_referral,
    confirm_referral,
    referral_owner,
    count_referrals,
    referral_link
)

router = APIRouter()


@router.post("/max/webhook")
async def max_webhook(request: Request):

    data = await request.json()

    user = data.get("user", {})
    message = data.get("message", {})

    user_id = user.get("id")
    username = user.get("username")
    first_name = user.get("first_name")

    text = message.get("text", "")

    if not user_id:
        return {"status": "no user"}

    add_user(user_id, username, first_name)

    if text.startswith("/start"):

        parts = text.split()

        ref = None

        if len(parts) > 1:
            ref = parts[1]

        if ref:
            try:
                add_referral(int(ref), user_id)
            except:
                pass

        return {
            "text": f"""
Рады видеть вас, {first_name}!

Подпишитесь на канал:
{CHANNEL_LINK}

Пригласите {REF_REQUIRED} друзей и получите бонус.

Напишите:
получить ссылку
"""
        }

    if text.lower() == "получить ссылку":

        confirm_referral(user_id)

        owner = referral_owner(user_id)

        if owner:

            count = count_referrals(owner)

            if count >= REF_REQUIRED:

                return {
                    "text": """
Поздравляем!

Вы пригласили нужное количество друзей!

База эфиров:
https://www.youtube.com/playlist?list=PL2DjtAFoLP6w3ztMXg4eLzBPUj3iaFvPm

Консультация:
https://onstudy.org/konsultatsiya-art/
"""
                }

        link = referral_link(user_id)

        return {
            "text": f"Ваша реферальная ссылка:\n{link}"
        }

    if text.lower() == "как получить приз":

        return {
            "text": f"""
Что нужно сделать:

1 Подписаться на канал
{CHANNEL_LINK}

2 Написать: получить ссылку

3 Отправить друзьям

4 Пригласить {REF_REQUIRED}

5 Получить бонус
"""
        }

    return {"status": "ok"}

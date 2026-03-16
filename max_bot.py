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

from max_api import send_message_max

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

        await send_message_max(
            user_id,
            f"""
Рады видеть вас, {first_name}!

Подпишитесь на канал:
{CHANNEL_LINK}

Пригласите {REF_REQUIRED} друзей и получите бонус.
"""
        )

    elif text.lower() == "получить ссылку":

        confirm_referral(user_id)

        link = referral_link(user_id)

        await send_message_max(
            user_id,
            f"Ваша реферальная ссылка:\n{link}"
        )

    elif text.lower() == "как получить приз":

        await send_message_max(
            user_id,
            f"""
Что нужно сделать:

1 Подписаться на канал
{CHANNEL_LINK}

2 Написать: получить ссылку

3 Отправить ссылку друзьям

4 Пригласить {REF_REQUIRED} друзей
"""
        )

    return {"ok": True}

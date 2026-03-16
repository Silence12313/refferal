import aiohttp
from config import MAX_BOT_TOKEN

MAX_API = "https://api.max.ru/bot"


async def send_message_max(user_id, text):

    url = f"{MAX_API}/sendMessage"

    payload = {
        "token": MAX_BOT_TOKEN,
        "user_id": user_id,
        "text": text
    }

    async with aiohttp.ClientSession() as session:

        await session.post(url, json=payload)

import asyncio
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn

from telegram_bot import dp, bot
from max_bot import router as max_router
from config import BOT_USERNAME

app = FastAPI()

app.include_router(max_router)


@app.get("/")
async def root():
    return {"status": "bot running"}


@app.get("/ref/{user_id}")
async def referral_redirect(user_id: int):

    link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    return RedirectResponse(link)


@app.on_event("startup")
async def startup():

    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except:
        pass

    asyncio.create_task(dp.start_polling(bot))


if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080
    )

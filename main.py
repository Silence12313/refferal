import asyncio
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
import uvicorn

from telegram_bot import dp, bot
from config import BOT_USERNAME
from max_bot import router as max_router

app = FastAPI()

app.include_router(max_router)


@app.get("/")
async def root():
    return {"status": "bot running"}


@app.get("/ref/{user_id}")
async def referral_redirect(user_id: int):

    telegram_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

    return RedirectResponse(telegram_link)


@app.on_event("startup")
async def startup():

    await bot.delete_webhook(drop_pending_updates=True)

    asyncio.create_task(dp.start_polling(bot))


if __name__ == "__main__":

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080
    )

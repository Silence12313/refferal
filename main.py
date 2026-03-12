import asyncio
from fastapi import FastAPI
import uvicorn

from telegram_bot import dp, bot

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "running"}


async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


@app.on_event("startup")
async def startup():
    asyncio.create_task(start_bot())


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080)

import asyncio

from fastapi import FastAPI
import uvicorn

from telegram_bot import dp, bot
from max_bot import router

app = FastAPI()

app.include_router(router)


@app.on_event("startup")
async def startup():

    asyncio.create_task(
        dp.start_polling(bot)
    )


if __name__ == "__main__":

    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

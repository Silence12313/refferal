from fastapi import APIRouter, Request

from database import add_user

router = APIRouter()


@router.post("/max/webhook")
async def max_webhook(request: Request):

    data = await request.json()

    user = data.get("user", {})
    message = data.get("message", {})

    user_id = user.get("id")
    username = user.get("username")
    first_name = user.get("first_name")

    if user_id:
        add_user(user_id, username, first_name)

    return {"status": "ok"}
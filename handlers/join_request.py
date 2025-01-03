from aiogram import Router
from aiogram.types import ChatJoinRequest

router = Router()


@router.chat_join_request()
async def handle_join_request(chat_join_request: ChatJoinRequest):
    user = chat_join_request.from_user
    chat = chat_join_request.chat

    try:
        await chat_join_request.approve()
        print(f"User {user.id} joined chat {chat.id}")
    except Exception as e:
        print(e)

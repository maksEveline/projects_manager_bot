from aiogram import Router
from aiogram.types import ChatJoinRequest

from data.database import db
from utils.time_utils import format_timestamp, is_future_time

router = Router()


@router.chat_join_request()
async def handle_join_request(chat_join_request: ChatJoinRequest):
    user = chat_join_request.from_user
    chat_id = chat_join_request.chat.id
    try:
        project_id = await db.get_project_id_by_chat_id(chat_id)
        active_subs = await db.get_user_active_subscriptions(user.id, project_id)

        is_subscribed = False

        for sub in active_subs:
            formated_date = format_timestamp(float(sub["date"]))
            is_future = is_future_time(formated_date)
            if is_future:
                is_subscribed = True
                break

        if is_subscribed:
            try:
                await chat_join_request.approve()
                print(f"User {user.id} joined chat {chat_id}")
            except Exception as e:
                print(f"Error while approving join request: {e}")
            return
        else:
            print("User is not subscribed")
            await chat_join_request.decline()
            return
    except Exception as ex:
        print(f"Ошибка при принятии запроса на вступление в чат/канал: {ex}")
        return

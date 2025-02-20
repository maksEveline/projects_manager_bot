from datetime import datetime
from aiogram import F, Bot
from aiogram.types import CallbackQuery

from data.database import db
from utils.routers import create_router_with_user_middleware
from utils.time_utils import get_timestamp, format_timestamp


router = create_router_with_user_middleware()


def reverse_date(date_str: str) -> str:
    date_part, time_part = date_str.split(" ")
    reversed_date = ".".join(date_part.split("-")[::-1])
    return f"{reversed_date} {time_part}"


@router.callback_query(F.data.startswith("confirm_pay_request_"))
async def confirm_pay_request(callback: CallbackQuery, bot: Bot):
    request_id = callback.data.split("_")[-1]
    payment_request = await db.get_payment_request(int(request_id))

    user_id = payment_request["user_id"]
    rate_id = payment_request["rate_id"]
    rate_info = await db.get_rate(rate_id)
    project_id = rate_info["project_id"]
    project_info = await db.get_project(project_id)
    project_chats = await db.get_project_chats_and_channels(project_id)

    if rate_info["duration_type"] == "hours":
        sub_time = rate_info["duration"]
    elif rate_info["duration_type"] == "days":
        sub_time = rate_info["duration"] * 24

    sub_timestamp = get_timestamp(sub_time)
    formatted_time = format_timestamp(sub_timestamp)

    await db.add_active_subscriptions(
        user_id, rate_info["project_id"], rate_id, sub_timestamp, hourses=sub_time
    )

    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await db.add_user_purchase(user_id, rate_info["project_id"], rate_id, now_time)

    reversed_date = reverse_date(formatted_time)
    answ_text = (
        f"✅ Тариф успешно приобретен\nПодписка действует до: {reversed_date}\n\n"
    )

    await db.delete_alerts(int(user_id), int(project_id), int(rate_id))

    # пробуем разбанить пользователя в чатах и каналах если у него уже была подписка
    for chat in project_chats:
        answ_text += f"<b>{chat['name']}({chat['type']})</b> : {chat['link']}\n"

        try:
            await bot.unban_chat_member(chat["id"], user_id)
            print(f"Пользователь {user_id} разбанен в чате {chat['id']}")
        except Exception as e:
            ...

    # отправляем сообщение пользователю
    await bot.send_message(
        text=answ_text,
        chat_id=user_id,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

    user_info = await db.get_user(user_id)
    # отправляем сообщение владельцу проекта
    await bot.send_message(
        text=f"💰 Оплата за {project_info['name']} {rate_info['name']} подтверждена\n{user_info['first_name']} @{user_info['username']} id: <code>{user_id}</code>",
        chat_id=callback.message.chat.id,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
    await db.delete_payment_request(request_id)
    await bot.edit_message_reply_markup(
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=None,
    )


@router.callback_query(F.data.startswith("cancel_pay_request_"))
async def cancel_pay_request(callback: CallbackQuery, bot: Bot):
    request_id = callback.data.split("_")[-1]
    payment_request = await db.get_payment_request(int(request_id))
    user_id = payment_request["user_id"]
    user_info = await db.get_user(user_id)

    await db.delete_payment_request(request_id)
    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    await bot.send_message(
        text=f"❌ Ваш запрос на оплату (ID: {request_id}) отменен владельцем проекта",
        chat_id=user_id,
    )

    await bot.send_message(
        text=f"❌ Запрос на оплату (ID: {request_id}) отменен\n{user_info['first_name']} @{user_info['username']} id: <code>{user_id}</code>",
        chat_id=callback.message.chat.id,
    )

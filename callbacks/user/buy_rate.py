from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from data.database import db
from keyboards.user.user_inline import get_main_menu_user
from utils.json_utils import get_project_percentage
from utils.time_utils import format_hours, get_timestamp, format_timestamp
from config import DURATION_TYPES, FIXED_PERCENT

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


@router.callback_query(F.data.startswith("buy_rate_"))
async def buy_rate(callback: CallbackQuery, bot: Bot):
    rate_id = int(callback.data.split("_")[-1])
    rate = await db.get_rate(rate_id)
    if rate["duration_type"] == "hours":
        dur_type = format_hours(rate["duration"])
    else:
        dur_type = f"{rate['duration']} дней"
    project_chats = await db.get_project_chats_and_channels(rate["project_id"])

    answ_msg = (
        f"🤑 Вы хотите купить <b>{rate['name']}</b> - {dur_type}({rate['price']}$)\n\n"
    )
    answ_msg += "🦋 Вы получите доступ в следующих чатах и каналах:\n\n"

    for chat in project_chats:
        answ_msg += f"<b>{chat['name']}</b>({chat['type']})\n"

    kb = [
        [
            InlineKeyboardButton(
                text="✅Покупаю", callback_data=f"confirm_buy_rate_{rate_id}"
            )
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=answ_msg,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("confirm_buy_rate_"))
async def confirm_buy_rate(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    user_info = await db.get_user(user_id)
    rate_id = callback.data.split("confirm_buy_rate_")[-1]
    rate_info = await db.get_rate(rate_id)
    project_info = await db.get_project(rate_info["project_id"])
    project_chats = await db.get_project_chats_and_channels(rate_info["project_id"])

    if float(user_info["balance"]) < float(rate_info["price"]):
        kb = [
            [
                InlineKeyboardButton(
                    text="💰 Пополнить баланс", callback_data=f"add_balance"
                )
            ]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=kb)
        await bot.send_message(
            text="❌ Недостаточно средств",
            chat_id=callback.message.chat.id,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
        return

    if rate_info["duration_type"] == "hours":
        sub_time = rate_info["duration"]
    elif rate_info["duration_type"] == "days":
        sub_time = rate_info["duration"] * 24

    sub_timestamp = get_timestamp(sub_time)
    formatted_time = format_timestamp(sub_timestamp)

    await db.add_active_subscriptions(
        user_id, rate_info["project_id"], rate_id, sub_timestamp, hourses=sub_time
    )

    dirrty_price = rate_info["price"]
    clean_price = dirrty_price - (dirrty_price * get_project_percentage())

    if project_info["project_type"] == "percentage":
        await db.deduct_balance(
            user_id, dirrty_price
        )  # у пользователя снимаем всю сумму
        await db.update_user_balance(
            project_info["user_id"], clean_price
        )  # владельцу проекта добавляем сумму за вычетом процента
    else:
        await db.deduct_balance(user_id, rate_info["price"])
        await db.update_user_balance(project_info["user_id"], rate_info["price"])

    now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await db.add_user_purchase(user_id, rate_info["project_id"], rate_id, now_time)

    answ_text = (
        f"✅ Тариф успешно приобретен\nПодписка действует до: {formatted_time}\n\n"
    )

    # пробуем разбанить пользователя в чатах и каналах если у него уже была подписка
    for chat in project_chats:
        answ_text += f"<b>{chat['name']}({chat['type']})</b> : {chat['link']}\n"

        try:
            await bot.unban_chat_member(chat["id"], user_id)
            print(f"Пользователь {user_id} разбанен в чате {chat['id']}")
        except Exception as e:
            ...

    await bot.send_message(
        text=answ_text,
        chat_id=callback.message.chat.id,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

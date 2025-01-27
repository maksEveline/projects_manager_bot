from aiogram import F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from data.database import db
from keyboards.user.user_inline import get_main_menu_user
from config import DURATION_TYPES
from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


@router.message(F.text == "/start")
async def start_func(msg: Message, bot: Bot):
    if msg.chat.type != "private":
        return

    user_id = msg.from_user.id
    first_name = msg.from_user.first_name
    username = msg.from_user.username.lower()
    if username is None:
        username = "Unknown"

    await db.add_user_if_not_exists(user_id, first_name, username)
    await db.update_username(user_id, username)

    await msg.answer(
        text=f"👋 Привет, <b>{msg.from_user.full_name}</b>",
        parse_mode="html",
        reply_markup=await get_main_menu_user(),
    )

    await bot.delete_message(chat_id=user_id, message_id=msg.message_id)


@router.message(F.text.startswith("/start"))
async def splited_start(msg: Message, bot: Bot):
    if msg.chat.type != "private":
        return

    user_id = msg.from_user.id
    first_name = msg.from_user.first_name
    username = msg.from_user.username.lower()
    if username is None:
        username = "Unknown"

    await db.add_user_if_not_exists(user_id, first_name, username)
    await db.update_username(user_id, username)

    project_info = msg.text.split("/start ")[-1]
    project_id = int(project_info.split("_")[-1])

    project = await db.get_project(project_id)
    rates = await db.get_rates(project_id)

    if project["project_type"] == "fixed" and project["is_active"] == 0:
        await msg.answer(
            text="🚫 Проект не активен",
            reply_markup=await get_main_menu_user(),
        )
        return

    answ_msg = f"🤑 Вы хотите купить проект <b>{project['name']}</b>\n\n"
    kb = []

    for rate in rates:
        dur_type = DURATION_TYPES[rate["duration_type"]]
        answ_msg += (
            f"{rate['name']} - {rate['duration']} {dur_type}({rate['price']}$)\n"
        )
        kb.append(
            [
                InlineKeyboardButton(
                    text=f"{rate['name']} - {rate['duration']} {dur_type}({rate['price']}$)",
                    callback_data=f"buy_rate_{rate['rate_id']}",
                )
            ]
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await bot.send_message(
        chat_id=msg.from_user.id,
        text=answ_msg,
        parse_mode="html",
        reply_markup=keyboard,
    )

    await bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id)


@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery, bot: Bot):

    await bot.edit_message_text(
        text=f"👋 Привет, <b>{callback.from_user.full_name}</b>",
        parse_mode="html",
        reply_markup=await get_main_menu_user(),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
    )


@router.message(F.text == "/get_id")
async def get_id(msg: Message):
    chat_type = msg.chat.type
    if chat_type == "private":
        await msg.answer(
            text=f"🆔 Ваш ID: <code>{msg.from_user.id}</code>", parse_mode="html"
        )
    else:
        await msg.answer(
            text=(
                f"👤 Ваш ID: <code>{msg.from_user.id}</code>\n"
                f"💭 ID чата: <code>{msg.chat.id}</code>"
            ),
            parse_mode="html",
        )

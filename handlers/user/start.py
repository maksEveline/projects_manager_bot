from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    SwitchInlineQueryChosenChat,
)

from data.database import db
from keyboards.user.user_inline import get_main_menu_user

router = Router()


# @router.message(F.text == "/start")
# async def start_func(msg: Message, bot: Bot):
#     bot_username = (await bot.get_me()).username
#     url = f"https://t.me/{bot_username}?startgroup=start"
#     url_channel = f"https://t.me/{bot_username}?startchannel&admin=post_messages"
#     button = InlineKeyboardButton(text="Добавить бота в группу", url=url)
#     button_channel = InlineKeyboardButton(text="Добавить бота в канал", url=url_channel)
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[[button], [button_channel]])
#     await msg.answer(
#         "Нажмите кнопку ниже, чтобы добавить бота в группу:", reply_markup=keyboard
#     )


@router.message(F.text == "/start")
async def start_func(msg: Message, bot: Bot):
    user_id = msg.from_user.id
    first_name = msg.from_user.first_name
    username = msg.from_user.username
    if username is None:
        username = "Unknown"

    await db.add_user_if_not_exists(user_id, first_name, username)

    await msg.answer(
        text=f"👋 Привет, <b>{msg.from_user.full_name}</b>",
        parse_mode="html",
        reply_markup=await get_main_menu_user(),
    )

    await bot.delete_message(chat_id=user_id, message_id=msg.message_id)


@router.callback_query(F.data == "main_menu")
async def back_to_main_menu(callback: CallbackQuery, bot: Bot):
    await bot.edit_message_text(
        text=f"👋 Привет, <b>{callback.from_user.full_name}</b>",
        parse_mode="html",
        reply_markup=await get_main_menu_user(),
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
    )

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery

from data.database import db
from keyboards.user.user_inline import get_main_menu_user

router = Router()


@router.message(F.text == "/start")
async def start_func(msg: Message, bot: Bot):
    user_id = msg.from_user.id
    await db.add_user_if_not_exists(user_id)

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

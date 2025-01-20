from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
)

from aiogram.fsm.context import FSMContext

from data.database import db
from keyboards.user.user_inline import get_profile_menu

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


@router.callback_query(F.data == "profile")
async def open_profile(callback: CallbackQuery, bot: Bot, state: FSMContext):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    purchases_count = len(await db.get_user_purchases(user_id))

    msg_text = "<b>👤 Ваш профиль</b>\n\n"
    msg_text += f"🆔 Ваш айди: <code>{user['user_id']}</code>\n"
    msg_text += f"💰 Ваш баланс: <b>{user['balance']}$</b>\n"
    msg_text += f"🧑‍💻 Кол-во проектов: <b>{user['projects_count']}</b>\n"
    msg_text += f"🧑‍💻 Макс. кол-во фикс. проектов: <b>{user['max_projects']}</b>\n"
    msg_text += f"🛍️ Кол-во покупок: <b>{purchases_count}</b>\n"

    await bot.edit_message_text(
        text=msg_text,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=await get_profile_menu(),
        parse_mode="HTML",
    )

from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from utils.json_utils import get_project_percentage

router = Router()


@router.callback_query(F.data == "add_project")
async def add_project(callback: CallbackQuery, bot: Bot):
    kb = [
        [
            InlineKeyboardButton(
                text="Проект за фикс", callback_data="add_project_fixed"
            )
        ],
        [
            InlineKeyboardButton(
                text=f"Этот проект за {int(get_project_percentage() * 100)}% от дохода",
                callback_data="add_project_percent",
            )
        ],
        [InlineKeyboardButton(text="🔙 Главное меню", callback_data="main_menu")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await bot.edit_message_text(
        text="Выберите тип проекта",
        reply_markup=keyboard,
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
    )

from aiogram import F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from data.database import db
from keyboards.user.user_inline import get_main_menu_user
from config import DURATION_TYPES, ADMIN_IDS
from utils.routers import create_router_with_admin_middleware

router = create_router_with_admin_middleware()


@router.callback_query(F.data == "backups")
async def backups(callback: CallbackQuery, bot: Bot):
    kb = [
        [
            InlineKeyboardButton(
                text="Изменить канал", callback_data="change_backup_channel"
            ),
        ],
        [
            InlineKeyboardButton(text="Назад", callback_data="admin_menu"),
        ],
    ]

    await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    await callback.message.answer(
        "Бекапы", reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
    )

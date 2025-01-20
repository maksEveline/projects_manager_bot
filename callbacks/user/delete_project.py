from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from data.database import db
from keyboards.user.user_inline import get_back_to_main_menu

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


@router.callback_query(F.data.startswith("delete_project_"))
async def delete_project(callback: CallbackQuery, bot: Bot):
    project_id = callback.data.split("delete_project_")[-1]
    project = await db.get_project(project_id)

    kb = [
        [
            InlineKeyboardButton(
                text="🗑️ Удалить проект",
                callback_data=f"accept_delete_project_{project_id}",
            )
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_method")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await bot.edit_message_text(
        text=f"🗑️ Удалить проект {project['name']}?",
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("accept_delete_project_"))
async def accept_delete_project(callback: CallbackQuery, bot: Bot):
    project_id = callback.data.split("accept_delete_project_")[-1]
    is_deleted = await db.delete_project(project_id)
    if is_deleted:
        await bot.edit_message_text(
            text=f"🗑️ Проект <code>{project_id}</code> удален",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            parse_mode="HTML",
            reply_markup=await get_back_to_main_menu(),
        )
    else:
        await bot.edit_message_text(
            text="❌ Ошибка при удалении проекта",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=await get_back_to_main_menu(),
        )

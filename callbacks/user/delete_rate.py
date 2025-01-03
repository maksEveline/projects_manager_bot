from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext

from keyboards.user.user_inline import get_cancel_menu, get_back_to_project_menu
from data.database import db

router = Router()


@router.callback_query(F.data.startswith("delete_rate_"))
async def delete_rate(callback: CallbackQuery, bot: Bot):
    rate_id = callback.data.split("delete_rate_")[-1]

    rate = await db.get_rate(rate_id)
    project_id = rate["project_id"]
    project = await db.get_project(project_id)

    kb = [
        [
            InlineKeyboardButton(
                text="✅ Да", callback_data=f"confirm_delete_rate_{rate_id}"
            ),
            InlineKeyboardButton(text="❌ Нет", callback_data="cancel_method"),
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await bot.edit_message_text(
        text=f"Вы действительно хотите удалить тариф <b>{rate['name']}</b> из проекта <b>{project['name']}</b>?",
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("confirm_delete_rate_"))
async def confirm_delete_rate(callback: CallbackQuery, bot: Bot):
    rate_id = callback.data.split("confirm_delete_rate_")[-1]
    rate = await db.get_rate(rate_id)
    project_id = rate["project_id"]

    is_deleted = await db.delete_rate(rate_id)

    kb = [[InlineKeyboardButton(text="🔙 Назад", callback_data=f"rates_{project_id}")]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    if is_deleted:
        await bot.edit_message_text(
            text="✅ Тариф успешно удален",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=keyboard,
            parse_mode="HTML",
        )
    else:
        await bot.edit_message_text(
            text="❌ Ошибка при удалении тарифа",
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            reply_markup=await get_cancel_menu(),
            parse_mode="HTML",
        )

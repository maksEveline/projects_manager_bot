from aiogram import F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext

from data.database import db

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


@router.callback_query(F.data.startswith("settings_payment_"))
async def enable_payment_requisites(
    callback: CallbackQuery, bot: Bot, state: FSMContext
):
    project_id = callback.data.split("settings_payment_")[-1]
    project_payment_requisites = await db.get_payment_requisites(project_id)

    kb = []

    answ_text = ""

    if project_payment_requisites:
        answ_text = f"💸 Текущие реквизиты для альтернативной оплаты проекта:\n\n{project_payment_requisites}"
        kb.append(
            [
                InlineKeyboardButton(
                    text="🔄 Изменить реквизиты",
                    callback_data=f"change_payment_requisites_{project_id}",
                )
            ]
        )
    else:
        answ_text = "🦋 Выберите действие"
        kb.append(
            [
                InlineKeyboardButton(
                    text="➕ Добавить реквизиты",
                    callback_data=f"add_payment_requisites_{project_id}",
                )
            ]
        )

    kb.append(
        [
            InlineKeyboardButton(
                text="🔙 Назад",
                callback_data=f"project_{project_id}",
            )
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await bot.edit_message_text(
        text=answ_text,
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=keyboard,
    )

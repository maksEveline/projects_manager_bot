from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from aiogram.fsm.context import FSMContext

from data.database import db
from config import DURATION_TYPES
from utils.time_utils import format_hours

router = Router()


@router.callback_query(F.data.startswith("rates_"))
async def open_project_rates(callback: CallbackQuery, bot: Bot, state: FSMContext):
    project_id = callback.data.split("rates_")[-1]
    rates = await db.get_rates(project_id)

    kb = []

    for rate in rates:
        if rate["duration_type"] == "hours":
            dur_type = format_hours(rate["duration"])
        else:
            dur_type = f"{rate['duration']} дней"
        kb.append(
            [
                InlineKeyboardButton(
                    text=f"{rate['name']} - {dur_type}({rate['price']}$)",
                    callback_data=f"rate_settings_{rate['rate_id']}",
                )
            ]
        )

    kb.append(
        [
            InlineKeyboardButton(
                text="➕ Добавить тариф", callback_data=f"add_rate_{project_id}"
            )
        ]
    )
    kb.append(
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"project_{project_id}")]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    msg_text = ""

    if len(rates) == 0:
        msg_text = "<b>💰 Тарифы проекта:</b>\n\n<b>Нет тарифов</b>"
    else:
        msg_text = "<b>💰 Тарифы проекта:</b>"

    await bot.edit_message_text(
        text=msg_text,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=keyboard,
        parse_mode="HTML",
    )

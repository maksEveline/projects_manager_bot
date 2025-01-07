from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.user.user_inline import get_rate_settings_menu
from data.database import db

from config import DURATION_TYPES

router = Router()


@router.callback_query(F.data.startswith("rate_settings_"))
async def open_rate_settings(callback: CallbackQuery, bot: Bot, state: FSMContext):
    rate_id = callback.data.split("rate_settings_")[-1]
    rate = await db.get_rate(rate_id)

    dur_type = DURATION_TYPES[rate["duration_type"]]

    answer_text = f"💰 Цена: <code>{rate['price']}$</code>\n⏱️ Длительность: <code>{rate['duration']} {dur_type}</code>\n📝 Название: <code>{rate['name']}</code>"
    answer_text += "\n\n🦋 Выберите действие:"
    answer_keyboard = await get_rate_settings_menu(rate_id, rate["project_id"])

    await bot.edit_message_text(
        text=answer_text,
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=answer_keyboard,
        parse_mode="HTML",
    )

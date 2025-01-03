from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from data.database import db
from keyboards.user.user_inline import get_back_to_project_menu, get_cancel_menu

router = Router()


class ChangeDuration(StatesGroup):
    waiting_for_duration = State()


@router.callback_query(F.data.startswith("change_rate_duration_"))
async def change_duration(callback: CallbackQuery, bot: Bot, state: FSMContext):
    rate_id = callback.data.split("change_rate_duration_")[-1]
    await state.set_state(ChangeDuration.waiting_for_duration)
    await bot.edit_message_text(
        text="🚀 Введите новую длительность тарифа:",
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=await get_cancel_menu(),
    )

    await state.update_data({"rate_id": rate_id, "msg_id": callback.message.message_id})


@router.message(ChangeDuration.waiting_for_duration)
async def process_change_duration(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    rate_id = data["rate_id"]
    rate = await db.get_rate(rate_id)
    project_id = rate["project_id"]

    try:
        duration = int(message.text)
        if duration <= 0:
            raise ValueError

        await db.update_rate_duration(rate_id, duration)
        await bot.delete_message(message.chat.id, message.message_id)

        await bot.edit_message_text(
            text="✅ Длительность тарифа успешно изменена",
            chat_id=message.chat.id,
            message_id=data["msg_id"],
            reply_markup=await get_back_to_project_menu(project_id),
        )

        await state.clear()

    except ValueError:
        await bot.delete_message(message.chat.id, message.message_id)
        await bot.edit_message_text(
            text="❌ Пожалуйста, введите положительное число",
            chat_id=message.chat.id,
            message_id=data["msg_id"],
            reply_markup=await get_cancel_menu(),
        )

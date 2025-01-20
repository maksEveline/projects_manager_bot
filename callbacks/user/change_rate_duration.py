from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


from data.database import db
from keyboards.user.user_inline import get_back_to_project_menu, get_cancel_menu

from utils.routers import create_router_with_user_middleware

router = create_router_with_user_middleware()


class ChangeDuration(StatesGroup):
    waiting_for_duration = State()
    duration_type = State()


@router.callback_query(F.data.startswith("change_rate_duration_"))
async def change_duration(callback: CallbackQuery, bot: Bot, state: FSMContext):
    rate_id = callback.data.split("change_rate_duration_")[-1]

    kb = [
        [
            InlineKeyboardButton(text="Дни", callback_data=f"set_duration_days"),
            InlineKeyboardButton(text="Часы", callback_data=f"set_duration_hours"),
        ],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_method")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    await bot.edit_message_text(
        text="⏰ Выберите метод подписки",
        chat_id=callback.message.chat.id,
        message_id=callback.message.message_id,
        reply_markup=keyboard,
    )
    await state.set_state(ChangeDuration.duration_type)
    await state.update_data({"rate_id": rate_id, "msg_id": callback.message.message_id})


@router.callback_query(ChangeDuration.duration_type)
async def set_duration_type(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    rate_id = data["rate_id"]

    picked_dur_type = call.data.split("set_duration_")[-1]
    await state.update_data({"duration_type": picked_dur_type})

    await state.set_state(ChangeDuration.waiting_for_duration)
    await bot.edit_message_text(
        text="🚀 Введите новую длительность тарифа:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=await get_cancel_menu(),
    )


@router.message(ChangeDuration.waiting_for_duration)
async def process_change_duration(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    rate_id = data["rate_id"]
    rate = await db.get_rate(rate_id)
    project_id = rate["project_id"]
    duration_type = data["duration_type"]

    try:
        duration = int(message.text)
        if duration <= 0:
            raise ValueError

        await db.update_rate_duration(rate_id, duration, duration_type)
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
